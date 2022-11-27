
import re
from db_service import DbService


def processing_message(vks, ms, event, request, loop=False):
    dbs = DbService()
    user_id = event.user_id
    client = dbs.get_client(user_id)
    if not client:
        user = vks.get_client(user_id)
        client = dbs.save_client(user)
    ms.client = client
    if client.status == 0:
        if not vks.check_token():
            ms.send_message(message=ms.token_expired())
        else:
            if all((
                client.candidate_sex,
                client.candidate_age,
                client.candidate_city
            )):
                ms.send_message(message=ms.hello_message(),
                                keyboard=ms.get_keyboard(['Продолжить поиск']))
                dbs.update(user_id, "status", 5)
            else:
                ms.send_message(message=ms.hello_message())
                dbs.set_next_status(user_id, client.status)
                processing_message(vks, ms, event, request, loop=True)

    elif client.status == 1:
        ms.send_message(message=ms.choose_sex(),
                        keyboard=ms.get_keyboard(('М', 'Ж'), ['PRIMARY', 'NEGATIVE']))
        dbs.set_next_status(user_id, client.status)

    elif client.status == 2:
        if request in ('М', 'Ж') or loop:
            vks.sex = request
            dbs.update(user_id, "candidate_sex", request)
            dbs.set_next_status(user_id, client.status)
            ms.send_message(message=ms.choose_age(),
                            keyboard=ms.get_keyboard(vks.AGES_LIST), complete=True)
        else:
            dbs.set_prev_status(user_id, client.status)
            ms.send_message(message='неверный пол')
            processing_message(vks, ms, event, request, loop=True)

    elif client.status == 3:
        if request in vks.AGES_LIST or loop:
            vks.age = request
            dbs.update(user_id, "candidate_age", request)
            dbs.set_next_status(user_id, client.status)
            ms.send_message(user_id=user_id,
                            message=ms.choose_city(),
                            keyboard=ms.get_keyboard([vks.client_city]), complete=True)
        else:
            ms.send_message(message='неверный возраст')
            dbs.set_prev_status(user_id, client.status)
            processing_message(vks, ms, event, client.candidate_sex, loop=True)

    elif client.status == 4:
        vks.city = request
        if vks.city:
            print('город', vks.city)
            dbs.update(user_id, "candidate_city", request)
            dbs.set_next_status(user_id, client.status)
            processing_message(vks, ms, event, 'Следующий', loop=True)
        else:
            ms.send_message(user_id=user_id,
                            message='Нет такого города',
                            keyboard=ms.get_keyboard([vks.client_city]), complete=True)

    elif client.status == 5 and request in ('Следующий', 'Продолжить поиск'):
        user = vks.get_user()
        photos = vks.get_photos(user['id'])
        photos_att = ms.get_photos_att(photos)
        ms.send_message(user_id=user_id,
                        message=ms.send_candidate(user), attachment=photos_att,
                        keyboard=ms.get_keyboard(['Следующий', 'Сохранить']), complete=True)

    elif re.match("Сохранить", request, re.IGNORECASE) and client.status == 5:
        candidate = dbs.save_candidate(
            vks.user, ms.get_photos_att(vks.photos))
        ms.send_message(message='сохранено',
                        keyboard=ms.get_keyboard(['Следующий', 'Избранное']))

    elif re.match("Избранное", request, re.IGNORECASE):
        candidates = dbs.get_candidates()
        if candidates:
            for candidate in candidates:
                ms.send_message(message=ms.send_favorite(candidate),
                                attachment=candidate.photos, keyboard=ms.get_keyboard(['Следующий', 'Удалить']))
        else:
            ms.send_message(message='Никого нет в избранном',
                            keyboard=ms.get_keyboard(['Следующий']))

    elif re.match("Удалить", request, re.IGNORECASE):
        candidate = dbs.drop_candidate()
        ms.send_message(message=f'удален {candidate.first_name} {candidate.last_name}',
                        keyboard=ms.get_keyboard(['Следующий', 'Избранное']))

    elif re.match("пока", request, re.IGNORECASE):
        ms.send_message(user_id=user_id,
                        message=ms.bye_message())
        dbs.update(user_id, "status", 0)
    else:
        ms.send_message(user_id=event.user_id,
                        message=ms.err_message())

    dbs.session.close()
