from datetime import datetime
from dotenv import load_dotenv
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import io

load_dotenv()
nlp = SentimentIntensityAnalyzer()
creds = {
    "type": os.getenv("type"),
    "project_id": os.getenv("project_id"),
    "private_key_id": os.getenv("private_key_id"),
    "private_key": os.getenv("private_key"),
    "client_email": os.getenv("client_email"),
    "client_id": os.getenv("client_id"),
    "auth_uri": os.getenv("auth_uri"),
    "token_uri": os.getenv("token_uri"),
    "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
    "client_x509_cert_url": os.getenv("client_x509_cert_url"),
    "universe_domain": os.getenv("universe_domain"),
}
cred = credentials.Certificate(creds)
firebase_admin.initialize_app(cred)


def messages(server, channel, content, author, timestamp):
    db = firestore.client()
    doc = nlp.polarity_scores(content)
    if doc["compound"] > 0.005:
        sentiment = "positive"
    elif doc["compound"] < -0.005:
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
        "sentiment_score": doc["compound"],
    }
    db.collection("messages").add(message)


def get_voice(server, channel, username):
    db = firestore.client()
    user = (
        db.collection("voice")
        .where("server", "==", server)
        .where("channel", "==", channel)
        .where("username", "==", username)
        .get()
    )
    return user


def add_voice(server, channel, username, last_joined, last_left, total_time):
    db = firestore.client()
    voice = {
        "server": server,
        "channel": channel,
        "username": username,
        "last_joined": last_joined,
        "last_left": last_left,
        "total_time": total_time,
    }
    db.collection("voice").add(voice)


def join_voice(user, last_joined):
    db = firestore.client()
    for doc in user:
        doc_ref = db.collection("voice").document(doc.id)
        doc_ref.update(
            {
                "last_joined": last_joined,
            }
        )


def leave_voice(user, last_left, total_time):
    db = firestore.client()
    for doc in user:
        doc_ref = db.collection("voice").document(doc.id)
        doc_ref.update(
            {
                "last_left": last_left,
                "total_time": total_time,
            }
        )


def get_channels(server, name):
    db = firestore.client()
    channels = (
        db.collection("channels")
        .where("server", "==", server)
        .where("name", "==", name)
        .get()
    )
    return channels


def add_channels(server, name, type, messages, total_voice_time, active_users):
    db = firestore.client()
    channel = {
        "server": server,
        "name": name,
        "type": type,
        "total_messages": messages,
        "total_voice_time": total_voice_time,
        "active_users": active_users,
    }
    db.collection("channels").add(channel)


def update_channels(server, name):
    db = firestore.client()
    channel = get_channels(server, name)
    users = []
    active_users = []
    for doc in channel:
        if doc.to_dict()["type"] == "text":
            messages = db.collection("messages").get()
            total_messages = 0
            for message in messages:
                users.append(message.to_dict()["author"])
                if message.to_dict()["channel"] == name:
                    total_messages += 1
            for user in users:
                if user not in [i["username"] for i in active_users]:
                    active_users.append({"username": user, "count": users.count(user)})
            doc_ref = db.collection("channels").document(doc.id)
            doc_ref.update(
                {
                    "total_messages": total_messages,
                    "active_users": active_users,
                }
            )
            print("updated")
        else:
            voice = db.collection("voice").get()
            total_voice_time = 0
            for user in voice:
                if user.to_dict()["channel"] == name:
                    total_voice_time += user.to_dict()["total_time"]
            for user in voice:
                if user.to_dict()["channel"] == name:
                    if user.to_dict()["username"] not in [
                        i["username"] for i in active_users
                    ]:
                        active_users.append(
                            {
                                "username": user.to_dict()["username"],
                                "total_time": user.to_dict()["total_time"],
                            }
                        )
            doc_ref = db.collection("channels").document(doc.id)
            doc_ref.update(
                {
                    "total_voice_time": total_voice_time,
                    "active_users": active_users,
                }
            )
            print("updated")


# Deletions
def delete_channel(server, name):
    db = firestore.client()
    channels = (
        db.collection("channels")
        .where("server", "==", server)
        .where("name", "==", name)
        .get()
    )
    for channel in channels:
        db.collection("channels").document(channel.id).delete()


def delete_message(server, channel, content, author):
    db = firestore.client()
    messages = (
        db.collection("messages")
        .where("server", "==", server)
        .where("channel", "==", channel)
        .where("content", "==", content)
        .where("author", "==", author)
        .get()
    )
    for message in messages:
        db.collection("messages").document(message.id).delete()
