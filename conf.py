import configparser


def get_config():
    config = configparser.ConfigParser()
    config.read('token.ini')
    return config

def get_token(config):
    return config['VK']['vk_group_token']