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

    def hello_message(self, name):
        return (f"Привет, {name}.\n"
                f"Давай найдем тебе вторую половинку.\n")

    def choose_sex(self):
        self.cur_req = 'sex'
        return 'Укажи пол своего избранника(цы)'

    def choose_age(self):
        self.cur_req = 'age'
        return 'Выбери возраст для поиска'

    def choose_city(self):
        self.cur_req = 'city'
        return 'Напиши город в котором искать'

    def bye_message(self):
        self.cur_req = 'hey'
        return "До встречи!"

    def err_message(self):
        return 'Не поняла'

    def send_message(self, keyboard=None, **kwargs):
        body = {**kwargs, 'random_id': randrange(10 ** 7)}
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
        message =  (f"{user['first_name']} {user['last_name']}\n"
                    f"https://vk.com/{user['domain']}\n")

        return message

    def send_favorite(self, user):
        self.cur_req = 'choice'
        message =  (f"{user.first_name} {user.last_name}\n"
                    f"https://vk.com/{user.domain}\n")

        return message