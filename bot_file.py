import configparser
import vk_api
import re
import sqlalchemy as sq

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from models import create_tables
from sqlalchemy.orm import sessionmaker
from db_service import DbService
from message_service import MessageService
from vk_search import Vk_search


def get_config():
    config = configparser.ConfigParser()
    config.read('token.ini')
    return config


def get_token(config):
    return config['VK']['vk_group_token']


def get_DSN(config):
    PG_USER = config['PG']['PG_USER']
    PG_PASSWORD = config['PG']['PG_PASSWORD']
    SERVER = config['PG']['SERVER']
    PORT = config['PG']['PORT']
    DB_NAME = config['PG']['DB_NAME']
    return f'postgresql://{PG_USER}:{PG_PASSWORD}@{SERVER}:{PORT}/{DB_NAME}'


SEX_FLAG, AGE_FLAG, CITY_FLAG = False, False, False
AGES_LIST = ['18-25', '25-35', '35-40', '40-50']

config = get_config()
vk = vk_api.VkApi(token=get_token(config))
longpoll = VkLongPoll(vk)
engine = sq.create_engine(get_DSN(config))
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()
ms = MessageService(VkKeyboard, VkKeyboardColor, vk)
vk_search = Vk_search(vk.get_api(), config['VK']['vk_app_token'])


for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if re.match('привет', request, re.IGNORECASE):
                user = vk_search.get_user(event.user_id)[0]
                ms.send_message(user_id=event.user_id,
                                message=ms.hello_message(user['first_name']))
                ms.send_message(user_id=event.user_id, message=ms.choose_sex(),
                                keyboard=ms.get_keyboard(('М', 'Ж'), ['PRIMARY', 'NEGATIVE']))
                SEX_FLAG = True
                client = DbService(session).save_client(user)
                session.add(client)
                session.commit()

            elif request in ('М', 'Ж') and SEX_FLAG:
                vk_search.search_params['sex'] = 'male' if request == 'М' else 'female'
                SEX_FLAG, AGE_FLAG = False, True
                ms.send_message(user_id=event.user_id, message=ms.choose_age(),
                                keyboard=ms.get_keyboard(AGES_LIST))

            elif request in AGES_LIST and AGE_FLAG:
                vk_search.search_params['age'] = str(request)
                AGE_FLAG, CITY_FLAG = False, True
                ms.send_message(user_id=event.user_id,
                                message=ms.choose_city())

            elif CITY_FLAG:
                vk_search.search_params['city'] = str(request)
                CITY_FLAG == False
                ms.send_message(user_id=event.user_id,
                                message=str(vk_search.search_by_params()['items'][0]))

            elif re.match("пока", request, re.IGNORECASE):
                ms.send_message(user_id=event.user_id,
                                message=ms.bye_message())
            else:
                ms.send_message(user_id=event.user_id,
                                message=ms.err_message())

session.close()
