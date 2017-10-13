import json
import googlemaps
from nltk import pos_tag, word_tokenize
import MessageHandler
import Secret as s
from Utils import to_json
from googlemaps import places as google_places
import Quick_replies as qr
def handle_location(token, user, location):
    user.setLocation(location)
    data = to_json({
        "recipient": {"id": user.get_id()},
        "message": {"text": "Updated Location. What is it you are looking for?",
                    "quick_replies" : qr.quick_replies_list_smaps
                    }})
    MessageHandler.messagerequestpost(token, data)

def handle_geosearch(token, recipient, text, client, amttodisplay = 3):
    search_words= " ".join([tok for tok, pos in pos_tag(word_tokenize(text)) if pos.startswith('N') or pos.startswith('J')])

    query_result = client.nearby_search(
        location='{},{}'.format(recipient.get_location().get_longitude(),
                                recipient.get_location().get_latitude()),
        keyword=search_words, rankby="distance")

    if len(query_result.places) > 0:
        elements = []
        for indx, place in enumerate(query_result.places[:amttodisplay]):
            image_url = None
            if (len(place.photos) > 0):
                photo = place.photos[0]
                photo.get(maxheight=500, maxwidth=500)
                image_url = photo.url
            element = {"title": place.name.encode('utf-8'),
                       "image_url": image_url,
                       "subtitle": ", ".join([type.replace("_"," ")for type in place.types]),
                       "buttons": [{"title": "Open in Maps",
                                    "type": "web_url",
                                    "url": place.url,
                                    "messenger_extensions": 'true',
                                    "webview_height_ratio": "tall",
                                    }]}
            element = json.dumps(element)
            elements.append(element)
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

    MessageHandler.messagerequestpost(token, data)

def ask_for_location(user, token):
    data = to_json({
        "recipient": {"id": user.get_id()},
        "message": {"text": "I'd love to help you look. Could you send me a location?",
                    "quick_replies":[
      {
        "content_type":"location"
      }]}})
    MessageHandler.messagerequestpost(token, data)