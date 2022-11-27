import vk_api


from models import create_tables, Clients, Candidates
from sqlalchemy.exc import NoResultFound
from sqlalchemy.inspection import inspect
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker

from conf import get_config

def get_DSN(config):
    PG_USER = config['PG']['PG_USER']
    PG_PASSWORD = config['PG']['PG_PASSWORD']
    SERVER = config['PG']['SERVER']
    PORT = config['PG']['PORT']
    DB_NAME = config['PG']['DB_NAME']
    return f'postgresql://{PG_USER}:{PG_PASSWORD}@{SERVER}:{PORT}/{DB_NAME}'


class DbService:

    def __init__(self):
        self.session = self.get_session()

    def get_session(self):
        engine = sq.create_engine(get_DSN(get_config()))
        Session = sessionmaker(bind=engine)
        return Session()

    def is_user_exists(self, user_id, model):
        return self.session.query(model.user_id).filter_by(user_id=user_id).first() is not None
    
    def get_client(self, user_id):
        return self.session.query(Clients).filter_by(user_id=user_id).one_or_none()

    def update(self, user_id, field, value):
        self.session.query(Clients).filter(Clients.user_id == user_id).update({field: value})
        self.session.commit()

    def set_next_status(self, user_id, status):
        self.session.query(Clients).filter(Clients.user_id == user_id).update({"status": status + 1})
        self.session.commit()

    def set_prev_status(self, user_id, status):
        self.session.query(Clients).filter(Clients.user_id == user_id).update({"status": status - 1})
        self.session.commit()

    def save_client(self, client):
        data = {
            'user_id': client.get('id'),
            'first_name': client.get('first_name'),
            'last_name': client.get('last_name'),
            'nickname': client.get('nickname'),
            'city': client.get('city', {}).get('title'),
            'bdate': client.get('bdate'),
            'country': client.get('country', {}).get('title'),
            'sex': client.get('sex')
        }
        if not self.is_user_exists(data['user_id'], Clients):
            client = Clients(**data)
            print('client db', client)
            self.session.add(client)
            self.session.commit()
            return client

    def save_candidate(self, user, photos):
        data = {
            'user_id': user.get('id'),
            'first_name': user.get('first_name'),
            'last_name': user.get('last_name'),
            'domain': user.get('domain'),
            'photos': photos,
        }
        if not self.is_user_exists(data['user_id'], Candidates):
            candidate = Candidates(**data)
            self.session.add(candidate)
            self.session.commit()
            return candidate

    def get_candidates(self):
        return self.session.query(Candidates).order_by(Candidates.id.desc()).all()

    def drop_candidate(self):
        last = self.session.query(Candidates).order_by(Candidates.id.desc()).limit(1).one()
        self.session.query(Candidates).filter(Candidates.id == last.id).delete()
        self.session.commit()
        return last

