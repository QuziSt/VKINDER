import vk_api


from models import create_tables, Clients, Candidates, Clients_and_Candidates
from sqlalchemy.exc import NoResultFound
from sqlalchemy.inspection import inspect
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from conf import get_config


def get_DSN(config):
    PG_USER = config['PG']['PG_USER']
    PG_PASSWORD = config['PG']['PG_PASSWORD']
    SERVER = config['PG']['SERVER']
    PORT = config['PG']['PORT']
    DB_NAME = config['PG']['DB_NAME']
    return f'postgresql://{PG_USER}:{PG_PASSWORD}@{SERVER}:{PORT}/{DB_NAME}'


class DbService:

    def __init__(self, session):
        self.session = session

    def is_user_exists(self, user_id, model):
        return self.session.query(model.user_id).filter_by(user_id=user_id).first() is not None

    def get_client(self, user_id):
        q = self.session.query(Clients_and_Candidates).filter(
            Clients_and_Candidates.client_id == user_id)
        candidates = self.session.query(Clients).filter(
            Clients.user_id == user_id).join(q.subquery(), isouter=True)
        return candidates.one_or_none()

    def update(self, table, user_id, field, value):
        model = {
            "candidates": Candidates,
            "clients": Clients
        }[table]
        self.session.query(model).filter(
            model.user_id == user_id).update({field: value})
        self.session.commit()

    def set_next_status(self, user_id, status):
        self.session.query(Clients).filter(
            Clients.user_id == user_id).update({"status": status + 1})
        self.session.commit()

    def set_prev_status(self, user_id, status):
        self.session.query(Clients).filter(
            Clients.user_id == user_id).update({"status": status - 1})
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

    def save_candidate(self, user, client_id):
        data = {
            'user_id': user.get('id'),
            'first_name': user.get('first_name'),
            'last_name': user.get('last_name'),
            'domain': user.get('domain'),
        }
        data_rel = {
            'client_id': client_id,
            'candidate_id': user.get('id')
        }
        if not self.is_user_exists(data['user_id'], Candidates):
            candidate = Candidates(**data)
            self.session.add(candidate)
            rel = Clients_and_Candidates(**data_rel)
            self.session.add(rel)
            # self.session.commit()
            # return candidate

    def save_favorite(self, client_id, candidate_id):
        cls_and_cands = self.session.query(Clients_and_Candidates)
        candidates = self.session.query(
            Candidates).join(cls_and_cands.subquery())
        candidate = candidates.filter(
            Clients_and_Candidates.client_id == client_id,
            Candidates.user_id == candidate_id
        ).one()
        if not candidate.favorite:
            self.update("candidates", candidate.user_id, "favorite", True)
            return candidate

    def get_favorites(self, client_id):
        cls_and_cands = self.session.query(Clients_and_Candidates)
        candidates = self.session.query(
            Candidates).join(cls_and_cands.subquery())
        return candidates.filter(
            Clients_and_Candidates.client_id == client_id,
            Candidates.favorite == True
        ).order_by(Candidates.user_id.desc()).all()

    def drop_candidate(self, client_id):
        cls_and_cands = self.session.query(Clients_and_Candidates)
        candidates = self.session.query(
            Candidates).join(cls_and_cands.subquery())
        last = candidates.filter(
            Clients_and_Candidates.client_id == client_id,
            Candidates.favorite == True
        ).order_by(Candidates.user_id.desc()).order_by(
            Candidates.id.desc()).limit(1).one_or_none()
        if last:
            self.session.query(Candidates).filter(
                Candidates.id == last.id).delete()
            self.session.commit()
            return last

    def get_candidate(self, client_id):
        cls_and_cands = self.session.query(Clients_and_Candidates)
        candidates = self.session.query(
            Candidates).join(cls_and_cands.subquery())
        result = candidates.filter(
            Clients_and_Candidates.client_id == client_id,
            Candidates.favorite == False,
            Candidates.viewed == False
        ).all()
        return result if not result else result[0]

    def save_candidates(self, candidates, user_id):
        for candidate in candidates:
            self.save_candidate(candidate, user_id)
        self.session.commit()

    def pop_candidate(self, user_id):
        candidate = self.get_candidate(user_id)
        if candidate:
            self.update("candidates", candidate.user_id, "viewed", True)
            return candidate

    def drop_candidates(self, client_id):
        self.session.query(Candidates).filter(
            Candidates.user_id == Clients_and_Candidates.candidate_id,
            Candidates.favorite == False,
            Clients_and_Candidates.client_id == client_id,
        ).delete(synchronize_session=False)
        self.session.commit()
