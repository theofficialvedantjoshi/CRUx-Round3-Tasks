import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import discord
import seaborn as sns
from matplotlib import pyplot as plt
import io
import pandas as pd
from datetime import datetime, timedelta
from wordcloud import WordCloud, STOPWORDS
from pytz import timezone


class Response:
    def __init__(self):
        self.db = firestore.client()
        self.commands_help = [
            "overview",
            "user <hourly/daily/weekly>",
            "channel <channelname>",
            "top <n>",
            "versus <@user1> <@user2>",
            "heatmap server/<channelname> <n>",
            "trends",
            "spikes <timeframe>",
            "cloud server/<channelname>",
            "sentiment",
            "help",
        ]
        self.commands = [
            "overview",
            "user",
            "channel",
            "top",
            "versus",
            "heatmap",
            "trends",
            "spikes",
            "cloud",
            "sentiment",
            "help",
        ]
        self.timezone_region = timezone("Asia/Kolkata")

    def get_response(self, message: str) -> str:
        if message == "!stat help":
            return (
                "Commands:\n"
                + "\n".join([f"{command}" for command in self.commands])
                + "\n\nFor more information on a command, type `!stat help <command>`"
            )

        if message.startswith("!stat help"):
            command = message.split(" ")[2]
            return self.get_help(message, command)

    def get_help(self, message: str, command: str) -> str:
        if command not in self.commands:
            return f"Command {command} not found"
        if command == "overview":
            return (
                "Overview command: `!stat overview`\n"
                "Server overview which shows total messages sent, number of active users, and other relevant metrics"
            )
        elif command == "user":
            return (
                "User command: `!stat user hourly/daily/weekly`\n"
                "User specific stats that shows the number of messages sent, time spent in voice channels, and other relevant metrics for the specified user."
                " The timeframe can be hourly(for todays day), daily, or weekly."
            )
        elif command == "channel":
            return (
                "Channel command: `!stat channel <channelname>`\n"
                "Channel specific stats that shows the most active users in the channel and usage analytics"
            )
        elif command == "top":
            return (
                "Top command: `!stat top`\n"
                "List the top 10 users ranked by the number of messages sent and time spent in voice channels."
            )
        elif command == "versus":
            return (
                "Versus command: `!stat versus <user1> <user2>`\n"
                "Compare the number of messages sent and time spent in voice channels between two users."
            )
        elif command == "heatmap":
            return (
                "Heatmap command: `!stat heatmap server/<channelname> <n>`\n"
                "Generate a heatmap of message activity over the course of the last n days for the entire server or a specific channel."
            )
        elif command == "trends":
            return (
                "Trends command: `!stat trends`\n"
                "trends in server activity, such as increasing or decreasing message frequency over a specific period"
            )
        elif command == "spikes":
            return (
                "Spikes command: `!stat spikes <daily/hourly>`\n"
                "Identify spikes in message activity for a specific channel over a specific timeframe"
            )
        elif command == "cloud":
            return (
                "Cloud command: `!stat cloud server/<channelname>`\n"
                "Perform a content analysis of messages to identify common keywords and topics. Visualise these using a word cloud."
            )
        elif command == "sentiment":
            return (
                "Sentiment command: `!stat sentiment`\n"
                "Analyse and plot the sentiment of messages in that channel over time to observe changes in overall server mood."
            )
        elif command == "help":
            return (
                "Help command: `!stat help <command>`\n"
                "This command gives more information on a specific command"
            )

    def hour_to_time(self, hour):
        if hour < 12:
            return f"{hour} AM"
        elif hour == 12:
            return f"{hour} PM"
        else:
            return f"{hour-12} PM"

    def overview(self, server: str):
        db = self.db
        channels = db.collection("channels").where("server", "==", server).get()
        total_messages = 0
        total_voice_time = 0
        active_user_text = ""
        active_user_voice = ""
        active_users_text = {}
        active_users_voice = {}
        for active_user in channels[0].to_dict()["active_users"]:
            active_users_text[active_user["username"]] = active_user["count"]
        for channel in channels:
            channel = channel.to_dict()
            total_messages += channel["total_messages"]
            total_voice_time += channel["total_voice_time"]

            if "active_users" in channel:
                if channel["type"] == "text":
                    for user in channel["active_users"]:
                        if user["username"] not in active_users_text:
                            active_users_text[user["username"]] = user["count"]
                        else:
                            active_users_text[user["username"]] += user["count"]
                else:
                    for user in channel["active_users"]:
                        if user["username"] not in active_users_voice:
                            active_users_voice[user["username"]] = user["total_time"]
                        else:
                            active_users_voice[user["username"]] += user["total_time"]
        active_user_text = max(active_users_text, key=lambda x: active_users_text[x])
        active_user_voice = max(active_users_voice, key=lambda x: active_users_voice[x])
        messages = db.collection("messages").where("server", "==", server).get()
        timeseries = []
        for message in messages:
            message = message.to_dict()
            message["timestamp"] = message["timestamp"].astimezone(self.timezone_region)
            timeseries.append(message["timestamp"])
        avg_messages = total_messages / len(
            list(set([time.date() for time in timeseries]))
        )
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Server Overview",
            description=f"Total messages sent: {total_messages}\n"
            f"Total voice time: {round(total_voice_time/60,2)} mins\n"
            f"Average messages per day: {avg_messages}\n"
            f"Most active user in text channels: {active_user_text}\n"
            f"Most active user in voice channels: {active_user_voice}",
        )
        return embed

    def user(self, server: str, username: str, timeframe: str):
        db = self.db
        messages = (
            db.collection("messages")
            .where("server", "==", server)
            .where("author", "==", username)
            .get()
        )
        voice = (
            db.collection("voice")
            .where("server", "==", server)
            .where("username", "==", username)
            .get()
        )
        # plotting messages
        channels = []
        timeseries = []
        for message in messages:
            message = message.to_dict()
            channels.append(message["channel"])
            timeseries.append(message["timestamp"].astimezone(self.timezone_region))
        if timeframe == "daily":
            date = datetime.now(timezone("Asia/Kolkata")).date()
            last_week = date - timedelta(days=7)
            timeseries = [
                time.date() for time in timeseries if time.date() >= last_week
            ]
            message_data = {}
            for time in timeseries:
                if time not in [*message_data]:
                    message_data[time] = timeseries.count(time)
            messagesperday = sum([*message_data.values()]) / len([*message_data])
            plt.figure(figsize=(6, 6))
            sns.color_palette("mako", as_cmap=True)
            plot = sns.barplot(x=[*message_data], y=[*message_data.values()])
            plt.xlabel("Date")
            plt.ylabel("Messages")
            plt.title(f"Messages sent by {username}")
            plt.xticks(rotation=45)
            figure = plot.get_figure()
            buffer = io.BytesIO()
            figure.savefig(buffer, bbox_inches="tight", format="png")
            buffer.seek(0)
            image = discord.File(buffer, filename="plot.png")
            plt.clf()
            total_messages = sum([*message_data.values()])
            total_voice_time = 0
            most_active_channel = []
            for channel in channels:
                if channel not in most_active_channel:
                    most_active_channel.append([channel, channels.count(channel)])
            most_active_channel = max(most_active_channel, key=lambda x: x[1])
            for v in voice:
                v = v.to_dict()
                total_voice_time += v["total_time"]
            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"{username} Stats",
                description=f"Total messages sent: {total_messages}\n"
                f"Average messages per day: {messagesperday}\n"
                f"Total voice time: {round(total_voice_time/60,2)} mins\n"
                f"Most active channel: {most_active_channel[0]}",
            )
            embed.set_image(url="attachment://plot.png")
            return embed, image
        if timeframe == "weekly":
            timeseries = [
                "Week: " + str(time.isocalendar().week) for time in timeseries
            ]
            message_data = {}
            for time in timeseries:
                if time not in [*message_data]:
                    message_data[time] = timeseries.count(time)
            message_data = dict(
                sorted(message_data.items(), key=lambda x: int(x[0].split()[1]))
            )
            messagesperweek = sum([*message_data.values()]) / len([*message_data])
            plt.figure(figsize=(6, 6))
            sns.color_palette("mako", as_cmap=True)
            plot = sns.barplot(x=[*message_data], y=[*message_data.values()])
            plt.xlabel("Week")
            plt.ylabel("Messages")
            plt.title(f"Messages sent by {username}")
            plt.xticks(rotation=45)
            figure = plot.get_figure()
            buffer = io.BytesIO()
            figure.savefig(buffer, bbox_inches="tight", format="png")
            buffer.seek(0)
            image = discord.File(buffer, filename="plot.png")
            plt.clf()
            total_messages = sum([*message_data.values()])
            total_voice_time = 0
            most_active_channel = []
            for channel in channels:
                if channel not in most_active_channel:
                    most_active_channel.append([channel, channels.count(channel)])
            most_active_channel = max(most_active_channel, key=lambda x: x[1])
            for v in voice:
                v = v.to_dict()
                total_voice_time += v["total_time"]
            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"{username} Stats",
                description=f"Total messages sent: {total_messages}\n"
                f"Average messages per week: {messagesperweek}\n"
                f"Total voice time: {round(total_voice_time/60,2)} mins\n"
                f"Most active channel: {most_active_channel[0]}",
            )
            embed.set_image(url="attachment://plot.png")
            return embed, image
        if timeframe == "hourly":
            today = datetime.now(timezone("Asia/Kolkata")).date()
            timeseries = [
                str(time.hour) + ":00" for time in timeseries if time.date() == today
            ]
            message_data = {}
            for time in timeseries:
                if time not in [*message_data]:
                    message_data[time] = timeseries.count(time)
            messagesperhour = sum([*message_data.values()]) / len([*message_data])
            plt.figure(figsize=(6, 6))
            sns.color_palette("mako", as_cmap=True)
            plot = sns.barplot(x=[*message_data], y=[*message_data.values()])
            plt.xlabel("Hour")
            plt.ylabel("Messages")
            plt.title(f"Messages sent by {username}")
            plt.xticks(rotation=45)
            figure = plot.get_figure()
            buffer = io.BytesIO()
            figure.savefig(buffer, bbox_inches="tight", format="png")
            buffer.seek(0)
            image = discord.File(buffer, filename="plot.png")
            plt.clf()
            total_messages = sum([*message_data.values()])
            total_voice_time = 0
            most_active_channel = []
            for channel in channels:
                if channel not in most_active_channel:
                    most_active_channel.append([channel, channels.count(channel)])
            most_active_channel = max(most_active_channel, key=lambda x: x[1])
            for v in voice:
                v = v.to_dict()
                total_voice_time += v["total_time"]
            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"{username} Stats",
                description=f"Total messages sent: {total_messages}\n"
                f"Average messages per hour: {messagesperhour}\n"
                f"Total voice time: {round(total_voice_time/60,2)} mins\n"
                f"Most active channel: {most_active_channel[0]}",
            )
            embed.set_image(url="attachment://plot.png")
            return embed, image

    def channel_stats(self, server, name):
        db = self.db
        channels = (
            db.collection("channels")
            .where("server", "==", server)
            .where("name", "==", name)
            .get()
        )
        total_messages = 0
        total_voice_time = 0
        active_users = []
        for channel in channels:
            channel = channel.to_dict()
            total_messages += channel["total_messages"]
            total_voice_time += channel["total_voice_time"]
            active_users = channel["active_users"]
        if channels[0].to_dict()["type"] == "text":
            messages = (
                db.collection("messages")
                .where("server", "==", server)
                .where("channel", "==", name)
                .get()
            )
            timeseries = []
            for message in messages:
                message = message.to_dict()
                timeseries.append(message["timestamp"].astimezone(self.timezone_region))
            avg_messages = total_messages / len(
                list(set([time.date() for time in timeseries]))
            )
            message_data = {}
            timeseries = [time.date() for time in timeseries]
            for time in timeseries:
                if time not in [*message_data]:
                    message_data[time] = timeseries.count(time)
            sns.color_palette("mako", as_cmap=True)
            plot = sns.scatterplot(x=[*message_data], y=[*message_data.values()])
            plt.xlabel("Date")
            plt.ylabel("Messages")
            plt.title(f"Messages sent in {name}")
            plt.xticks(rotation=45)
            figure = plot.get_figure()
            buffer = io.BytesIO()
            figure.savefig(buffer, bbox_inches="tight", format="png")
            buffer.seek(0)
            image = discord.File(buffer, filename="plot.png")
            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"{name} Stats",
                description=f"Total messages sent: {total_messages}\n"
                f"Average messages per day: {avg_messages}\n"
                f"Active users: {', '.join([user['username'] for user in active_users])}",
            )
            return embed, image
        else:
            voice = (
                db.collection("voice")
                .where("server", "==", server)
                .where("channel", "==", name)
                .get()
            )
            total_voice_time = 0
            for v in voice:
                v = v.to_dict()
                total_voice_time += v["total_time"]
            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"{name} Stats",
                description=f"Total voice time: {round(total_voice_time/60,2)} mins\n"
                f"Active users: {', '.join([user['username'] for user in active_users])}",
            )
            return embed, None

    def word_cloud(self, server, tag):
        db = self.db
        if tag == "server":
            messages = db.collection("messages").where("server", "==", server).get()
        else:
            messages = (
                db.collection("messages")
                .where("server", "==", server)
                .where("channel", "==", tag)
                .get()
            )
        text = ""
        for message in messages:
            message = message.to_dict()
            text += message["content"] + " "
        stopwords = set(STOPWORDS)
        wordcloud = WordCloud(
            width=800,
            height=800,
            background_color="black",
            stopwords=stopwords,
            min_font_size=10,
        ).generate(text)
        plt.figure(figsize=(6, 6), facecolor=None)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.tight_layout(pad=0)
        buff = io.BytesIO()
        plt.savefig(buff, bbox_inches="tight", format="png")
        buff.seek(0)
        image = discord.File(buff, filename="wordcloud.png")
        return image

    def sentiment_analysis(self, server, channel):
        db = self.db
        messages = (
            db.collection("messages")
            .where("server", "==", server)
            .where("channel", "==", channel)
            .get()
        )
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        hours = [self.hour_to_time(x) for x in range(24)]
        sentiment_score = {hour: 0 for hour in hours}
        for message in messages:
            message = message.to_dict()
            sentiments[message["sentiment"]] += 1
            message["timestamp"] = message["timestamp"].astimezone(self.timezone_region)
            if (
                message["timestamp"].date()
                == datetime.now(timezone("Asia/Kolkata")).date()
            ):
                sentiment_score[
                    self.hour_to_time(message["timestamp"].hour)
                ] += message["sentiment_score"]
        # pie chart
        labels = sentiments.keys()
        sizes = sentiments.values()
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct="%1.1f%%", shadow=True, startangle=90)
        ax1.title.set_text("Sentiment Analysis of all messages")
        ax1.axis("equal")
        buff = io.BytesIO()
        plt.savefig(buff, bbox_inches="tight", format="png")
        buff.seek(0)
        image1 = discord.File(buff, filename="sentiment.png")
        plt.clf()
        # line graph
        sns.color_palette("mako", as_cmap=True)
        plot = sns.lineplot(x=[*sentiment_score], y=[*sentiment_score.values()])
        plot.set(xlabel="Hour", ylabel="Sentiment Score")
        plot.set_xticklabels(labels=hours, rotation=45)
        plot.set_title("Sentiment Score over the course of the day")
        buff = io.BytesIO()
        plot.get_figure().savefig(buff, bbox_inches="tight", format="png")
        buff.seek(0)
        image2 = discord.File(buff, filename="sentiment_score.png")
        return image1, image2

    def generate_heatmap(self, server, tag, n):
        db = self.db
        if tag == "server":
            messages = db.collection("messages").where("server", "==", server).get()
        else:
            messages = (
                db.collection("messages")
                .where("server", "==", server)
                .where("channel", "==", tag)
                .get()
            )
        dates = []
        hours = []
        date = datetime.now(timezone("Asia/Kolkata")).date()
        last_date = date - timedelta(days=n)
        for message in messages:
            message = message.to_dict()
            message["timestamp"] = message["timestamp"].astimezone(self.timezone_region)
            if message["timestamp"].date() >= last_date:
                dates.append(message["timestamp"].date())
                hours.append(self.hour_to_time(message["timestamp"].hour))
        df = pd.DataFrame({"date": dates, "hour": hours})
        df["date"] = df["date"].apply(lambda x: x.strftime(r"%Y-%m-%d"))
        sns.color_palette("mako", as_cmap=True)
        sns.heatmap(df.groupby(["date", "hour"]).size().unstack(), cmap="coolwarm")
        plt.title("Message Heatmap")
        plt.xlabel("Hour")
        plt.ylabel("Date")
        buff = io.BytesIO()
        plt.savefig(buff, bbox_inches="tight", format="png")
        buff.seek(0)
        image = discord.File(buff, filename="heatmap.png")
        return image

    def versus(self, server, user1, user2):
        db = self.db
        messages1 = (
            db.collection("messages")
            .where("server", "==", server)
            .where("author", "==", user1)
            .get()
        )
        messages2 = (
            db.collection("messages")
            .where("server", "==", server)
            .where("author", "==", user2)
            .get()
        )
        voice1 = (
            db.collection("voice")
            .where("server", "==", server)
            .where("username", "==", user1)
            .get()
        )
        voice2 = (
            db.collection("voice")
            .where("server", "==", server)
            .where("username", "==", user2)
            .get()
        )
        # plotting messages
        channels1 = []
        timeseries1 = []
        for message in messages1:
            message = message.to_dict()
            channels1.append(message["channel"])
            timeseries1.append(message["timestamp"].astimezone(self.timezone_region))
        channels2 = []
        timeseries2 = []
        for message in messages2:
            message = message.to_dict()
            channels2.append(message["channel"])
            timeseries2.append(message["timestamp"].astimezone(self.timezone_region))
        message_data1 = {}
        timeseries1 = [time.date() for time in timeseries1]
        for time in timeseries1:
            if time not in [*message_data1]:
                message_data1[time] = timeseries1.count(time)
        message_data2 = {}
        timeseries2 = [time.date() for time in timeseries2]
        for time in timeseries2:
            if time not in [*message_data2]:
                message_data2[time] = timeseries2.count(time)
        plt.figure(figsize=(6, 6))
        sns.color_palette("mako", as_cmap=True)
        plot = sns.lineplot(
            x=[*message_data1], y=[*message_data1.values()], label=user1
        )
        plot = sns.lineplot(
            x=[*message_data2], y=[*message_data2.values()], label=user2
        )
        plt.xlabel("Date")
        plt.ylabel("Messages")
        plt.title(f"Messages sent by {user1} and {user2}")
        plt.xticks(rotation=45)
        figure = plot.get_figure()
        buffer = io.BytesIO()
        figure.savefig(buffer, bbox_inches="tight", format="png")
        buffer.seek(0)
        image = discord.File(buffer, filename="plot.png")
        plt.clf()
        total_messages1 = sum([*message_data1.values()])
        total_messages2 = sum([*message_data2.values()])
        total_voice_time1 = 0
        total_voice_time2 = 0
        most_active_channel1 = []
        for channel in channels1:
            if channel not in most_active_channel1:
                most_active_channel1.append([channel, channels1.count(channel)])
        most_active_channel1 = max(most_active_channel1, key=lambda x: x[1])
        most_active_channel2 = []
        for channel in channels2:
            if channel not in most_active_channel2:
                most_active_channel2.append([channel, channels2.count(channel)])
        most_active_channel2 = max(most_active_channel2, key=lambda x: x[1])
        for v in voice1:
            v = v.to_dict()
            total_voice_time1 += v["total_time"]
        for v in voice2:
            v = v.to_dict()
            total_voice_time2 += v["total_time"]
        embed = discord.Embed(
            color=discord.Color.blue(),
            title=f"{user1} vs {user2} Stats",
            description=f"Total messages sent by {user1}: {total_messages1}\n"
            f"Total messages sent by {user2}: {total_messages2}\n"
            f"Total voice time by {user1}: {round(total_voice_time1/60,2)} mins\n"
            f"Total voice time by {user2}: {round(total_voice_time2/60,2)} mins\n"
            f"Most active channel for {user1}: {most_active_channel1[0]}\n"
            f"Most active channel for {user2}: {most_active_channel2[0]}",
        )
        embed.set_image(url="attachment://plot.png")
        return embed, image

    def top_users(self, server, n):
        db = self.db
        messages = db.collection("messages").where("server", "==", server).get()
        voice = db.collection("voice").where("server", "==", server).get()
        users = []
        for message in messages:
            message = message.to_dict()
            users.append(message["author"])
        user_data = {}
        for user in users:
            if user not in [*user_data]:
                user_data[user] = users.count(user)
        voice_data = {}
        for v in voice:
            v = v.to_dict()
            if v["username"] not in [*voice_data]:
                voice_data[v["username"]] = v["total_time"]
        if not voice_data:
            top_voice = [{"User": "No data", "Voice Time": 0}]
        else:
            top_voice = sorted(voice_data.items(), key=lambda x: x[1], reverse=True)
        top_users = sorted(user_data.items(), key=lambda x: x[1], reverse=True)
        df_messages = pd.DataFrame(top_users, columns=["User", "Messages"])
        df_voice = pd.DataFrame(top_voice, columns=["User", "Voice Time"])
        table = pd.plotting.table
        fig, ax = plt.subplots(2, 1, figsize=(10, 8))
        ax[0].axis("off")
        tbl1 = ax[0].table(
            cellText=df_messages.values,
            colLabels=df_messages.columns,
            loc="center",
            cellLoc="center",
        )
        tbl1.auto_set_font_size(False)
        tbl1.set_fontsize(10)
        tbl1.scale(1.2, 1.2)
        for i in range(len(df_messages)):
            color = "lightgrey" if i % 2 == 0 else "white"
            for j in range(len(df_messages.columns)):
                tbl1[(i + 1, j)].set_facecolor(color)
        for j in range(len(df_messages.columns)):
            tbl1[(0, j)].set_facecolor("lightblue")
        ax[0].set_title("Top Users by Messages", fontsize=14, weight="bold")

        ax[1].axis("off")
        tbl2 = ax[1].table(
            cellText=df_voice.values,
            colLabels=df_voice.columns,
            loc="center",
            cellLoc="center",
        )
        tbl2.auto_set_font_size(False)
        tbl2.set_fontsize(10)
        tbl2.scale(1.2, 1.2)
        for i in range(len(df_voice)):
            color = "lightgrey" if i % 2 == 0 else "white"
            for j in range(len(df_voice.columns)):
                tbl2[(i + 1, j)].set_facecolor(color)
        for j in range(len(df_voice.columns)):
            tbl2[(0, j)].set_facecolor("lightblue")
        ax[1].set_title("Top Users by Voice Time", fontsize=14, weight="bold")

        buff = io.BytesIO()
        plt.savefig(buff, bbox_inches="tight", format="png")
        buff.seek(0)

        image = discord.File(buff, filename="top_users.png")
        plt.clf()

        return image

    def get_trends(self, server):
        db = self.db
        messages = db.collection("messages").where("server", "==", server).get()
        date = datetime.now(timezone("Asia/Kolkata")).date()
        last_week = date - timedelta(days=7)
        # group messages day wise in a week
        messages_data = {}
        for message in messages:
            message = message.to_dict()
            message["timestamp"] = message["timestamp"].astimezone(self.timezone_region)
            if message["timestamp"].date() >= last_week:
                if message["timestamp"].date() not in [*messages_data]:
                    messages_data[message["timestamp"].date()] = 1
                else:
                    messages_data[message["timestamp"].date()] += 1
        max_day = max(messages_data, key=lambda x: messages_data[x])
        max_day_messages = messages_data[max_day]
        min_day = min(messages_data, key=lambda x: messages_data[x])
        min_day_messages = messages_data[min_day]
        df = pd.DataFrame(messages_data.items(), columns=["Date", "Messages"])
        df["Date"] = df["Date"].apply(lambda x: x.strftime(r"%Y-%m-%d"))
        df["SMA"] = df["Messages"].rolling(window=2).mean()
        plt.figure(figsize=(6, 6))
        sns.color_palette("mako", as_cmap=True)
        plot = sns.lineplot(x="Date", y="Messages", data=df, label="Messages")
        plot = sns.lineplot(x="Date", y="SMA", data=df, label="SMA")
        plt.xlabel("Date")
        plt.ylabel("Messages")
        plt.title("Messages sent over the week")
        plt.xticks(rotation=45)
        figure = plot.get_figure()
        buffer = io.BytesIO()
        figure.savefig(buffer, bbox_inches="tight", format="png")
        buffer.seek(0)
        image1 = discord.File(buffer, filename="plot.png")
        plt.clf()
        current_date = datetime.now().date()
        print
        messages_data = {}
        for message in messages:
            message = message.to_dict()
            message["timestamp"] = message["timestamp"].astimezone(self.timezone_region)
            if message["timestamp"].date() == current_date:
                print(message["timestamp"].hour)
                if self.hour_to_time(message["timestamp"].hour) not in [*messages_data]:
                    messages_data[self.hour_to_time(message["timestamp"].hour)] = 1
                else:
                    messages_data[self.hour_to_time(message["timestamp"].hour)] += 1
        max_hour = max(messages_data, key=lambda x: messages_data[x])
        max_hour_messages = messages_data[max_hour]
        min_hour = min(messages_data, key=lambda x: messages_data[x])
        min_hour_messages = messages_data[min_hour]
        df = pd.DataFrame(messages_data.items(), columns=["Hour", "Messages"])
        df["SMA"] = df["Messages"].rolling(window=3).mean()
        plt.figure(figsize=(6, 6))
        sns.color_palette("mako", as_cmap=True)
        plot = sns.lineplot(x="Hour", y="Messages", data=df, label="Messages")
        plot = sns.lineplot(x="Hour", y="SMA", data=df, label="SMA")
        plt.xlabel("Hour")
        plt.ylabel("Messages")
        plt.title("Messages sent over the day")
        plt.xticks(rotation=45)
        figure = plot.get_figure()
        buffer = io.BytesIO()
        figure.savefig(buffer, bbox_inches="tight", format="png")
        buffer.seek(0)
        image2 = discord.File(buffer, filename="plot.png")
        plt.clf()
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Trends",
            description=f"Most active day: {max_day} with {max_day_messages} messages\n"
            f"Least active day: {min_day} with {min_day_messages} messages\n"
            f"Most active hour today: {max_hour} with {max_hour_messages} messages\n"
            f"Least active hour today: {min_hour} with {min_hour_messages} messages",
        )
        return embed, image1, image2

    def get_spikes(self, server, channel, timeframe):
        db = self.db
        channels = db.collection("channels").where("server", "==", server).get()
        text_channels = []
        voice_channels = []
        for channel in channels:
            channel = channel.to_dict()
            if channel["type"] == "text":
                text_channels.append(channel["name"])
        if timeframe == "daily":
            for channel in text_channels:
                date = datetime.now(timezone("Asia/Kolkata")).date()
                last_week = date - timedelta(days=7)
                messages = (
                    db.collection("messages")
                    .where("server", "==", server)
                    .where("channel", "==", channel)
                    .get()
                )
                messages_data = {}
                for message in messages:
                    message = message.to_dict()
                    message["timestamp"] = message["timestamp"].astimezone(
                        self.timezone_region
                    )
                    if message["timestamp"].date() >= last_week:
                        if message["timestamp"].date() not in [*messages_data]:
                            messages_data[message["timestamp"].date()] = 1
                        else:
                            messages_data[message["timestamp"].date()] += 1
                print(messages_data)
                df = pd.DataFrame(messages_data.items(), columns=["Date", "Messages"])
                df["Date"] = df["Date"].apply(lambda x: x.strftime(r"%Y-%m-%d"))
                average = df["Messages"].mean()
                std = df["Messages"].std()
                threshold = 2 * std
                spikes = df[df["Messages"] > threshold]
                if spikes.empty:
                    return "No spikes found"
                plt.figure(figsize=(6, 6))
                sns.color_palette("mako", as_cmap=True)
                plot = sns.lineplot(x="Date", y="Messages", data=df, label="Messages")
                plot = sns.scatterplot(x="Date", y="Messages", data=spikes, color="red")
                plt.xlabel("Date")
                plt.ylabel("Messages")
                plt.title(f"Message spikes in {channel}")
                plt.xticks(rotation=45)
                figure = plot.get_figure()
                buffer = io.BytesIO()
                figure.savefig(buffer, bbox_inches="tight", format="png")
                buffer.seek(0)
                image = discord.File(buffer, filename="plot.png")
                plt.clf()
                return image
        if timeframe == "hourly":
            today = datetime.now(timezone("Asia/Kolkata")).date()
            for channel in text_channels:
                messages = (
                    db.collection("messages")
                    .where("server", "==", server)
                    .where("channel", "==", channel)
                    .get()
                )
                messages_data = {}
                for message in messages:
                    message = message.to_dict()
                    message["timestamp"] = message["timestamp"].astimezone(
                        self.timezone_region
                    )
                    if message["timestamp"].date() == today:
                        if self.hour_to_time(message["timestamp"].hour) not in [
                            *messages_data
                        ]:
                            messages_data[
                                self.hour_to_time(message["timestamp"].hour)
                            ] = 1
                        else:
                            messages_data[
                                self.hour_to_time(message["timestamp"].hour)
                            ] += 1
                df = pd.DataFrame(messages_data.items(), columns=["Hour", "Messages"])
                average = df["Messages"].mean()
                std = df["Messages"].std()
                threshold = 3 * std
                spikes = df[df["Messages"] > average + threshold]
                if spikes.empty:
                    return "No spikes found"
                plt.figure(figsize=(6, 6))
                sns.color_palette("mako", as_cmap=True)
                plot = sns.lineplot(x="Hour", y="Messages", data=df, label="Messages")
                plot = sns.scatterplot(x="Hour", y="Messages", data=spikes, color="red")
                plt.xlabel("Hour")
                plt.ylabel("Messages")
                plt.title(f"Message spikes in {channel}")
                plt.xticks(rotation=45)
                figure = plot.get_figure()
                buffer = io.BytesIO()
                figure.savefig(buffer, bbox_inches="tight", format="png")
                buffer.seek(0)
                image = discord.File(buffer, filename="plot.png")
                plt.clf()
                return image
