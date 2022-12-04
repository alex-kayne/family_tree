import enum

from app.store.database.models import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB


class GenderEnum(enum.Enum):
    male = 'male'
    female = 'female'


class Tree(db.Model):
    __tablename__ = 'tree'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    birth_date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    pids = db.Column(JSONB(none_as_null=True), nullable=True)
    mid = db.Column(db.Integer, nullable=True)
    fid = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.Enum(GenderEnum), nullable=False)
    dt_created = db.Column(db.DateTime, default=datetime.now())
    dt_updated = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_url = db.Column(db.Text, nullable=True)

    _user_id_idx = db.Index('user_id_idx', user_id)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    picture = db.Column(db.Text, nullable=False)

    _email_idx = db.Index('email_index', email)
