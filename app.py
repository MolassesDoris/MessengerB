# EAAHKlA4PzIABAIpdIctX2mL19yEJl67ntOEu1m2BwXfIYCwB1uVKZCRzRZCWZCugqTb5i555ARBaoPiZBZCJG7W1wiwTyn9eKcx1b767bazSSeAZCBsmacITxhV6TAdZC82qHpv0VZC0ZCMWyr1dBYKpJiZCp7VqEWj10zjrWbwTiyltfd7UWoo8WQ
# https://pythontips.com/2017/04/13/making-a-reddit-facebook-messenger-bot/
#  praw.Reddit(client_id = '8jBSydMLLF6uvg', client_secret = '3w8bcqu7FYTpGJNCm3oQILV7DtM'

from flask import Flask, request
import json
import requests
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

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

@app.route('/', methods=['GET'])
def handle_verification():
    # hi='my_voice_is_my_password_verify_me'
    print("Handling Verification.")

    if request.args.get('hub.verify_token') == 'my_voice_is_my_password_verify_me':
    # if hi == 'my_voice_is_my_password_verify_me':
        print("Verification successful!")
        return(request.args.get('hub.challenge'))
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
    return "ok"

def messaging_events(payload):
    """Generate tuples of (sender_id, message_text) from the
    provided payload.
    """
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]
    for event in messaging_events:
        if "message" in event and "text" in event["message"]:
            yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
        else:
            yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
    """Send the message text to recipient with id recipient.
    """
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params={"access_token": token},
                      data=json.dumps({
                          "recipient": {"id": recipient},
                          "message": {"text": text.decode('unicode_escape')}
                      }),
                      headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print(r.text)

relationship_table = db.Table('relationship_table,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id').nullable = False),
    db.Column('post_id',db.Integer,db.ForeignKey('posts.id'),nullable=False),
    db.PrimaryKeyConstraint('user_id', 'post_id') )

class Users(db.Model):
    id = db.column(db.Integer, primary_key = True)
    name = db.column(db.String(255), nullable = False)
    posts = db.relationship('Posts', secondary = relationship_table, backref='users')

    def __init__(self, name):
        self.name = name

class Posts(db.Model):
    id = db.column(db.Integer, primary_key = True)
    name = db.column(db.String(255),unique = True ,nullable = False)
    url = db.column(db.String, nullable = False)

    def __init__(self, name, url):
        self.name = name
        self.url = url
if __name__ == '__main__':
    app.run()
