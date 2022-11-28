
import re
from db_service import DbService
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from message_service import MessageService
import time


def processing_message(vks, ms, event, request):
    dbs = DbService()
    user_id = event.user_id
    client = dbs.get_client(user_id)

    if not client:
        user = vks.get_client(user_id)
        dbs.save_client(user)
        client = dbs.get_client(user_id)

    ms.client = client
    dbs.update(user_id, "status", ms.get_cur_status())
    print('request', request)
    print('ms.get_cur_status()',  ms.get_cur_status())
    print('client.candidate_sex', client.candidate_sex)
    print('client.candidate_age', client.candidate_age)
    print('client.candidate_city', client.candidate_city)
    print('ms.client.candidate_sex', ms.client.candidate_sex)
    print('ms.client.candidate_age', ms.client.candidate_age)
    print('ms.client.candidate_city', ms.client.candidate_city)
    print('ms.client.count', ms.client.clients_and_candidates)
    print('ms.all_req_params()', ms.all_req_params())

    # time.sleep(3)
    if client.status == 0:
        if not vks.check_token():
            ms.send(message=ms.token_expired())
        else:
            if ms.all_req_params():
                ms.send(message=ms.hello_message(), keyboard=ms.proceed_kb())
            else:
                ms.send(message=ms.hello_message(), keyboard=ms.start_kb())

    elif client.status == 1:
        if ms.start_check(request):
            ms.send(message=ms.choose_sex(), keyboard=ms.sex_kb())
        else:
            ms.send(message=ms.err_message(), keyboard=ms.start_kb())

    elif client.status == 2:
        if ms.check_sex(request):
            vks.sex = request
            dbs.update(user_id, "candidate_sex", request)
            ms.send(message=ms.choose_age(),
                    keyboard=ms.age_kb(), complete=True)
        else:
            ms.send(message=ms.err_sex(), keyboard=ms.sex_kb())

    elif client.status == 3:
        if ms.check_age(request):
            vks.age = request
            dbs.update(user_id, "candidate_age", request)
            ms.send(message=ms.choose_city(),
                    keyboard=ms.city_kb(), complete=True)
        else:
            ms.send(message=ms.err_age(), keyboard=ms.age_kb(), complete=True)

    elif client.status == 4:
        vks.city = request
        if vks.city:
            dbs.update(user_id, "candidate_city", request)
            processing_message(vks, ms, event, 'Поиск')
        else:
            ms.send(message=ms.err_city(),
                    keyboard=ms.city_kb(), complete=True)

    elif client.status == 5:
        if ms.check_show(request):
            user = vks.get_user()
            photos = vks.get_photos(user['id'])
            photos_att = ms.get_photos_att(photos)
            ms.send(message=ms.send_candidate(user), attachment=photos_att,
                    keyboard=ms.search_kb(save=True),  complete=True)
        elif ms.check_save(request):
            candidate = dbs.save_candidate(
                vks.user, ms.get_photos_att(vks.photos), user_id)
            ms.send(message='сохранено', keyboard=ms.search_kb())
        elif ms.check_favorite(request):
            candidates = dbs.get_candidates(client.user_id)
            if candidates:
                for candidate in candidates:
                    ms.send(message=ms.send_favorite(candidate),
                            attachment=candidate.photos, 
                            keyboard=ms.search_kb(delete=True, favorite=False))
            else:
                ms.send(message='Никого нет в избранном',
                        keyboard=ms.search_kb())
        elif ms.check_del(request):
            candidate = dbs.drop_candidate()
            ms.send(message=f'удален {candidate.first_name} {candidate.last_name}',
                    keyboard=ms.search_kb())
        elif re.match("пока", request, re.IGNORECASE):
            ms.send(user_id=user_id,
                    message=ms.bye_message())
            ms.greet = False
        else:
            ms.send(message=ms.err_message(),
                    keyboard=ms.search_kb(save=True))

    else:
        ms.send(user_id=event.user_id,
                message=ms.err_message())

    dbs.session.close()
