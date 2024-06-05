import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import discord
import seaborn as sns
from matplotlib import pyplot as plt
import io
import pandas as pd
from datetime import datetime
from wordcloud import WordCloud, STOPWORDS
from pytz import timezone

# cred = credentials.Certificate(
#     "D:\CODE\CRUx-Round3-Tasks\stattron-a881c-firebase-adminsdk-fwiky-b0a560b4ca.json"
# )
# firebase_admin.initialize_app(cred)
commands = [
    "overview",
    "user",
    "channel",
    "top",
    "versus" "heatmap",
    "trends",
    "cloud",
    "sentiment",
    "help",
]


def get_response(message: str) -> str:
    if message == "!help":
        return (
            "Commands:\n"
            + "\n".join([f"{command}" for command in commands])
            + "\n\nFor more information on a command, type `!help <command>`"
        )

    if message.startswith("!help"):
        command = message.split(" ")[1]
        return get_help(message, command)


def get_help(message: str, command: str) -> str:
    if command not in commands:
        return f"Command {command} not found"
    if command == "overview":
        return (
            "Overview command: `!overview`\n"
            "Server overview which shows total messages sent, number of active users, and other relevant metrics"
        )
    elif command == "user":
        return (
            "User command: `!user hourly/daily/weekly`\n"
            "User specific stats that shows the number of messages sent, time spent in voice channels, and other relevant metrics for the specified user."
            " The timeframe can be hourly(for todays day), daily, or weekly."
        )
    elif command == "channel":
        return (
            "Channel command: `!channel`\n"
            "Channel specific stats that shows the most active users in the channel and usage analytics"
        )
    elif command == "top":
        return (
            "Top command: `!top`\n"
            "List the top 10 users ranked by the number of messages sent and time spent in voice channels."
        )
    elif command == "versus":
        return (
            "Versus command: `!versus <user1> <user2>`\n"
            "Compare the number of messages sent and time spent in voice channels between two users."
        )
    elif command == "heatmap":
        return (
            "Heatmap command: `!heatmap server/<channel>`\n"
            "Generate a heatmap of message activity over the course of a week"
            " for the entire server or a specific channel."
        )
    elif command == "trends":
        return (
            "Trends command: `!trends <channel> <n>`\n"
            "trends in server activity, such as increasing or decreasing message frequency over a specific period"
        )
    elif command == "cloud":
        return (
            "Cloud command: `!cloud server/<channel>`\n"
            "Perform a content analysis of messages to identify common keywords and topics. Visualise these using a word cloud."
        )
    elif command == "sentiment":
        return (
            "Sentiment command: `!sentiment <channel>`\n"
            "Analyse and plot the sentiment of messages over time to observe changes in overall server mood."
        )
    elif command == "help":
        return (
            "Help command: `!help <command>`\n"
            "This command gives more information on a specific command"
        )


def overview(server: str):
    db = firestore.client()
    channels = db.collection("channels").where("server", "==", server).get()
    total_messages = 0
    total_voice_time = 0
    active_user_text = ""
    active_user_voice = ""
    for channel in channels:
        channel = channel.to_dict()
        total_messages += channel["total_messages"]
        total_voice_time += channel["total_voice_time"]

        if "active_users" in channel:
            if channel["type"] == "text":
                active_users = channel["active_users"]
                active_user = max(active_users, key=lambda x: x["count"])
                active_user_text = active_user["username"]
            else:
                active_users = channel["active_users"]
                active_user = max(active_users, key=lambda x: x["total_time"])
                active_user_voice = active_user["username"]
    messages = db.collection("messages").where("server", "==", server).get()
    timeseries = []
    for message in messages:
        message = message.to_dict()
        timeseries.append(message["timestamp"])
    avg_messages = total_messages / len(list(set([time.date() for time in timeseries])))
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


def user(server: str, username: str, timeframe: str):
    db = firestore.client()
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
        timeseries.append(message["timestamp"])
    if timeframe == "daily":
        timeseries = [time.date() for time in timeseries]
        message_data = {}
        for time in timeseries:
            if time not in [*message_data]:
                message_data[time] = timeseries.count(time)
        messagesperday = sum([*message_data.values()]) / len([*message_data])
        plot = sns.barplot(x=[*message_data], y=[*message_data.values()])
        plt.xlabel("Date")
        plt.ylabel("Messages")
        plt.title(f"Messages sent by {username}")
        plt.xticks(rotation=45)
        figure = plot.get_figure()
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png")
        buffer.seek(0)
        image = discord.File(buffer, filename="plot.png")
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
        timeseries = ["Week: " + str(time.isocalendar().week) for time in timeseries]
        message_data = {}
        for time in timeseries:
            if time not in [*message_data]:
                message_data[time] = timeseries.count(time)
        messagesperweek = sum([*message_data.values()]) / len([*message_data])
        plot = sns.barplot(x=[*message_data], y=[*message_data.values()])
        plt.xlabel("Week")
        plt.ylabel("Messages")
        plt.title(f"Messages sent by {username}")
        plt.xticks(rotation=45)
        figure = plot.get_figure()
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png")
        buffer.seek(0)
        image = discord.File(buffer, filename="plot.png")
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
        # only get todays messages
        today = datetime.now(timezone("Asia/Kolkata")).date()
        timeseries = [
            str(time.hour) + ":00" for time in timeseries if time.date() == today
        ]
        message_data = {}
        for time in timeseries:
            if time not in [*message_data]:
                message_data[time] = timeseries.count(time)
        messagesperhour = sum([*message_data.values()]) / len([*message_data])
        plot = sns.barplot(x=[*message_data], y=[*message_data.values()])
        plt.xlabel("Hour")
        plt.ylabel("Messages")
        plt.title(f"Messages sent by {username}")
        plt.xticks(rotation=45)
        figure = plot.get_figure()
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png")
        buffer.seek(0)
        image = discord.File(buffer, filename="plot.png")
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


