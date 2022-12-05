import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
import enum


class SexEnum(enum.IntEnum):
    female = 1
    male = 2


Base = declarative_base()


class Clients(Base):
    __tablename__ = "clients"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String(length=40))
    last_name = sq.Column(sq.String(length=40))
    nickname = sq.Column(sq.String(length=40))
    city = sq.Column(sq.String(length=40))
    bdate = sq.Column(sq.String(length=40))
    country = sq.Column(sq.String(length=40))
    sex = sq.Column(sq.Enum(SexEnum))
    status = sq.Column(sq.Integer, default=0)
    greet = sq.Column(sq.Boolean, default=False)
    changing_param = sq.Column(sq.String(length=40))
    start_search = sq.Column(sq.Boolean, default=False)
    candidate_sex = sq.Column(sq.String(length=2))
    candidate_age_from = sq.Column(sq.Integer)
    candidate_age_to = sq.Column(sq.Integer)
    candidate_city_id = sq.Column(sq.String(length=40))
    candidate_id = sq.Column(sq.Integer)
    offset = sq.Column(sq.Integer, default=-10)

    def __str__(self):
        return (f'Пользователь (id: {self.user_id}): '
                f'"{self.first_name} {self.last_name}" ;')


class Candidates(Base):
    __tablename__ = "candidates"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String(length=40))
    last_name = sq.Column(sq.String(length=40))
    domain = sq.Column(sq.String(length=1000))
    photos = sq.Column(sq.String(length=1000))
    favorite = sq.Column(sq.Boolean, default=False)
    viewed = sq.Column(sq.Boolean, default=False)


class Clients_and_Candidates(Base):
    __tablename__ = "clients_and_candidates"

    id = sq.Column(sq.Integer, primary_key=True)

    client_id = sq.Column(
        sq.Integer, sq.ForeignKey("clients.user_id", ondelete="CASCADE"))
    clients = relationship(
        Clients, backref="clients_and_candidates", cascade="all,delete")

    candidate_id = sq.Column(
        sq.Integer, sq.ForeignKey("candidates.user_id", ondelete="CASCADE"))
    candidates = relationship(
        Candidates, backref="clients_and_candidates", cascade="all,delete")


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
