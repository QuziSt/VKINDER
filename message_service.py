from random import randrange
from itertools import zip_longest
from db_service import DbService
from vk_search import Vk_search
import re
from conf import get_config
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json


class MessageService:

    def __init__(self, keyboard, vl_color, vk, event, engine):
        self.vk_keyboard = keyboard
        self.vk_color = vl_color
        self.vk = vk
        self.vks = Vk_search(vk.get_api(), get_config()['VK']['vk_app_token'])
        self.buttons = None
        self.client = None
        self.event = event
        self.user_id = event.user_id
        self.message = event.text
        self.engine = engine
        self.payload = {}

    def get_payload(self):
        payload = getattr(self.event, 'payload', None)
        return json.loads(payload) if payload else None

    def get_sex_param(self):
        if not self.client.candidate_sex:
            sex = 'Ж' if self.client.sex == 2 else 'М'
            self.dbs.update("clients", self.client.user_id,
                            "candidate_sex", sex)
            return sex
        return self.client.candidate_sex

    def get_city_param(self):
        if not self.client.candidate_city_id:
            city = self.client.city if self.client.city else 'Москва'
            self.dbs.update("clients", self.client.user_id,
                            "candidate_city_id", city)
            return city
        return self.client.candidate_city_id

    def get_age_from_bdate(self, bdate):
        return datetime.now().year - datetime.strptime(bdate, "%d.%m.%Y").year

    def get_age_param(self):
        if not self.client.candidate_age_from:
            if self.client.bdate:
                age_from = self.get_age_from_bdate(self.client.bdate) - 5
            else:
                age_from = 18
            self.dbs.update("clients", self.client.user_id,
                            "candidate_age_from", age_from)
            return age_from
        return self.client.candidate_age_from

    def get_age_to(self):
        if not self.client.candidate_age_to:
            if self.client.bdate:
                age_to = self.get_age_from_bdate(self.client.bdate) + 5
            else:
                age_to = 45
            self.dbs.update("clients", self.client.user_id,
                            "candidate_age_to", age_to)
            return age_to
        return self.client.candidate_age_to

    def get_search_params(self):
        params = {
            'Пол': (self.get_sex_param(), self.sex_kb, self.sex_validator()),
            'Город': (self.get_city_param(), self.city_kb, self.city_validator()),
            'Возраст от': (self.get_age_param(), self.age_kb_from, self.age_validator_from()),
            'Возраст до': (self.get_age_to(), self.age_kb_to, self.age_validator_to()),
        }
        return params

    def sex_validator(self):
        pass

    def city_validator(self):
        pass

    def age_validator_from(self):
        pass

    def age_validator_to(self):
        pass

    def token_expired(self):
        return (f"Привет, {self.client.first_name}.\n"
                f"Ваш токен не действителен!\n")

    def _add_search_data(self, message):
        message += "\nПараметры поиска:"
        params = self.get_search_params()
        for k, v in params.items():
            if v:
                message += f"\n{k} - {v[0]}"
        return message

    def hello_message(self):
        message = f"Привет, {self.client.first_name}.\n"
        message += f"Давай найдем тебе вторую половинку.\n"
        message = self._add_search_data(message)
        return message

    def err_message(self):
        return 'Не поняла'

    def get_photos_att(self, photos):
        return ','.join(f"photo{photo['owner_id']}_{photo['id']}" for photo in photos)

    def send_candidate(self, user):
        message = (f"{user.first_name} {user.last_name}\n"
                   f"https://vk.com/{user.domain}\n")
        return message

    def send_saved(self, candidate):
        return (f"Пользователь {candidate.first_name} {candidate.last_name} сохранен\n")

    def err_saved(self):
        return (f"Последний просмотренный пользователь уже был сохранен.\n")

    def send_favorite(self, user):
        message = (f"{user.first_name} {user.last_name}\n"
                   f"https://vk.com/{user.domain}\n")

        return message

    def err_favorites(self):
        return "В избранном пока никого нет."

    def send_del(self, candidate):
        message = (f"Пользватель: {candidate.first_name} {candidate.last_name}\n"
                   f"удален\n")
        return message

    def err_del(self):
        return "В избранном пусто"

    def send_change(self):
        return "Выберите параметр для изменения."

    def change_param(self):
        return f"Укажите {self.message.lower()}"

    def send_changed(self):
        return f"Параметр {self.client.changing_param} изменен"

    def sex_kb(self):
        return self.get_keyboard(
            ('М', 'Ж'), ['PRIMARY', 'NEGATIVE'],
            show_change_b=False, show_fav_b=False
        )

    def age_kb_from(self):
        age_list = [i for i in range(18, self.client.candidate_age_to, 4)][:10]
        return self.get_keyboard(
            age_list,
            show_change_b=False, show_fav_b=False
        )

    def age_kb_to(self):
        age_list = [i for i in range(self.client.candidate_age_from, 60, 4)][:10]
        return self.get_keyboard(
            age_list,
            show_change_b=False, show_fav_b=False
        )

    def city_kb(self):
        return self.get_keyboard(
            [
                "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург",
                "Нижний Новгород", "Казань", "Челябинск", "Омск"
            ],
            show_change_b=False, show_fav_b=False
        )

    def search_kb(self, **kwargs):
        return self.get_keyboard(['Поиск'], **kwargs)

    def params_kb(self):
        buttons = []
        for param in self.get_search_params():
            buttons.append(param)
        return self.get_keyboard(buttons, show_change_b=False, show_fav_b=False, payload={'params_change': self.message})

    def send(self, message, keyboard=None, complete=False, **kwargs):
        if complete:
            message = self._add_search_data(message)
        body = {
            **kwargs,
            'message': message,
            'random_id': randrange(10 ** 7),
            'user_id': self.client.user_id
        }
        if keyboard:
            body['keyboard'] = keyboard.get_keyboard()
        self.vk.method('messages.send', body)

    def handle_event(self):
        Session = sessionmaker(bind=self.engine)
        with Session() as session:

            self.dbs = DbService(session)
            client = self.dbs.get_client(self.user_id)

            if not client:
                user = self.vks.get_client(self.user_id)
                self.dbs.save_client(user)
                client = self.dbs.get_client(self.user_id)

            self.client = client

            print('message', self.message)

            self.payload = self.get_payload()
            print('self.payload', self.payload)
            print('client.candidate_sex', client.candidate_sex)
            print('client.candidate_age_from', client.candidate_age_from)
            print('client.candidate_age_to', client.candidate_age_to)
            print('client.candidate_city_id', client.candidate_city_id)
            self.send_answer()

    def answ_greeting(self):
        if not self.vks.check_token():
            self.send(message=self.token_expired())
        else:
            self.dbs.update("clients", self.client.user_id, "greet", True)
            self.send(message=self.hello_message(), keyboard=self.search_kb())

    def answ_err(self):
        self.send(message=self.err_message(), keyboard=self.search_kb())

    def answ_search(self):
        candidate = self.dbs.pop_candidate(self.client.user_id)
        print('answ_search candidate', candidate)
        if not candidate:
            self.dbs.update("clients", self.client.user_id,
                            "offset", self.client.offset + 10)
            candidates = self.vks.get_users(
                self.get_search_params(), self.client.offset)
            self.dbs.save_candidates(candidates, self.client.user_id)
            candidate = self.dbs.pop_candidate(self.client.user_id)

        self.dbs.update("clients", self.client.user_id,
                        "candidate_id", candidate.user_id)
        photos = self.vks.get_photos(candidate.user_id)
        photos_att = self.get_photos_att(photos)
        self.send(message=self.send_candidate(candidate), attachment=photos_att,
                  keyboard=self.search_kb(save=True),  complete=True)

    def answ_save(self):
        candidate = self.dbs.save_favorite(
            self.client.user_id, self.client.candidate_id)
        if candidate:
            self.send(message=self.send_saved(
                candidate), keyboard=self.search_kb())
        else:
            self.send(message=self.err_saved(), keyboard=self.search_kb())

    def answ_favorites(self):
        candidates = self.dbs.get_favorites(self.client.user_id)
        if candidates:
            for candidate in candidates:
                photos = self.vks.get_photos(candidate.user_id)
                photos_att = self.get_photos_att(photos)
                self.send(message=self.send_favorite(candidate),
                          attachment=photos_att,
                          keyboard=self.search_kb(delete=True, show_fav_b=False))
        else:
            self.send(message=self.err_favorites(),
                      keyboard=self.search_kb(delete=True, show_fav_b=False))

    def answ_del(self):
        candidate = self.dbs.drop_candidate(self.client.user_id)
        if candidate:
            self.send(message=self.send_del(candidate),
                      keyboard=self.search_kb())
        else:
            self.send(message=self.err_del(), keyboard=self.search_kb())

    def answ_change(self):
        self.send(message=self.send_change(), keyboard=self.params_kb())

    def answ_param_change(self):
        params = self.get_search_params()
        if self.message in self.get_search_params():
            self.dbs.update("clients", self.client.user_id,
                            "changing_param", self.message)
            self.send(message=self.change_param(),
                      keyboard=params[self.message][1]())
        else:
            self.answ_err()

    def answ_param_changed(self):
        param = self.vks.conver_param(self.client.changing_param)[0]
        self.dbs.update("clients", self.client.user_id,
                        f"candidate_{param}", self.message)
        self.dbs.update("clients", self.client.user_id, f"changing_param", "")
        self.dbs.drop_candidates(self.client.user_id)
        self.send(message=self.send_changed(), keyboard=self.search_kb())

    def get_keyboard(
        self,
        texts,
        payload={},
        colors_types=[],
        show_fav_b=True,
        show_change_b=True,
        **kwargs
    ):
        self.buttons = self.vk_keyboard(one_time=True)
        for i, val in enumerate(zip_longest(texts, colors_types, fillvalue='PRIMARY')):
            text, color_type = val
            color = {
                'PRIMARY': self.vk_color.PRIMARY,
                'NEGATIVE': self.vk_color.NEGATIVE
            }[color_type]
            if i % 2 == 0 and i > 0:
                self.buttons.add_line()
            self.buttons.add_button(text, color=color, payload=payload)

        if show_fav_b and self.client.greet:
            self.buttons.add_button('Избранное', color=color, payload=payload)

        if kwargs.get('save'):
            self.buttons.add_button('Сохранить', color=color, payload=payload)

        if kwargs.get('delete'):
            self.buttons.add_button('Удалить', color=color, payload=payload)

        if show_change_b:
            self.buttons.add_line()
            self.buttons.add_button(
                'Изменить параметры поиска', color=color, payload=payload)

        return self.buttons

    def send_answer(self):
        if not self.client.greet:
            return self.answ_greeting()

        if self.client.changing_param:
            return self.answ_param_changed()

        if self.payload:
            if self.payload.get('params_change'):
                return self.answ_param_change()

        if re.match("Поиск", self.message, re.IGNORECASE):
            return self.answ_search()
        if re.match("Сохранить", self.message, re.IGNORECASE):
            return self.answ_save()
        if re.match("Избранное", self.message, re.IGNORECASE):
            return self.answ_favorites()
        if re.match("Удалить", self.message, re.IGNORECASE):
            return self.answ_del()
        if re.match("Изменить параметры поиска", self.message, re.IGNORECASE):
            return self.answ_change()
        return self.answ_err()
