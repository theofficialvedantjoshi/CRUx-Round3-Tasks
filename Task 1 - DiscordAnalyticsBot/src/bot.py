from config import config
from discord import Intents, Client, Message, Member
import discord
from datetime import datetime
from pytz import timezone
from src.activity import Activity
from src.response import Response

activity = Activity()
responses = Response()
TOKEN = config.DISCORD_TOKEN
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)


async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("No message to send")
        return
    try:
        print(f"User message: {user_message}")
        if user_message == "!overview":
            response = responses.overview(message.guild.name)
            await message.channel.send(embed=response)
        if user_message.startswith("!user"):
            timeframe = user_message.split(" ")[1]
            response, image = responses.user(
                message.guild.name, message.author.name, timeframe
            )
            await message.channel.send(embed=response)
            await message.channel.send(file=image)
        if user_message.startswith("!channel"):
            name = user_message.split(" ")[1]
            try:
                response, image = responses.channel_stats(message.guild.name, name)
                await message.channel.send(embed=response)
                if image:
                    await message.channel.send(file=image)
            except Exception as e:
                print(f"Error: {e}")
                await message.channel.send("Channel not found")
        if user_message.startswith("!cloud"):
            tag = user_message.split(" ")[1]
            response = responses.word_cloud(message.guild.name, tag)
            await message.channel.send(file=response)
        if user_message == "!sentiment":
            image1, image2 = responses.sentiment_analysis(
                message.guild.name, message.channel.name
            )
            await message.channel.send(file=image1)
            await message.channel.send(file=image2)
        if user_message.startswith("!heatmap"):
            tag = user_message.split(" ")[1]
            image = responses.generate_heatmap(message.guild.name, tag)
            await message.channel.send(file=image)
        if user_message.startswith("!versus"):
            user1 = await client.fetch_user(int(user_message.split(" ")[1][2:-1]))
            user2 = await client.fetch_user(int(user_message.split(" ")[2][2:-1]))
            response, image = responses.versus(
                message.guild.name, user1.name, user2.name
            )
            await message.channel.send(embed=response)
            await message.channel.send(file=image)
        if user_message == "!top":
            response = responses.top_users(message.guild.name, 5)
            await message.channel.send(file=response)
        else:
            response = responses.get_response(user_message)
            await message.channel.send(response)
    except Exception as e:
        print(f"Error: {e}")


@client.event
async def on_ready():
    print(f"{client.user} is now running")
    for server in client.guilds:
        print(f"Connected to server: {server.name}")
        for channel in server.channels:
            print(f"Connected to channel: {channel.name}")
            if not activity.get_channels(server.name, channel.name):
                if channel.type[0] != "category":
                    activity.add_channels(
                        server.name, channel.name, channel.type[0], 0, 0, []
                    )


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return
    username = message.author.name
    user_message = message.content
    channel = message.channel
    print(f"{username} said: {user_message} in {channel}")
    time = datetime.now(timezone("Asia/Kolkata"))
    activity.messages(
        server=message.guild.name,
        channel=channel.name,
        content=user_message,
        author=username,
        timestamp=time,
    )
    activity.update_channels(message.guild.name, channel.name)
    await send_message(message, user_message)


@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        time = datetime.now(timezone("Asia/Kolkata"))
        print(f"{member.name} joined {after.channel.name} at {time}")
        user = activity.get_voice(member.guild.name, after.channel.name, member.name)
        if user:
            activity.join_voice(user, time)
        else:
            activity.add_voice(
                server=member.guild.name,
                channel=after.channel.name,
                username=member.name,
                last_joined=time,
                last_left=None,
                total_time=0,
            )
        activity.update_channels(member.guild.name, after.channel.name)
    elif before.channel is not None and after.channel is None:
        time = datetime.now(timezone("Asia/Kolkata"))
        print(f"{member.name} left {before.channel.name} at {time}")
        user = activity.get_voice(member.guild.name, before.channel.name, member.name)
        total_time = (time - user[0].to_dict()["last_joined"]).total_seconds() + user[
            0
        ].to_dict()["total_time"]
        activity.leave_voice(user, time, total_time)
        activity.update_channels(member.guild.name, before.channel.name)


@client.event
async def on_guild_channel_create(channel):
    activity.add_channels(channel.guild.name, channel.name, channel.type[0], 0, 0, [])


@client.event
async def on_guild_channel_delete(channel):
    print(f"Channel {channel.name} deleted")
    activity.delete_channel(channel.guild.name, channel.name)


@client.event
async def on_message_delete(message):
    print(f"Message {message.content} deleted")
    activity.delete_message(
        message.guild.name, message.channel.name, message.content, message.author.name
    )


def bot() -> None:
    client.run(TOKEN)
