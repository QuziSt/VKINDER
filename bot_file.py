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
from random import randrange
import requests


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


config = get_config()
vk = vk_api.VkApi(token=get_token(config))
longpoll = VkLongPoll(vk)
engine = sq.create_engine(get_DSN(config))
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()
ms = MessageService(VkKeyboard, VkKeyboardColor, vk)
vks = Vk_search(vk.get_api(), config['VK']['vk_app_token'])


for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if re.match('Привет', request, re.IGNORECASE):

                user = vks.get_client(event.user_id)
                ms.send_message(user_id=event.user_id,
                                message=ms.hello_message(user['first_name']))
                ms.send_message(user_id=event.user_id, message=ms.choose_sex(),
                                keyboard=ms.get_keyboard(('М', 'Ж'), ['PRIMARY', 'NEGATIVE']))
                client = DbService(session).save_client(user)
                session.add(client)
                session.commit()

            elif request in ('М', 'Ж') and ms.cur_req == 'sex':
                vks.sex = request
                ms.send_message(user_id=event.user_id, message=ms.choose_age(),
                                keyboard=ms.get_keyboard(vks.AGES_LIST))

            elif ms.cur_req == 'age' and request in vks.AGES_LIST:
                vks.age = request
                ms.send_message(user_id=event.user_id,
                                message=ms.choose_city(),
                                keyboard=ms.get_keyboard([vks.client_city]))

            elif re.match("Удалить", request, re.IGNORECASE):
                candidate = DbService(session).drop_candidate()
                session.commit()
                ms.send_message(user_id=event.user_id, message=f'удален {candidate.first_name} {candidate.last_name}',
                                keyboard=ms.get_keyboard(['Следующий', 'Избранное']))

            elif re.match("Избранное", request, re.IGNORECASE):
                candidates = DbService(session).get_candidates()
                if candidates:
                    for candidate in candidates:
                        ms.send_message(user_id=event.user_id, message=ms.send_favorite(candidate),
                                        attachment=candidate.photos, keyboard=ms.get_keyboard(['Следующий', 'Удалить']))
                else:
                    ms.send_message(user_id=event.user_id, message='Никого нет в избранном',
                                    keyboard=ms.get_keyboard(['Следующий']))

            elif re.match("Сохранить", request, re.IGNORECASE) and ms.cur_req == 'choice':
                candidate = DbService(session).save_candidate(
                    vks.user, ms.get_photos_att(vks.photos))
                print(candidate)
                session.add(candidate)
                session.commit()
                ms.send_message(user_id=event.user_id, message='сохранено',
                                keyboard=ms.get_keyboard(['Следующий', 'Избранное']))

            elif ms.cur_req == 'city' or ms.cur_req == 'choice':
                vks.city = request
                if vks.city:
                    user = vks.get_user()
                    photos = vks.get_photos(user['id'])
                    photos_att = ms.get_photos_att(photos)
                    ms.send_message(user_id=event.user_id,
                                    message=ms.send_candidate(user), attachment=photos_att,
                                    keyboard=ms.get_keyboard(['Следующий', 'Сохранить']))
                else:
                    ms.send_message(user_id=event.user_id,
                                    message='Нет такого города',
                                    keyboard=ms.get_keyboard([vks.client_city]))

            elif re.match("пока", request, re.IGNORECASE):
                ms.send_message(user_id=event.user_id,
                                message=ms.bye_message())
            else:
                ms.send_message(user_id=event.user_id,
                                message=ms.err_message(), keyboard=ms.buttons)

session.close()
