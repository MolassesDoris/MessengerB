from flask import Flask, request
import json
import requests
app = Flask(__name__)
import praw
import Quick_replies as qr
import Secret as s
from nltk import pos_tag, word_tokenize
import googlemaps
from Users import User, Location, Post

google_places = googlemaps.Client(s.GAPI)

Users = []

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

        if(isinstance(message,Location)):
            handle_location(PAT, user, message)
        elif ("pic" in message.lower() or "send" in message.lower() or "get" in message.lower()):
            send_message_reddit(PAT, user, message)
        # elif("look" in message or "search" in message and user.get_location() is not None):
        #     handle_geosearch(PAT, user, message)
        # elif("look" in message or "search" in message and user.get_location() is None):
        #     ask_for_location(user, PAT)
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


if __name__ == '__main__':
    app.run()
