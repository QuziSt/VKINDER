from random import randrange
import configparser
import vk_api
import requests
import re
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def get_token():
    config = configparser.ConfigParser()
    config.read('token.ini')
    token = config['VK']['vk_group_token']
    return token


vk = vk_api.VkApi(token=get_token())
longpoll = VkLongPoll(vk)



def get_all_fields():
    all_fields = 'bdate,activities,about,blacklisted,blacklisted_by_me,books,can_be_invited_group,can_post,' \
                 'can_see_all_posts,can_see_audio,can_send_friend_request,can_write_private_message,career,connections,' \
                 'contacts,city,country,crop_photo,domain,education,exports,followers_count,friend_status,has_photo,' \
                 'has_mobile,home_town,photo_100,photo_200,photo_200_orig,photo_400_orig,photo_50,sex,site,schools,' \
                 'screen_name,status,verified,games,interests,is_favorite,is_friend,is_hidden_from_feed,last_seen,' \
                 'maiden_name,military,movies,music,nickname,occupation,online,personal,photo_id,photo_max,' \
                 'photo_max_orig,quotes,relation,relatives,timezone,tv,universities'
    return all_fields

def show_button(user_id, message, keyboard):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),
                                'keyboard': keyboard.get_keyboard()})

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7)})


def sex_check():
    vk_keyboard = VkKeyboard(one_time=True)
    vk_color = VkKeyboardColor
    vk_keyboard.add_button('М', color=vk_color.PRIMARY)
    vk_keyboard.add_button('Ж', color=vk_color.NEGATIVE)
    return vk_keyboard

def age_check():
    vk_keyboard = VkKeyboard(one_time=True)
    vk_color = VkKeyboardColor
    vk_keyboard.add_button('18-25', color=vk_color.PRIMARY)
    vk_keyboard.add_button('25-35', color=vk_color.PRIMARY)
    vk_keyboard.add_button('35-40', color=vk_color.PRIMARY)
    vk_keyboard.add_button('40-50', color=vk_color.PRIMARY)
    return vk_keyboard
def get_user_data(user_id):

    api = vk.get_api()
    return api.users.get(user_ids=str(user_id), fields=get_all_fields())


SEX_FLAG = False
AGE_FLAG = False
CITY_FLAG = False
AGES_LIST = ['18-25', '25-35', '35-40', '40-50']
for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if re.match('привет', request, re.IGNORECASE):
                search_params = []
                write_msg(event.user_id, f"Привет, {get_user_data(event.user_id)[0]['first_name']}.\n"
                                         f"Давай найдем тебе вторую половинку.\n"
                                         f"Укажи пол своего избранника(цы) - в ответ напиши М или Ж")

                show_button(event.user_id, 'Укажи пол своего избранника(цы)', sex_check())
                SEX_FLAG = True

            elif request == 'М' or request == 'Ж' and SEX_FLAG is True:
                search_params += [request]
                SEX_FLAG = False
                AGE_FLAG = True
                show_button(event.user_id, 'Выбери возраст для поиска', age_check())
            elif all([request in AGES_LIST, AGE_FLAG is True]):
                search_params += [request]
                AGE_FLAG = False
                CITY_FLAG = True
                write_msg(event.user_id, 'Напиши город в котором искать')
            elif all([CITY_FLAG is True]):
                search_params += [request]
                CITY_FLAG == False
            elif re.match("пока", request, re.IGNORECASE):
                write_msg(event.user_id, "До встречи!")
            else:
                write_msg(event.user_id, 'Не поняла')