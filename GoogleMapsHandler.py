from Utils import to_json
import MessageHandler
import googlemaps
import json
import Secret as s
from nltk import pos_tag, word_tokenize

google_places = googlemaps.Client(s.GAPI)

def handle_location(token, user, location):
    user.setLocation(location)
    data = to_json({
        "recipient": {"id": user.get_id()},
        "message": {"text": "Updated Location."}})
    MessageHandler.messagerequestpost(token, data)

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

    MessageHandler.messagerequestpost(token, data)

def ask_for_location(user, token):
    data = to_json({
        "recipient": {"id": user.get_id()},
        "message": {"text": "I'd love to help you look. Could you send me a location?"}})
    MessageHandler.messagerequestpost(token, data)