import vk_api


from models import create_tables, Clients, Candidates
from sqlalchemy.exc import NoResultFound
from sqlalchemy.inspection import inspect


class DbService:
    def __init__(self, session):
        self.session = session

    def is_user_exists(self, user_id, model):
        return self.session.query(model.user_id).filter_by(user_id=user_id).first() is not None

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
            return Clients(**data)

    def save_candidate(self, user, photos):
        data = {
            'user_id': user.get('id'),
            'first_name': user.get('first_name'),
            'last_name': user.get('last_name'),
            'domain': user.get('domain'),
            'photos': photos,
        }
        if not self.is_user_exists(data['user_id'], Candidates):
            return Candidates(**data)

    def get_candidates(self):
        return self.session.query(Candidates).order_by(Candidates.id.desc()).all()

    def drop_candidate(self):
        last = self.session.query(Candidates).order_by(Candidates.id.desc()).limit(1).one()
        self.session.query(Candidates).filter(Candidates.id == last.id).delete()
        return last

