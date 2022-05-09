import jwt
from datetime import datetime, timedelta
from model.User import User
import os



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
        'exp': datetime.utcnow() + timedelta(hours=os.environ.get("JWT_EXPIRES_IN"))
    }
    return jwt.encode(
        payload,
        os.environ.get("APP_SECRET_KEY"),
        algorithm='HS256'
    )  

def decode_jwt(jwt_token):
    payload = jwt.decode(jwt_token, os.environ.get("APP_SECRET_KEY"), algorithms=['HS256'])
    return payload    