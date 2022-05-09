from ast import Try
from flask import Flask, request, jsonify, make_response, redirect, url_for, flash
from flask_cors import CORS
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.consumer import oauth_authorized
from werkzeug.security import check_password_hash
import openai
from model.User import User
from flask_mongoengine import MongoEngine
from routes.tweet_generator import generator
from routes.user import user
import config as config
from helper import auth_tool



app = Flask(__name__)

app.config['SECRET_KEY'] = config.app_secret['key']

twitter_blueprint = make_twitter_blueprint(
    api_key=config.twitter_api['key'], 
    api_secret=config.twitter_api['secret'])

openai.api_key = config.openai_api['key']

#DB
app.config['MONGODB_SETTINGS'] = {
    'db': config.mongodb_settings['db'],
    'host': config.mongodb_settings['host'],
    'port': config.mongodb_settings['port'],
    'serverSelectionTimeoutMS':config.mongodb_settings['serverSelectionTimeoutMS']
}
#CORS
app.config['CORS_HEADERS'] = 'Content-Type'

mongo_engine = MongoEngine(app)

def setup():
    #Allows users to make authenticated requests. If true, injects the Access-Control-Allow-Credentials header in responses.
    CORS(app, supports_credentials=True) 
    app.register_blueprint(twitter_blueprint, url_prefix='/login')
    app.register_blueprint(generator)
    app.register_blueprint(user)



setup()       
 
###############
# Signals
###############
@oauth_authorized.connect_via(twitter_blueprint)
def twitter_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in.", category="error")
        return False

    resp = twitter.get("account/verify_credentials.json")
    if not resp.ok:
        flash("Failed to log in.", category="error")
        return False

    user_info = resp.json()
    twitter_id = user_info['id']
    user_name = user_info['screen_name']
   
    user = User.objects(twitter_id=twitter_id).first()
    

    if user is None:
        try:
            session_user = User(username=user_name, 
            twitter_id=twitter_id, 
            twitter_access_token=token['oauth_token'], 
            twitter_access_token_secret=token['oauth_token_secret'])
            session_user.save()

        except Exception as es:
            print(es) 
                   
    return build_response(user_name) 



def build_response(user_name):
    jwt = auth_tool.create_payload(user_name)
    resp = make_response(redirect(config.app_settings['local_fe_url'] + '/tweet'))
    resp.set_cookie('Bearer', value =  jwt, httponly = False, samesite='None', secure=True)
    return resp

#############
# ROUTES
############

##TODO function to get user status


# @app.route('/')
# def index():
#     #The bearer is stored on the server side, they won't see it in the client
#      return '<h1>Hello!</h1>'

@app.route('/logout') 
def logout():
    resp = make_response(redirect(config.app_settings['local_fe_url'] + '/'))
    resp.set_cookie('Bearer', '', expires=0)
    return resp 

@app.route('/authenticated', methods=['POST']) 
def authenticated():
    #decode the json
    jwt = request.cookies.get('Bearer')
    try:
        payload = auth_tool.decode_jwt(jwt)
        return jsonify({"data": "Authenticated"}), 200 
    except Exception as es:
        print(es)
        return jsonify({"error": "Invalid JWT"}), 401  
        


@app.route('/')
def twitter_login():
    #Expires means time out
    #We need to
    try:
        jwt = request.cookies.get('Bearer')
        if not jwt:
            redirect(url_for('twitter.login'))
    except Exception as es:
        print(es)
        return redirect(url_for('twitter.login'))
    
    
    if not twitter.authorized:
        return redirect(url_for('twitter.login'))

    account_info = twitter.get('account/settings.json')

    if account_info.ok:
        account_info_json = account_info.json()
        user_name = account_info_json['screen_name']
        ##TODO check if user is subscribed, if not don't login, send them to payment page
        
        jwt = auth_tool.create_payload(user_name)
        resp = make_response(redirect(config.app_settings['local_fe_url'] + '/tweet'))
        resp.set_cookie('Bearer', value =  jwt, httponly = False, samesite='None', secure=True)

        return resp
    elif account_info.status_code == 401:
        return redirect(url_for('twitter.login'))
  
     

if __name__ == '__main__':
    app.run(host='0.0.0.0')
