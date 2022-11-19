import vk_api


from models import create_tables, Client
from sqlalchemy.exc import NoResultFound
from sqlalchemy.inspection import inspect


class DbService:
    def __init__(self, session):
        self.session = session

    def is_client_exists(self, client_id):
        return self.session.query(Client.client_id).filter_by(client_id=client_id).first() is not None

    def save_client(self, client):
        data = {
            'client_id': client.get('id'),
            'first_name': client.get('first_name'),
            'last_name': client.get('last_name'),
            'nickname': client.get('nickname'),
            'city': client.get('city', {}).get('title'),
            'bdate': client.get('bdate'),
            'country': client.get('country', {}).get('title'),
            'sex': client.get('sex')
        }
        if not self.is_client_exists(data['client_id']):
            return Client(**data)
