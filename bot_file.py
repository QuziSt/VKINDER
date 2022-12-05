from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from message_service import MessageService


def processing_message(vk, event, engine):
    ms = MessageService(VkKeyboard, VkKeyboardColor, vk, event, engine)
    ms.handle_event()
