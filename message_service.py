from random import randrange
from itertools import zip_longest
from db_service import DbService


class MessageService:

    def __init__(self, keyboard, vl_color, vk):
        self.vk_keyboard = keyboard
        self.vk_color = vl_color
        self.vk = vk
        self._cur_req = {
            'hey': True,
            'sex': False,
            'age': False,
            'city': False,
            'bye': False,
            'choice': False
        }
        self.buttons = None
        self.client = None
        self.greet = False
        self.statuses = {
            0: self.greet,
            1: self.client.candidate_sex,
            2: self.client.candidate_age,
            3: self.client.candidate_city,
            4: False,
        }

    @property
    def cur_req(self):
        for k, v in self._cur_req.items():
            if v:
                return k

    @cur_req.setter
    def cur_req(self, req):
        for k in self._cur_req:
            if k == req:
                self._cur_req[k] = True
            else:
                self._cur_req[k] = False

    def _is_any_search_params(self):
        return any((self.client.candidate_sex,
                self.client.candidate_age,
                self.client.candidate_city))

    def _complete_message(self, message):
        if self._is_any_search_params():
            message += "\n(Текущие параметры поиска:"
        if self.client.candidate_sex:
            message += f"\nПол - {self.client.candidate_sex}"
        if self.client.candidate_age:
            message += f"\nВозраст - {self.client.candidate_age}"
        if self.client.candidate_city:
            message += f"\nГород - {self.client.candidate_city}"
        if self._is_any_search_params():
            message += ')\n'
        return message

    def hello_message(self):
        message = f"Привет, {self.client.first_name}.\n"
        message = self._complete_message(message)
        message += f"Давай найдем тебе вторую половинку.\n"
        self.greet = True
        return message

    def token_expired(self):
        return (f"Привет, {self.client.first_name}.\n"
                f"Ваш токен не действителен!\n")

    def choose_sex(self):
        self.cur_req = 'sex'
        return 'Укажи пол своего избранника(цы)\n'

    def choose_age(self):
        self.cur_req = 'age'
        return 'Выбери возраст для поиска\n'

    def choose_city(self):
        self.cur_req = 'city'
        return 'Напиши город в котором искать\n'

    def bye_message(self):
        self.cur_req = 'hey'
        return "До встречи!"

    def err_message(self):
        return 'Не поняла'

    def send_message(self, message, keyboard=None, complete=False, **kwargs):
        if complete:
            message = self._complete_message(message)
        body = {
            **kwargs,
            'message': message,
            'random_id': randrange(10 ** 7),
            'user_id': self.client.user_id
        }
        if keyboard:
            body['keyboard'] = keyboard.get_keyboard()
        self.vk.method('messages.send', body)

    def get_keyboard(self, texts, colors_types=[]):
        self.buttons = self.vk_keyboard(one_time=True)
        for text, color_type in zip_longest(texts, colors_types, fillvalue='PRIMARY'):
            color = {
                'PRIMARY': self.vk_color.PRIMARY,
                'NEGATIVE': self.vk_color.NEGATIVE
            }[color_type]
            self.buttons.add_button(text, color=color)
        
        return self.buttons

    def get_photos_att(self, photos):
        return ','.join(f"photo{photo['owner_id']}_{photo['id']}" for photo in photos)

    def send_candidate(self, user):
        self.cur_req = 'choice'
        message = (f"{user['first_name']} {user['last_name']}\n"
                   f"https://vk.com/{user['domain']}\n")

        return message

    def send_favorite(self, user):
        self.cur_req = 'choice'
        message = (f"{user.first_name} {user.last_name}\n"
                   f"https://vk.com/{user.domain}\n")

        return message

    def get_cur_status(self):
        for k, v in self.statuses:
            if not v:
                return k
