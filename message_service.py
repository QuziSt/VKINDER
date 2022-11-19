from random import randrange
from itertools import zip_longest


class MessageService:

    def __init__(self, keyboard, vl_color, vk):
        self.vk_keyboard = keyboard
        self.vk_color = vl_color
        self.vk = vk

    def hello_message(self, name):
        return (f"Привет, {name}.\n"
                f"Давай найдем тебе вторую половинку.\n"
                )

    def choose_sex(self):
        return 'Укажи пол своего избранника(цы)'

    def choose_age(self):
        return 'Выбери возраст для поиска'

    def choose_city(self):
        return 'Напиши город в котором искать'

    def bye_message(self):
        return "До встречи!"

    def err_message(self):
        return 'Не поняла'

    def send_message(self, keyboard=None, **kwargs):
        body = {**kwargs, 'random_id': randrange(10 ** 7)}
        if keyboard:
            body['keyboard'] = keyboard.get_keyboard()
        self.vk.method('messages.send', body)

    def get_keyboard(self, texts, colors_types=[]):
        vk_keyboard = self.vk_keyboard(one_time=True)
        for text, color_type in zip_longest(texts, colors_types, fillvalue='PRIMARY'):
            color = {
                'PRIMARY': self.vk_color.PRIMARY,
                'NEGATIVE': self.vk_color.NEGATIVE
            }[color_type]
            vk_keyboard.add_button(text, color=color)
        return vk_keyboard
