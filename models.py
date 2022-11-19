import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
import enum

class SexEnum(enum.IntEnum):
    female = 1
    male = 2


Base = declarative_base()


class Client(Base):
    __tablename__ = "client"

    id = sq.Column(sq.Integer, primary_key=True)
    client_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String(length=40))
    last_name = sq.Column(sq.String(length=40))
    nickname = sq.Column(sq.String(length=40))
    city = sq.Column(sq.String(length=40))
    bdate = sq.Column(sq.String(length=40))
    country = sq.Column(sq.String(length=40))
    sex = sq.Column(sq.Enum(SexEnum))

    def __str__(self):
        return f'Пользователь (id: {self.id}): "{self.first_name} {self.last_name}" ;'


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)




