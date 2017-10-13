import MessageHandler
import Quick_replies as qr
from Users import *
from Utils import *
import praw
import Secret as s

def send_message_reddit(token, recipient, text, reddit):
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
            "recipient": {"id": recipient.get_id()},
            "message": {"text": "Hi I'm MemeBot. I can send you memes, doggo pics and I can also help you look for shops etc. if you request.".encode("utf-8")}})
        MessageHandler.messagerequestpost(token, data)
    else:
        print("Unknown Subreddit.")
        data = to_json({
            "recipient": {"id": recipient},
            "message": {"text": "Unknown Meme Source."}})
        MessageHandler.messagerequestpost(token, data)

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
                          }}, "quick_replies":qr.quick_replies_list_reddit}})
        MessageHandler.messagerequestpost(token, data)