class Location():

    def __init__(self, longitude, latitude):
        self._longitude = longitude
        self._latitude = latitude

    def get_longitude(self):
        return self._longitude

    def get_latitude(self):
        return self._latitude

class Post():

    def __init__(self, id, url):
        self._id = id
        self._url = url

    def get_id(self):
        return self._id
    def get_url(self):
        return self._url
class User():

    def __init__(self, id):
        self._id = id
        self._posts = None
        self._location = None

    def get_id(self):
        return self._id

    def get_posts(self):
        return self._posts

    def get_location(self):
        return self._location

    def addposts(self,post):
        if(self._posts is None):
            self._posts = []
        self._posts.append(post)

    def setLocation(self,location):
        self._location = location