def channel_stats(server, name):
    db = firestore.client()
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
            timeseries.append(message["timestamp"])
        avg_messages = total_messages / len(
            list(set([time.date() for time in timeseries]))
        )
        message_data = {}
        timeseries = [time.date() for time in timeseries]
        for time in timeseries:
            if time not in [*message_data]:
                # message_data[datetime.] = timeseries.count(time)
                message_data[time] = timeseries.count(time)
        plot = sns.scatterplot(x=[*message_data], y=[*message_data.values()])
        plt.xlabel("Date")
        plt.ylabel("Messages")
        plt.title(f"Messages sent in {name}")
        plt.xticks(rotation=45)
        figure = plot.get_figure()
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png")
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


def word_cloud(server, tag):
    db = firestore.client()
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
        background_color="white",
        stopwords=stopwords,
        min_font_size=10,
    ).generate(text)
    plt.figure(figsize=(6, 6), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    buff = io.BytesIO()
    plt.savefig(buff, format="png")
    buff.seek(0)
    image = discord.File(buff, filename="wordcloud.png")
    return image


def sentiment_analysis(server, channel):
    db = firestore.client()
    messages = (
        db.collection("messages")
        .where("server", "==", server)
        .where("channel", "==", channel)
        .get()
    )
    sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    hours = [x for x in range(24)]
    sentiment_score = {hour: 0 for hour in hours}
    for message in messages:
        message = message.to_dict()
        sentiments[message["sentiment"]] += 1
        if message["timestamp"].date() == datetime.now(timezone("Asia/Kolkata")).date():
            sentiment_score[message["timestamp"].hour] += message["sentiment_score"]
    # pie chart
    labels = sentiments.keys()
    sizes = sentiments.values()
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct="%1.1f%%", shadow=True, startangle=90)
    ax1.title.set_text("Sentiment Analysis of all messages")
    ax1.axis("equal")
    buff = io.BytesIO()
    plt.savefig(buff, format="png")
    buff.seek(0)
    image1 = discord.File(buff, filename="sentiment.png")
    plt.clf()
    # line graph
    plot = sns.lineplot(x=[*sentiment_score], y=[*sentiment_score.values()])
    plot.set(xlabel="Hour", ylabel="Sentiment Score")
    plot.set_title("Sentiment Score over the course of the day")
    buff = io.BytesIO()
    plot.get_figure().savefig(buff, format="png")
    buff.seek(0)
    image2 = discord.File(buff, filename="sentiment_score.png")
    return image1, image2


def generate_heatmap(server, tag):
    db = firestore.client()
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
    for message in messages:
        message = message.to_dict()
        dates.append(message["timestamp"].date())
        hours.append(message["timestamp"].hour)
    df = pd.DataFrame({"date": dates, "hour": hours})
    df["date"] = df["date"].apply(lambda x: x.strftime(r"%Y-%m-%d"))
    sns.heatmap(df.groupby(["date", "hour"]).size().unstack(), cmap="coolwarm")
    plt.title("Message Heatmap")
    plt.xlabel("Hour")
    plt.ylabel("Date")
    buff = io.BytesIO()
    plt.savefig(buff, format="png")
    buff.seek(0)
    image = discord.File(buff, filename="heatmap.png")
    return image


def versus(server, user1, user2):
    db = firestore.client()
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
        timeseries1.append(message["timestamp"])
    channels2 = []
    timeseries2 = []
    for message in messages2:
        message = message.to_dict()
        channels2.append(message["channel"])
        timeseries2.append(message["timestamp"])
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
    plot = sns.scatterplot(x=[*message_data1], y=[*message_data1.values()], label=user1)
    plot = sns.scatterplot(x=[*message_data2], y=[*message_data2.values()], label=user2)
    plt.xlabel("Date")
    plt.ylabel("Messages")
    plt.title(f"Messages sent by {user1} and {user2}")
    plt.xticks(rotation=45)
    figure = plot.get_figure()
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png")
    buffer.seek(0)
    image = discord.File(buffer, filename="plot.png")
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
