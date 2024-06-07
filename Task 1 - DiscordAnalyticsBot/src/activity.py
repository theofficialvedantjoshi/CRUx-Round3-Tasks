from nltk.sentiment.vader import SentimentIntensityAnalyzer
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from config import config

creds = {
    "type": config.type,
    "project_id": config.project_id,
    "private_key_id": config.private_key_id,
    "private_key": config.private_key,
    "client_email": config.client_email,
    "client_id": config.client_id,
    "auth_uri": config.auth_uri,
    "token_uri": config.token_uri,
    "auth_provider_x509_cert_url": config.auth_provider_x509_cert_url,
    "client_x509_cert_url": config.client_x509_cert_url,
    "universe_domain": config.universe_domain,
}
cred = credentials.Certificate(creds)


class Activity:
    def __init__(self):
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.nlp = SentimentIntensityAnalyzer()

    def messages(self, server, channel, content, author, timestamp):
        db = self.db
        nlp = self.nlp
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

    def get_voice(self, server, channel, username):
        db = self.db
        user = (
            db.collection("voice")
            .where("server", "==", server)
            .where("channel", "==", channel)
            .where("username", "==", username)
            .get()
        )
        return user

    def add_voice(self, server, channel, username, last_joined, last_left, total_time):
        db = self.db
        voice = {
            "server": server,
            "channel": channel,
            "username": username,
            "last_joined": last_joined,
            "last_left": last_left,
            "total_time": total_time,
        }
        db.collection("voice").add(voice)

    def join_voice(self, user, last_joined):
        db = self.db
        for doc in user:
            doc_ref = db.collection("voice").document(doc.id)
            doc_ref.update(
                {
                    "last_joined": last_joined,
                }
            )

    def leave_voice(self, user, last_left, total_time):
        db = self.db
        for doc in user:
            doc_ref = db.collection("voice").document(doc.id)
            doc_ref.update(
                {
                    "last_left": last_left,
                    "total_time": total_time,
                }
            )

    def get_channels(self, server, name):
        db = self.db
        channels = (
            db.collection("channels")
            .where("server", "==", server)
            .where("name", "==", name)
            .get()
        )
        return channels

    def add_channels(
        self, server, name, type, messages, total_voice_time, active_users
    ):
        db = self.db
        channel = {
            "server": server,
            "name": name,
            "type": type,
            "total_messages": messages,
            "total_voice_time": total_voice_time,
            "active_users": active_users,
        }
        db.collection("channels").add(channel)

    def update_channels(self, server, name):
        db = self.db
        channel = self.get_channels(server, name)
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
                        active_users.append(
                            {"username": user, "count": users.count(user)}
                        )
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
    def delete_channel(self, server, name):
        db = self.db
        channels = (
            db.collection("channels")
            .where("server", "==", server)
            .where("name", "==", name)
            .get()
        )
        for channel in channels:
            db.collection("channels").document(channel.id).delete()

    def delete_message(self, server, channel, content, author):
        db = self.db
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
