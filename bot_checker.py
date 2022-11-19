from random import randrange

import vk_api
import os
import dotenv
from vk_api.longpoll import VkLongPoll, VkEventType

dotenv.load_dotenv()
token = os.getenv('BOT_TOKEN')


vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})



b = {
    "type": "message_new",
    "object": {
        "id": 41,
        "date": 1526898082,
        "out": 0,
        "user_id": 163176673,
        "read_state": 0,
        "title": "",
        "body": "Blue",
        "payload": "{\"button\":\"4\"}"
    },
    "group_id": 1
}
vk.method('messages.send', {'message': b,  'random_id': randrange(10 ** 7),})

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        print('event', event)
        print('dir(event)', dir(event))
        print('event.user_id', event.user_id)

        if event.to_me:
            request = event.text
            print('request', request)

            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}")
                vk = vk_api.VkApi(token=token)
                
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")