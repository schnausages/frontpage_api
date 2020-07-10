import requests as req
import firebase_admin
from firebase_admin import credentials, firestore

class NewsGetter:
    def frontpage():
        frontpage_articles = {}
        frontpage_articles_list = []
        cred = credentials.Certificate("firebase-sdk.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        article_ref = db.collection('articles')
        ordered_ref = article_ref.order_by(u'added',direction=firestore.Query.DESCENDING)
        docs = ordered_ref.stream()
        # for i in docs:
        #     n = n+1
        #     frontpage_articles_list.append('{} => {}'.format(i.id, i.to_dict()))
        frontpage_articles['articles'] = frontpage_articles_list
        for i in docs:
            # frontpage_articles_list.append(u'{}'.format(i.to_dict()))
            frontpage_articles_list.append(i.to_dict())
        frontpage_articles['articles'] = frontpage_articles_list
        return frontpage_articles

frontpage = NewsGetter.frontpage()