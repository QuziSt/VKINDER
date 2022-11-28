from random import randrange
from itertools import zip_longest
from db_service import DbService
import re


class MessageService:

    AGES_LIST = ['18-25', '25-35', '35-40', '40-50']

    def __init__(self, keyboard, vl_color, vk):
        self.vk_keyboard = keyboard
        self.vk_color = vl_color
        self.vk = vk
        self.buttons = None
        self.client = None
        self.greet = False
        self.start_search = False
        self.age = False
        self.city = False

    def _is_any_search_params(self):
        return any((self.client.candidate_sex,
                    self.client.candidate_age,
                    self.client.candidate_city))

    def all_req_params(self):
        return all((
            self.client.candidate_sex,
            self.client.candidate_age,
            self.client.candidate_city
        ))

    def token_expired(self):
        return (f"Привет, {self.client.first_name}.\n"
                f"Ваш токен не действителен!\n")

    def _add_search_data(self, message):
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
        message = self._add_search_data(message)
        message += f"Давай найдем тебе вторую половинку.\n"
        self.greet = True
        return message

    def start_check(self, message):
        return re.match("Начать поиск", message, re.IGNORECASE)

    def choose_sex(self):
        self.start_search = True
        return 'Укажи пол своего избранника(цы)\n'

    def err_sex(self):
        return 'Пол указан не правильно!'

    def check_sex(self, message):
        return message in ('М', 'Ж')

    def choose_age(self):
        return 'Выбери возраст для поиска\n'

    def err_age(self):
        return 'Возраст указан не правильно!'

    def check_age(self, message):
        return message in self.AGES_LIST

    def choose_city(self):
        return 'Напиши город в котором искать\n'

    def err_city(self):
        return 'Город указан не правильно!'

    def check_show(self, message):
        return message in ('Поиск', 'Продолжить поиск')

    def check_save(self, message):
        return re.match("Сохранить", message, re.IGNORECASE)    

    def check_favorite(self, message):
        return re.match("Избранное", message, re.IGNORECASE)    

    def check_del(self, message):
        return re.match("Удалить", message, re.IGNORECASE)

    def bye_message(self):
        return "До встречи!"

    def err_message(self):
        return 'Не поняла'

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

    def get_keyboard(self, texts, colors_types=[], save=False, favorite=True, delete=False):
        self.buttons = self.vk_keyboard(one_time=True)
        for text, color_type in zip_longest(texts, colors_types, fillvalue='PRIMARY'):
            color = {
                'PRIMARY': self.vk_color.PRIMARY,
                'NEGATIVE': self.vk_color.NEGATIVE
            }[color_type]
            self.buttons.add_button(text, color=color)
        
        if self.client.clients_and_candidates and favorite:
           self.buttons.add_button('Избранное', color=self.vk_color.PRIMARY)     

        if save:
           self.buttons.add_button('Сохранить', color=self.vk_color.PRIMARY)

        if delete:
            self.buttons.add_button('Удалить', color=self.vk_color.PRIMARY)

        return self.buttons

    def get_photos_att(self, photos):
        return ','.join(f"photo{photo['owner_id']}_{photo['id']}" for photo in photos)

    def send_candidate(self, user):
        message = (f"{user['first_name']} {user['last_name']}\n"
                   f"https://vk.com/{user['domain']}\n")

        return message

    def send_favorite(self, user):
        message = (f"{user.first_name} {user.last_name}\n"
                   f"https://vk.com/{user.domain}\n")

        return message

    def get_statuses(self):
        return {
            0: not self.greet,
            1: not self.start_search,
            2: not self.client.candidate_sex,
            3: not self.client.candidate_age,
            4: not self.client.candidate_city,
            5: self.all_req_params(),
        }

    def get_cur_status(self):
        statuses = self.get_statuses()
        for k, v in statuses.items():
            if v:
                return k

    def proceed_kb(self):
        return self.get_keyboard(['Продолжить поиск'])

    def start_kb(self):
        return self.get_keyboard(['Начать поиск'])

    def sex_kb(self):
        return self.get_keyboard(('М', 'Ж'), ['PRIMARY', 'NEGATIVE'])

    def age_kb(self):
        return self.get_keyboard(self.AGES_LIST)

    def city_kb(self):
        return self.get_keyboard([self.client.city])

    def search_kb(self, save=False, delete=False, favorite=True):
        return self.get_keyboard(['Поиск'], save=save, delete=delete, favorite=favorite)