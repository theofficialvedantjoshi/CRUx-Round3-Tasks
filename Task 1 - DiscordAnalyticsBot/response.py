import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import discord
import seaborn as sns
from matplotlib import pyplot as plt
import io

commands = [
    "!overview",
    "!user",
    "!channel",
    "!top",
    "!heat",
    "!trends",
    "!cloud",
    "!sentiment",
    "!help",
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
    if command == "!overview":
        return (
            "Overview command: `!overview`\n"
            "Server overview which shows total messages sent, number of active users, and other relevant metrics"
        )
    elif command == "!user":
        return (
            "User command: `!user <user>`\n"
            "User specific stats that shows the number of messages sent, time spent in voice channels, and other relevant metrics for the specified user."
        )
    elif command == "!channel":
        return (
            "Channel command: `!channel`\n"
            "Channel specific stats that shows the most active users in the channel and usage analytics"
        )
    elif command == "!top":
        return (
            "Top command: `!top`\n"
            "List the top 10 users ranked by the number of messages sent and time spent in voice channels."
        )
    elif command == "!heat":
        return (
            "Heat command: `!heat`\n"
            "Generate a heatmap of message activity over the course of a week"
        )
    elif command == "!trends":
        return (
            "Trends command: `!trends <channel> <n>`\n"
            "trends in server activity, such as increasing or decreasing message frequency over a specific period"
        )
    elif command == "!cloud":
        return (
            "Cloud command: `!cloud <channel> <n>`\n"
            "Perform a content analysis of messages to identify common keywords and topics. Visualise these using a word cloud."
        )
    elif command == "!sentiment":
        return (
            "Sentiment command: `!sentiment <channel>`\n"
            "Analyse and plot the sentiment of messages over time to observe changes in overall server mood."
        )
    elif command == "!help":
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
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="Server Overview",
        description=f"Total messages sent: {total_messages}\n"
        f"Total voice time: {total_voice_time}\n"
        f"Most active user in text channels: {active_user_text}\n"
        f"Most active user in voice channels: {active_user_voice}",
    )
    return embed


def user(server: str, username: str):
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
    # grouping by day
    timeseries = [time.date() for time in timeseries]
    message_data = {}
    for time in timeseries:
        if time not in [*message_data]:
            message_data[time] = timeseries.count(time)
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
        f"Total voice time: {total_voice_time}\n"
        f"Most active channel: {most_active_channel[0]}",
    )
    embed.set_image(url="attachment://plot.png")
    return embed, image
