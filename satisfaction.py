import datetime
import urllib
import json

__all__ = ['Company']

API_URL = "http://api.getsatisfaction.com"

URLS = {
    "overview":"/companies/%(name)s.json",
    "products":"/companies/%(name)s/products.json",
    "topics":"/companies/%(name)s/topics.json",
    "people":"/companies/%(name)s/people.json",
    "topic":"/topics/%(topic_id)s.json",
    "replies":"/topics/%(topic_id)s/replies.json",
}

GENRES = ["question","idea","problem","praise"]

class ResourceNotAvailable(RuntimeError):
    pass

def fetch_json(url):
    response = urllib.urlopen(url)
    if response.headers.getheader('status') == '404':
        raise ResourceNotAvailable(url)
    return json.load(response)

class User():
    def __init__(self, user):
        pass

class Topic():
    def __init__(self, topic):
        self.last_mod = topic["last_active_at"]
        self.author = User(topic["author"])
        self.genre = topic["style"]
        self.title = topic["subject"]
        self.content = topic["content"]
        self.me2 = topic["me_too_count"]
        self.status = topic["status"]
        self.topic_id = topic["id"]
        self.url = topic["at_sfn"]

class Reply():
    def __init__(self, reply):
        self.author = reply["author"]["canonical_name"]
        self.created = datetime.datetime.strptime(reply["created_at"][:-6],"%Y/%m/%d %H:%M:%S")
        self.content = reply["content"]

class Product():
    def __init__(self, product):
        self.name = product["name"]
        self.url = product["url"]
        self.product_id = product["ud"]
        self.description = product["description"]

class Company():
    def __init__(self, name):
        self.name = name
        self.overview_url = API_URL + URLS["overview"] % {"name" : name}
        self.overview = fetch_json(self.overview_url)
        self.products = {}
        self.topics = {}
        self.topic_counts = {}

    @classmethod
    def parse_replies(cls, replies):
        return map(Reply, replies["data"])

    def _parse_products(self, products):
        for p in products["data"]:
            self.products[p["name"]] = Product(p)

    def _parse_topics(self, genre, topics):
        self.topic_counts[genre] = topics["total"]
        self.topics[genre] = map(Topic,topics["data"])

    def get_products(self):
        self.product_url = API_URL + URLS["products"] % {"name" : self.name}
        self._parse_products(fetch_json(self.product_url))
    
    def get_topics(self, refresh = False, genre = None, page = 0):
        if genre is not None and (not genre in self.topics or refresh):
            genre_url = "%(base)s%(topic_url)s?style=%(genre)s&sort=most_me_toos&status=none,pending,active" % ({
                "base":API_URL,
                "topic_url":URLS["topics"] % {"name":self.name},
                "genre":genre,
            })
            self._parse_topics(genre, fetch_json(genre_url))
            return
        for genre in GENRES:
            genre_url = "%(base)s%(topic_url)s?style=%(genre)s&sort=most_me_toos&status=none,pending,active" % ({
                "base":API_URL,
                "topic_url":URLS["topics"] % {"name":self.name},
                "genre":genre,
            })
            self._parse_topics(genre, fetch_json(genre_url))

    def get_people(self):
        self.people_url = API_URL + URLS["people"] % {"name" : self.name}
        self.people = fetch_json(self.people_url)

    # this function is pretty pointless as it returns no more data on each product
    # than the get_products function.  However, it's here in case get_satisfaction
    # add more info that is only provided via this url
    def get_product(self, product_name, refresh = False):
        if len(self.products) == 0: # make sure we have the product overviews
            self.get_products()
        if "data" in self.products[product_name] and not refresh:
            return # we already have the product data and don't want to force refresh
        url = "%s.json" % self.products[product_name].url
        self.products[product_name].data = fetch_json(url)

    def get_topics_by_genre(self, genre):
        return self.topics[genre]

    @classmethod
    def get_topic(cls, topic_id):
        url = "%(base)s%(topic_url)s" % ({
            "base":API_URL,
            "topic_url":URLS["topic"] % {"topic_id":topic_id},
        })
        replies_url = "%(base)s%(topic_url)s" % ({
            "base":API_URL,
            "topic_url":URLS["replies"] % {"topic_id":topic_id},
            })
        res = {
            "topic" : Topic(fetch_json(url)),
            "replies" : cls.parse_replies(fetch_json(replies_url))
        }
        return res
