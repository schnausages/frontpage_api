from flask import Flask
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import requests as req
import requests_cache
from datetime import datetime
import time

app = Flask(__name__)
CORS(app)
date = datetime.today().strftime('%Y-%m-%d')

#CACHE SETUP
requests_cache.install_cache('frontpage_cache', expire_after=3600)
requests_cache.remove_expired_responses()

#FIRESTORE
cred = credentials.Certificate("firebase-sdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def frontpage():
    frontpage_articles = {}
    frontpage_articles_list = []
    article_ref = db.collection('articles')
    ordered_ref = article_ref.order_by(u'added',direction=firestore.Query.DESCENDING)
    docs = ordered_ref.stream()
    frontpage_articles['articles'] = frontpage_articles_list
    for i in docs:
        frontpage_articles_list.append(i.to_dict())
    frontpage_articles['articles'] = frontpage_articles_list
    return frontpage_articles

@app.route('/', methods=['GET'])
def home():
    return 'frontpagenews'

@app.route('/api/frontpage',methods=['GET'])
def get_frontpage():
    return frontpage()

# @app.route('/api/newslab',methods=['GET'])
# def get_newslab():
    # full_dict = {}
    # newslab_dict = {}
    # articles_list = []
    # articles = frontpage_outlet_data['articles']
    # for i in articles:
    #     if i['outlet'] in newslab_dict:
    #         newslab_dict[i['outlet']]['biasIndexList'].append(i['biasIndex'])
    #     else:
    #         newslab_dict[i['outlet']] = {'outlet':i['outlet'],'iconImage':i['iconImage'],'biasIndexList':[i['biasIndex']]}
    # articles_list.append(newslab_dict)
    # full_dict['response'] = list(newslab_dict.values())
    # return full_dict

# @app.route('/api/newslab/outletimages', methods=['GET'])
# def get_news_lab_outlet_images():
#     articles = frontpage_outlet_data['articles']
#     icon_dict = {}
#     for i in articles:
#       if i['outlet'] in icon_dict:
#         pass
#       else:
#         icon_dict[i['outlet']] = [i['iconImage']]
#     return icon_dict

@app.route('/newsroom/trending', methods=['GET'])
def send_trending_news():
    requests_cache.remove_expired_responses()
    trending_response = req.get('http://newsapi.org/v2/top-headlines?country=us&pageSize=12&apiKey=8e5ad43b589749e8a7c76bbb04ec8ed6')
    trending_news = trending_response.json()
    return trending_news

@app.route('/newsroom/gaming', methods=['GET'])
def send_gaming_news():
    requests_cache.remove_expired_responses()
    gaming_response = req.get('http://newsapi.org/v2/everything?q=video games OR gaming OR esports&pageSize=10&sortBy=popularity&'f'from={date}&apiKey=8e5ad43b589749e8a7c76bbb04ec8ed6')
    gaming_news = gaming_response.json()
    return gaming_news

@app.route('/newsroom/socialmedia', methods=['GET'])
def send_socialmedia_news():
    requests_cache.remove_expired_responses()
    socialmedia_response = req.get('http://newsapi.org/v2/everything?q=instagram OR tiktok OR twitter OR snapchat OR youtube OR facebook OR social-media&'f'from={date}&pageSize=10&apiKey=8e5ad43b589749e8a7c76bbb04ec8ed6')
    socialmedia_news = socialmedia_response.json()
    return socialmedia_news

@app.route('/newsroom/science', methods=['GET'])
def send_science_news():
    requests_cache.remove_expired_responses()
    science_response = req.get('http://newsapi.org/v2/top-headlines?category=science&country=us&pageSize=6&apiKey=8e5ad43b589749e8a7c76bbb04ec8ed6')
    science_news = science_response.json()
    return science_news

@app.route('/newsroom/politics', methods=['GET'])
def send_politics_news():
    requests_cache.remove_expired_responses()
    politics_response = req.get('http://newsapi.org/v2/everything?q=politics OR democrats OR president trump OR trump OR pelosi OR white house OR republicans OR supreme-court &sortBy=relevancy&'f'from={date}&pageSize=10&apiKey=8e5ad43b589749e8a7c76bbb04ec8ed6')
    politics_news = politics_response.json()
    return politics_news

@app.route('/newsroom/popculture', methods=['GET'])
def send_popculture_news():
    requests_cache.remove_expired_responses()
    popculture_response = req.get('http://newsapi.org/v2/top-headlines?category=entertainment&country=us&pageSize=10&apiKey=8e5ad43b589749e8a7c76bbb04ec8ed6')
    popculture_news = popculture_response.json()
    return popculture_news

if __name__ == "__main__":
    app.run(debug = False)