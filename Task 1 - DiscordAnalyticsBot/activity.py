from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

load_dotenv()
nlp = SentimentIntensityAnalyzer()
cred = credentials.Certificate(
    "D:\CODE\CRUx-Round3-Tasks\stattron-a881c-firebase-adminsdk-fwiky-b0a560b4ca.json"
)
firebase_admin.initialize_app(cred)


def messages(server, channel, content, author, timestamp):
    db = firestore.client()
    doc = nlp.polarity_scores(content)
    if doc["compound"] > 0.05:
        sentiment = "positive"
    elif doc["compound"] < -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    message = {
        "server": server,
        "channel": channel,
        "content": content,
        "author": author,
        "timestamp": timestamp,
        "sentiment": sentiment,
    }
    db.collection("messages").add(message)
