import jwt
from datetime import datetime, timedelta
import config as config
from model.User import User


def create_payload(user_name):
    db_user = User.objects.get(username=user_name)
    jwt_user = create_jwt(db_user)
    return jwt_user


def create_jwt(user):
    payload = {
        'user_id': user.twitter_id,
        'user_name': user.username,
        'has_training_model': user.hasTrainingModel,
        'plan': user.plan,
        'exp': datetime.utcnow() + timedelta(hours=config.app_settings['jwt_expires_in'])
    }
    return jwt.encode(
        payload,
        config.app_secret['key'],
        algorithm='HS256'
    )  

def decode_jwt(jwt_token):
    payload = jwt.decode(jwt_token, config.app_secret['key'], algorithms=['HS256'])
    return payload    