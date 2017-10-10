# EAAHKlA4PzIABAIpdIctX2mL19yEJl67ntOEu1m2BwXfIYCwB1uVKZCRzRZCWZCugqTb5i555ARBaoPiZBZCJG7W1wiwTyn9eKcx1b767bazSSeAZCBsmacITxhV6TAdZC82qHpv0VZC0ZCMWyr1dBYKpJiZCp7VqEWj10zjrWbwTiyltfd7UWoo8WQ
# https://pythontips.com/2017/04/13/making-a-reddit-facebook-messenger-bot/
#  praw.Reddit(client_id = '8jBSydMLLF6uvg', client_secret = '3w8bcqu7FYTpGJNCm3oQILV7DtM'
import os
from flask import Flask, request
import json
import requests
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
import praw
import Quick_replies as qr
import Secret as s
from nltk import pos_tag, word_tokenize
from googleplaces import GooglePlaces, types, lang

google_places = GooglePlaces(s.GAPI)
Users = []

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://oklfqgmetzhqde:7e0fa4548443cfb59a98fb3075a1d241d3044f059bd6e1f6b969ee674c0bcd0e@ec2-176-34-242-58.eu-west-1.compute.amazonaws.com:5432/d3av8d9m9fdf8p'
# print("==============================")
# print(os.environ['DATABASE_URL'])
# print("==============================")
db = SQLAlchemy(app)
reddit = praw.Reddit(client_id=s.CLIENT_ID,
                     client_secret=s.CLIENT_SECRET,
                     password=s.PASSWORD,
                     user_agent=s.USER_AGENT,
                     username=s.USERNAME)

PAT = s.PAT

class Location():

    def __init__(self, longitude, latitude):
        self._longitude = longitude
        self._latitude = latitude

    def get_longitude(self):
        return self._longitude

    def get_latitude(self):
        return self._latitude


def to_json(data):
    return(json.dumps(data))

def handle_thread_settings(token,data):
    r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings",
                      params={"access_token": token},
                      data = data,headers={'Content-type': 'application/json'})

    if r.status_code != requests.codes.ok:
        print(r.text)

def messagerequestpost(token, data):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=data,headers={'Content-type': 'application/json'})

    if r.status_code != requests.codes.ok:
        print(r.text)
    # if "URL provided is not whitelisted" in r.text:
    #     handle_whitelisting(token, data)

@app.route('/', methods=['GET'])
def handle_verification():
    print("Handling Verification.")

    if request.args.get('hub.verify_token') == 'verify_token_fds':
        print("Verification successful!")
        return(request.args.get('hub.challenge',''))
    else:
        print("Verification failed!")
        return('Error, wrong validation token')

@app.route('/', methods=['POST'])
def handle_messages():
    print("Handling Messages")
    # get_started(PAT)
    payload = request.get_data()
    print(payload)
    for sender, message in messaging_events(payload):
        print("Incoming from %s: %s" % (sender, message))
        user = next((u1 for u1 in Users if u1.get_id() == sender), None)
        if user is None:
            user = User(sender)
            Users.append(user)
        mark_seen(user, PAT)
        typing_on(user, PAT)
        if("pic" in message or "send" in message or "get" in message):
            send_message_reddit(PAT, user, message)
        elif(isinstance(message,Location)):
            handle_location(PAT, sender, message)
        elif("look" in message or "search" in message and user.get_location() is not None):
            handle_geosearch(PAT, user, message)
        elif("look" in message or "search" in message and user.get_location() is None):
            ask_for_location(user, PAT)
        else:
            print("Not Sure how to respond.")
            data = to_json({
                "recipient": {"id": user.get_id()},
                "message": {"text": "I don't understand."}})
            messagerequestpost(PAT, data)
    return("ok")

def handle_location(token, user, location):
    user.setLocation(location)
    data = to_json({
        "recipient": {"id": user.get_id()},
        "message": {"text": "Updated Location."}})
    messagerequestpost(token, data)

def handle_geosearch(token, recipient, text, amttodisplay = 3):
    search_words= " ".join([token for token, pos in pos_tag(word_tokenize(text)) if pos.startswith('N') or pos.startswith('J')])

    query_result = google_places.nearby_search(
            location='{},{}'.format(recipient.get_location().get_longitude(), recipient.get_location().get_latitude()),radius=2000, keyword=search_words)
    if len(query_result.places) >0 :
        elements = []
        for indx, place in enumerate(query_result.places):
            place.get_details()
            image_url = place.url
            if(len(place.photos)>0):
                photo = place.photos[0]
                photo.get(maxheight=500, maxwidth=500)
                image_url = photo.url
            element = {"title": place.name.encode('utf-8'),
                       "image_url": image_url,
                       "buttons": [{"title": "Open in Maps",
                                    "type": "web_url",
                                    "url": place.url,
                                    "messenger_extensions": 'true',
                                    "webview_height_ratio": "tall",
                                    }]}
            element = json.dumps(element)
            elements.append(element)
            if(indx == amttodisplay):
                break
        data = to_json({
            "recipient":{"id": recipient.get_id()},
            "message":{
                "attachment":{
                    "type" : "template",
                    "payload" : {
                        "template_type" : "list",
                        "top_element_style": "compact",
                        "elements": elements
                    }
                }
            }
        })
    else: data = to_json({
            "recipient": {"id": recipient.get_id()},
            "message": {"text": "Couldn't find {}".format(search_words)}})

    messagerequestpost(token, data)

