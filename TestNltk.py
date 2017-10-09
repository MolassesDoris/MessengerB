# from geopy.geocoders import Nominatim
#
# geolocator = Nominatim()
# location = geolocator.geocode("Peter's street, cork")
# print(location)
# [
#           {
#             "title": "Classic T-Shirt Collection",
#             "subtitle": "See all our colors",
#             "image_url": "https://peterssendreceiveapp.ngrok.io/img/collection.png",
#             "buttons": [
#               {
#                 "title": "View",
#                 "type": "web_url",
#                 "url": "https://peterssendreceiveapp.ngrok.io/collection",
#                 "messenger_extensions": true,
#                 "webview_height_ratio": "tall",
#                 "fallback_url": "https://peterssendreceiveapp.ngrok.io/"
#               }
#             ]
#           },
#           {
#             "title": "Classic White T-Shirt",
#             "subtitle": "See all our colors",
#             "default_action": {
#               "type": "web_url",
#               "url": "https://peterssendreceiveapp.ngrok.io/view?item=100",
#               "messenger_extensions": true,
#               "webview_height_ratio": "tall",
#               "fallback_url": "https://peterssendreceiveapp.ngrok.io/"
#             }
#           },
#           {
#             "title": "Classic Blue T-Shirt",
#             "image_url": "https://peterssendreceiveapp.ngrok.io/img/blue-t-shirt.png",
#             "subtitle": "100% Cotton, 200% Comfortable",
#             "default_action": {
#               "type": "web_url",
#               "url": "https://peterssendreceiveapp.ngrok.io/view?item=101",
#               "messenger_extensions": true,
#               "webview_height_ratio": "tall",
#               "fallback_url": "https://peterssendreceiveapp.ngrok.io/"
#             },
#             "buttons": [
#               {
#                 "title": "Shop Now",
#                 "type": "web_url",
#                 "url": "https://peterssendreceiveapp.ngrok.io/shop?item=101",
#                 "messenger_extensions": true,
#                 "webview_height_ratio": "tall",
#                 "fallback_url": "https://peterssendreceiveapp.ngrok.io/"
#               }
#             ]
#           }
#         ]

from googleplaces import GooglePlaces
import Secret as s
google_places = GooglePlaces(s.GAPI)
import json
query_result = google_places.nearby_search(
            location='{}'.format("Cork city"),radius=3200, keyword="Clothes Shops")
elements = []
for place in query_result.places:
    place.get_details()
    element = {"title": str(place.name),
    "image_url": place._icon,
    "buttons": [{"title": "Open in Maps","type": "web_url","url": place.url,"messenger_extensions": 'true',"webview_height_ratio": "tall","fallback_url": place.website}]}
    element = str(element)
    elements.append(element)


print(elements)
    # title = str(place.name)
    # image_url = place._icon
    # type = "web_url"
    # url = place.website
    # mapsurl = place.url

#
# for res in query_result:
#     print(res)