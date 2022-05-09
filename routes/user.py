import openai
from flask import request, jsonify, Blueprint
from helper import auth_tool
import os


user = Blueprint('user', __name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

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