def ask_for_location(user, token):
    data = to_json({
        "recipient": {"id": user.get_id()},
        "message": {"text": "I'd love to help you look. Could you send me a location?"}})
    messagerequestpost(token, data)

def messaging_events(payload):
    """Generate tuples of (sender_id, message_text) from theLowCholestoralMemes
    provided payload.
    """
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]
    for event in messaging_events:
        if(event.get("postback")):
            print("=============================================")
            print("Inside Postback")
            print("=============================================")
            if event["postback"]["payload"]=="Get Started":
                yield(event["sender"]["id"],"Get Started")
        elif "message" in event and "text" in event["message"]:
            yield(event["sender"]["id"], event["message"]["text"].encode('unicode_escape'))
        elif (str(event['message']['attachments'][0]['type']) == 'location'):
            latitude = event['message']['attachments'][0]['payload']['coordinates']['lat']
            longitude = event['message']['attachments'][0]['payload']['coordinates']['long']
            yield (event["sender"]["id"], Location(latitude, longitude))
        else:
            yield(event["sender"]["id"], "I can't echo this")

def send_message_reddit(token, recipient, text):
    """Send the message text to recipient with id recipient.
    """

    subreddit_name =""
    if("meme" in str(text.lower())):
        subreddit_name = "meirl"
    elif("rarepuppers" in str(text.lower()) or "dog" in str(text.lower()) or "puppers" in str(text.lower())):
        subreddit_name = "rarepuppers"
    elif("black") in str(text.lower()) or "blackpeople" in str(text.lower()):
        subreddit_name = "blackpeopletwitter"
    elif("christian") in str(text.lower()) or "dankchristian" in str(text.lower()):
        subreddit_name = "dankchristianmemes"
    elif("started" in str(text.lower()) or "get started" in str(text.lower())):
        data = to_json({
            "recipient": {"id": recipient},
            "message": {"text": "Hi I'm MemeBot. I can send you memes and doggo pics if you request."}})
        messagerequestpost(token, data)
    else:
        print("Unknown Subreddit.")
        data = to_json({
            "recipient": {"id": recipient},
            "message": {"text": "Unknown Meme Source."}})
        messagerequestpost(token, data)

    if(subreddit_name != ""):
        for submission in reddit.subreddit(subreddit_name).hot(limit=None):
            if (submission.link_flair_css_class == 'image') or ((submission.is_self != True) and ((".jpg" in submission.url) or (".png" in submission.url))):
                user_posts = recipient.get_posts()
                if(user_posts is None):
                    user_posts = []
                if(next((post for post in user_posts if post.get_id() == submission.id), None) is None):
                    recipient.addposts(Post(submission.id, submission.url))
                    payload = submission.url
                    break
                else:
                    continue
        data = to_json({
            "recipient": {"id": recipient.get_id()},
            "message": {"attachment": {
                          "type": "image",
                          "payload": {
                            "url": payload
                          }}, "quick_replies":qr.quick_replies_list}})
        messagerequestpost(token, data)

def mark_seen(recipient, token):

    recipient_id = recipient.get_id()
    data = to_json({"recipient": {"id": recipient_id},
    "sender_action": "mark_seen"})

    messagerequestpost(token, data)

def typing_on(recipient, token):
    recipient_id = recipient.get_id()
    print("Replying to {}".format(recipient_id))

    data = to_json({
        "recipient": {"id": recipient_id},
        "sender_action": "typing_on"
    })

    messagerequestpost(token, data)

def typing_off(recipient, token):
    data = to_json({"recipient": {"id": recipient.get_id()},
    "sender_action": "typing_off"})

    messagerequestpost(token, data)

def hide_starting_button(token):
    data = to_json({
    "setting_type": "call_to_actions",
    "thread_state": "new_thread",
    })

    handle_thread_settings(token, data)

def greetings(token):
    print("=============================")
    print("Handling Greetings")
    print("=============================")

    data = to_json({
        'setting_type': 'greeting',
        'greeting': {
            'text': "Hi friend. I am MemeBot", "locale":"default"
        }
    })

    handle_thread_settings(token, data)

class Post():

    def __init__(self, id, url):
        self._id = id
        self._url = url

    def get_id(self):
        return self._id
    def get_url(self):
        return self._url
class User():

    def __init__(self, id):
        self._id = id
        self._posts = None
        self._location = None
        # if(self not in Users):
        #     Users.append(self)

    def get_id(self):
        return self._id

    def get_posts(self):
        return self._posts

    def get_location(self):
        return self._location

    def addposts(self,post):
        if(self._posts is None):
            self._posts = []
        self._posts.append(post)

    def setLocation(self,location):
        self._location = location

if __name__ == '__main__':
    app.run()
