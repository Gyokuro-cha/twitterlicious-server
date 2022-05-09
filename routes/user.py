import openai
from flask import request, jsonify, Blueprint
import config as config
from helper import auth_tool


user = Blueprint('user', __name__)

openai.api_key = config.openai_api['key']

@user.post('/profile')
def get_user_profile():
    """Return User obj"""
    #decode the json
    jwt = request.cookies.get('Bearer')
    try:
        payload = auth_tool.decode_jwt(jwt)
        return jsonify(payload), 200 
    except Exception as es:
        print(es)
        return jsonify({"error": "Invalid JWT"}), 401
