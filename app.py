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
# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
reddit = praw.Reddit(client_id='8jBSydMLLF6uvg',
                     client_secret='3w8bcqu7FYTpGJNCm3oQlLV7DtM',
                     password='memesgalore',
                     user_agent='my user agent',
                     username='LowCholestoralMemes')

PAT = 'EAAHKlA4PzIABALdD5WlzgkFuZCqEcvC5LfKixRsdI02UilqkAOyWZBpnWvQivb3rHWiaTd8j5hhS9mbz1zVlSxWSjE9ZCQ0CY9vkEoZCKbIFhNgvIMa6vVph56TcxaMtkf2rUNJWm8BVBZCrihZAvNZCiaxAPuXNOcFzXIgOe0AAHT4hbpHrqAR'
quick_replies_list = [{
    "content_type":"text",
    "title":"Meme",
    "payload":"meme",},{

    "content_type":"text",
    "title":"meirl",
    "payload":"meirl",
    }
]

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
    payload = request.get_data()
    print(payload)
    for sender, message in messaging_events(payload):
        print("Incoming from %s: %s" % (sender, message))
        send_message(PAT, sender, message)
    return("ok")

def messaging_events(payload):
    """Generate tuples of (sender_id, message_text) from theLowCholestoralMemes
    provided payload.
    """
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]
    for event in messaging_events:
        if "message" in event and "text" in event["message"]:
            yield(event["sender"]["id"], event["message"]["text"].encode('unicode_escape'))
        else:
            yield(event["sender"]["id"], "I can't echo this")


def send_message(token, recipient, text):
    """Send the message text to recipient with id recipient.
    """
    subreddit_name =""
    if("meme" in str(text.lower())):
        subreddit_name = "memeeconomy"
    elif("rarepuppers" in str(text.lower() or "dog" in str(text.lower()) or "puppers" in str(text.lower()))):
        subreddit_name = "rarepuppers"

    myUser = sessionhandle(db.session, Users, name = recipient)

    for submission in reddit.subreddit(subreddit_name).hot(limit=None):
        if (submission.link_flair_css_class == 'image') or ((submission.is_self != True) and ((".jpg" in submission.url) or (".png" in submission.url))):
            query_result = Posts.query.filter(Posts.name == submission.id).first()
            print(query_result)
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

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": token},
        data=json.dumps({
            "recipient": {"id": recipient},
            "message": {"attachment": {
                          "type": "image",
                          "payload": {
                            "url": payload
                          }},
                          "quick_replies":quick_replies_list}
        }),
        headers={'Content-type': 'application/json'})

    if r.status_code != requests.codes.ok:
        print(r.text)
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
