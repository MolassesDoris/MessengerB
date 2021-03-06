from flask import Flask, request
app = Flask(__name__)
import googlemaps
from MessageHandler import *

google_places = googlemaps.Client(s.GAPI)

Users = []

PAT = s.PAT

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
    handle_message_req(request,Users)
    return("ok")

if __name__ == '__main__':
    app.run()
