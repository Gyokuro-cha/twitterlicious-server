from datetime import datetime
from typing_extensions import Required
from mongoengine import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, Document):
    meta = {'collection': 'users'}
    twitter_id = IntField(required=True)
    twitter_access_token = StringField(required=True)
    twitter_access_token_secret = StringField(required=True)
    email = EmailField(default=None, unique=True, sparse=True,)
    username = StringField(unique=True)
    password_hash = StringField(Required=False)
    active = BooleanField(default=True)
    isAdmin = BooleanField(default=False)
    hasTrainingModel = BooleanField(default=False)
    modelName = StringField(default=None)
    plan = StringField(default='trail', Required=True) #trail, premium, pro 
    payment_schedule = StringField(default='trail', Required=True) #trail, monthly, quarterly, yearly
    created_at = DateTimeField(default=datetime.now)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)