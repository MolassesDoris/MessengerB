import json

import praw
import requests
from googleplaces import GooglePlaces
import Quick_replies as qr
import GoogleMapsHandler
import Secret as s
from RedditMessageHandler import send_message_reddit
from Users import *
from Utils import to_json
import Buttons


PAT =s.PAT


def handle_message_req(request, Users):
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

        if (isinstance(message, Location)):
            GoogleMapsHandler.handle_location(PAT, user, message)
        elif ("pic" in message.lower() or "send" in message.lower() or "get" in message.lower()):
            print("Initialized Reddit API Client")
            reddit = praw.Reddit(client_id=s.CLIENT_ID,
                                 client_secret=s.CLIENT_SECRET,
                                 password=s.PASSWORD,
                                 user_agent=s.USER_AGENT,
                                 username=s.USERNAME)
            send_message_reddit(PAT, user, message, reddit)
        elif("look" in message.lower() and user.get_location() is not None):
            print("Initialized Google Maps API Client")
            google_places = GooglePlaces(s.GAPI)
            GoogleMapsHandler.handle_geosearch(PAT, user, message, google_places)
        elif ("look" in message.lower() and user.get_location() is None):
            GoogleMapsHandler.ask_for_location(user, PAT)
        else:
            print("Not Sure how to respond.")
            data = to_json({
                "recipient": {"id": user.get_id()},
                "message": {"attachment":{
                    "type":"template",
                    "payload" : {
                        "template_type":"button",
                        "text":"Hi. Here are some of the things I can do for you!",
                        "buttons": Buttons.button_list
                    }
                }
                            }})
            messagerequestpost(PAT, data)
        return Users

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

def messaging_events(payload):
    """Generate tuples of (sender_id, message_text) from theLowCholestoralMemes
    provided payload.
    """
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]
    for event in messaging_events:
        if("message" in event and "quick_reply" in event["message"]):
            yield (event["sender"]["id"], event["message"]["quick_reply"]["payload"])
        if(event.get("postback")):
            if event["postback"]["payload"]=="Get Started":
                yield(event["sender"]["id"],"Get Started")
            else:
                yield(event["sender"]["id"],event["postback"]["payload"])
        elif "message" in event and "text" in event["message"]:
            yield(event["sender"]["id"], event["message"]["text"].encode('unicode_escape'))
        elif (str(event['message']['attachments'][0]['type']) == 'location'):
            latitude = event['message']['attachments'][0]['payload']['coordinates']['lat']
            longitude = event['message']['attachments'][0]['payload']['coordinates']['long']
            yield (event["sender"]["id"], Location(latitude, longitude))
        else:
            yield(event["sender"]["id"], "I can't echo this")


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
