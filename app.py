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

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
reddit = praw.Reddit(client_id=s.CLIENT_ID,
                     client_secret=s.CLIENT_SECRET,
                     password=s.PASSWORD,
                     user_agent=s.USER_AGENT,
                     username=s.USERNAME)

PAT = s.PAT

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

@app.route('/', methods=['GET'])
def handle_verification():
    print("Handling Verification.")

    if request.args.get('hub.verify_token') == 'my_voice_is_my_password_verify_me':
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
        mark_seen(sender, PAT)
        typing_on(sender, PAT)
        send_message(PAT, sender, message)
        typing_off(sender, PAT)
    return("ok")

def messaging_events(payload):
    """Generate tuples of (sender_id, message_text) from theLowCholestoralMemes
    provided payload.
    """
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]
    for event in messaging_events:
        print(event["message"]["text"])
        print(type(event["message"]["text"]))
        if(event.get("postback")):
            print("Inside Postback")
            yield(event["sender"]["id"],"Hi, I send memes, pics of doggos etc. Just request and I shall send.")
        elif "message" in event and "text" in event["message"]:
            yield(event["sender"]["id"], event["message"]["text"].encode('unicode_escape'))
        else:
            yield(event["sender"]["id"], "I can't echo this")


def send_message(token, recipient, text):
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
    else:
        print("Unknown Subreddit.")
        data = to_json({
            "recipient": {"id": recipient},
            "message": {"text": "Unknown Meme Source."}})
        messagerequestpost(token, data)

    if(subreddit_name != ""):
        myUser = sessionhandle(db.session, Users, name = recipient)
        print(subreddit_name)
        for submission in reddit.subreddit(subreddit_name).hot(limit=None):
            if (submission.link_flair_css_class == 'image') or ((submission.is_self != True) and ((".jpg" in submission.url) or (".png" in submission.url))):
                query_result = Posts.query.filter(Posts.name == submission.id).first()
                print(questartedry_result)
                if query_result is None:
                    myPost = Posts(submission.id, submission.url)
                    myUser.posts.append(myPost)
                    db.session.commit()
                    payload = submission.url
                    break
                elif myUser not in query_result.users:
                    myUser.posts.append(query_result)
                    db.session.commit()
                    payload = submission.url
                    break
                else:
                    continue
        data = to_json({
            "recipient": {"id": recipient},
            "message": {"attachment": {
                          "type": "image",
                          "payload": {
                            "url": payload
                          }}, "quick_replies":qr.quick_replies_list}})
        messagerequestpost(token, data)
def sessionhandle(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    # we check the users or posts model and filter and return the instance of the session
    # if that item is not in the model then we add
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

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

# def get_started(token):
#     print("=============================")
#     print("Get Started")
#     print("=============================")
#
#     data = to_json({
#     "setting_type": "call_to_actions",
#     "thread_state": "new_thread",
#     "call_to_actions": [{
#         "payload": "Hi, I send memes, pics of doggos etc. Just request and I shall send."
#     }]})
#
#     handle_thread_settings(token, data)

def hide_starting_button(token):
    data = to_json({
    "setting_type": "call_to_actions",
    "thread_state": "new_thread",
    })

    handle_thread_settings(token, data)

def typing_on(recipient, token):
    print("Replying to {}".format(recipient))

    data = to_json({
        "recipient": {"id": recipient},
        "sender_action": "typing_on"
    })

    messagerequestpost(token, data)

def typing_off(recipient, token):
    data = to_json({"recipient": {"id": recipient},
    "sender_action": "typing_off"})

    messagerequestpost(token, data)

def mark_seen(recipient, token):

    data = to_json({"recipient": {"id": recipient},
    "sender_action": "mark_seen"})

    messagerequestpost(token, data)

relationship_table=db.Table('relationship_table',
    db.Column('user_id', db.Integer,db.ForeignKey('users.id'), nullable=False),
    db.Column('post_id',db.Integer,db.ForeignKey('posts.id'),nullable=False),
    db.PrimaryKeyConstraint('user_id', 'post_id'))

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    posts=db.relationship('Posts', secondary=relationship_table, backref='users' )

    def __init__(self, name=None):
        self.name = name

class Posts(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, unique=True, nullable=False)
    url=db.Column(db.String, nullable=False)

    def __init__(self, name=None, url=None):
        self.name = name
        self.url = url

if __name__ == '__main__':
    app.run()
