from flask import Flask, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import requests as req
import requests_cache
from datetime import datetime
from newspaper import Article, Config, fulltext
from datetime import datetime, timedelta
from textblob import TextBlob
import json
import tweepy
import configparser
import time
import os
import git


app = Flask(__name__)
CORS(app)

#CACHE SETUP
date = datetime.today().strftime('%Y-%m-%d')
requests_cache.install_cache('frontpage_cache', expire_after=3600)
requests_cache.remove_expired_responses()

#FIREBASE JSON
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(THIS_FOLDER, 'firebase-sdk.json')

#FIRESTORE INIT
cred = credentials.Certificate(my_file)
firebase_admin.initialize_app(cred)
db = firestore.client()

#NEWSPAPER CONFIG HEADERS
newspaperConfig = Config()
headers = {
    "User-Agent": "Mozilla",
}
newspaperConfig.headers = headers
newspaperConfig.request_timeout = 10

config = configparser.ConfigParser()
config.read('config.ini')

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

@app.route('/update_server',methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('https://github.com/schnausages/frontpage_api.git')
        origin = repo.remotes.origin
    origin.pull()
    return 'Updated branch from GitHub Repo',200

@app.route('/api/frontpage',methods=['GET'])
def get_frontpage():
    return frontpage()

#admin dashboard article add
@app.route('/adminadd/<path:a>', methods=['GET'])
def admin_add_article(a):
    b = str(a)
    newsdata = json.loads(b)
    articleDict = {"topic":newsdata["topic"],"articles":[]}
    for eachUrl in newsdata['urls']:
    # if 'twitter.com' in eachUrl:
        # read config
        api_key = config['twitter']['api_key']
        api_key_secret = config['twitter']['api_key_secret']
        access_token = config['twitter']['access_token']
        access_token_secret = config['twitter']['access_token_secret']

        #auth app
        auth = tweepy.OAuthHandler(api_key,api_key_secret)
        auth.set_access_token(access_token,access_token_secret)
        api = tweepy.API(auth)

        #enter twitter URL here
        full_url = str(eachUrl)

        keyword = 'status/'
        after_keyword = full_url.partition(keyword)
        tweet_id = after_keyword[2]
        tweet_response = api.get_status(tweet_id,tweet_mode = "extended")
        articleDict['articles'].append(tweet_response.full_text)
        # #tweet sent analysis
        tweet_text = tweet_response.full_text
        tweet_blob = TextBlob(tweet_text)
        articleDict['articles'].append(tweet_blob.sentiment.subjectivity)

    return articleDict
    #     else:
    #         #run newspaper article analysis
    #         article = Article('https://'+eachUrl, config=config)
    #         article.download()
    #         article.parse()
    #         articleBody = article.text
    #         articleBlob = TextBlob(articleBody)
    #         biasIndex = articleBlob.sentiment.subjectivity * 1000
    #         articleDict["articles"].append({"url":eachUrl,"biasScore":biasIndex,"outet":"NEWSOUTLET"})
    # db.collection('articles').document(u'another').set(articleDict)
   # return articleDict

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

#TESTING SENTIMENT

@app.route('/feels/<posts>', methods=['GET'])
def send_feels(posts=None):
    blob = TextBlob(posts)
    feels = blob.sentiment.polarity
    if feels > 0.5:
        return {'mood':'happy','description':'You are among the happiest users on here!'}
    elif feels > 0.38:
        return {'mood':'content','description':'You seem pretty content! Definitely happier than most.'}
    elif feels >= 0.2:
        return {'mood':'sad','description':'Seems like you could be a lot happier, but you arent angry.'}
    elif feels < 0.2:
        return {'mood':'angry','description':'Your posts indicate you are in a bad mood lately.'}
    else:
        return {'mood':'ERROR','description':'SORRY ERROR'}

if __name__ == "__main__":
    app.run(debug = False)