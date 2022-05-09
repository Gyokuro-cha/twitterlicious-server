import openai
from flask import request, jsonify, Blueprint
from helper import auth_tool
import os



generator = Blueprint('generator', __name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")


def generate_tweet_by_prompt(prompt):
    #"davinci:ft-45-degrees-of-wizard:elonmusk-tweets-500-2022-03-24-20-13-02"
    #"davinci:ft-45-degrees-of-wizard:nofap-tweet-with-end-char-2022-03-19-17-13-25"
    #"davinci"
    response = openai.Completion.create(
        model="davinci",
        prompt=prompt,
        max_tokens=80,
        temperature=0.6,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1)
        

    return response           

@generator.get('/generate-tweet')
def generate_tweet():
    """Return simple "Hello" Greeting."""
    new_tweet = generate_tweet_by_prompt('')
    text = new_tweet.choices[0].text
    print(request.cookies)

    html = f"<html><body><h1>{text}</h1></body></html>"
    return html 


@generator.post("/generate-tweet")
def add_comment():
    """Handle POST request for generating new tweet"""

    #decode the json
    jwt = request.cookies.get('Bearer')
    try:
        payload = auth_tool.decode_jwt(jwt)
    except Exception as es:
        print(es)
        return jsonify({"error": "Invalid JWT"}), 401   

    #TODO if they have training model, use it 
    #TODO if they haven't paid or not in training period, don't use it
    request_json = request.get_json()
    prompt = request_json['data']['prompt']
    new_tweet = generate_tweet_by_prompt(prompt)
    
    result_text = new_tweet.choices[0].text

    return jsonify({'result': result_text})  