
import vk_api
import threading
from vk_api.longpoll import VkEventType
from bot_file import processing_message
import sqlalchemy as sq

from vk_api.longpoll import VkLongPoll
from conf import get_token, get_config
from db_service import get_DSN
from models import create_tables


config = get_config()
vk = vk_api.VkApi(token=get_token(config))
longpoll = VkLongPoll(vk)

engine = sq.create_engine(get_DSN(config))
create_tables(engine)

if __name__ == '__main__':
    for event in longpoll.listen():

        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                threading.Thread(
                    target=processing_message, args=(vk, event, engine)
                ).start()
