import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Member
from datetime import datetime
from activity import (
    messages,
    get_voice,
    add_voice,
    join_voice,
    leave_voice,
    get_channels,
    add_channels,
    update_channels,
    delete_message,
)
from response import get_response
from pytz import timezone

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setup
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)


async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("No message to send")
        return
    try:
        response = get_response(user_message)
        await message.channel.send(response)
    except Exception as e:
        print(f"Error: {e}")


# start up
@client.event
async def on_ready():
    print(f"{client.user} is now running")
    # n.o of channels
    for server in client.guilds:
        print(f"Connected to server: {server.name}")
        for channel in server.channels:
            print(f"Connected to channel: {channel.name}")
            if not get_channels(server.name, channel.name):
                if channel.type[0] != "category":
                    add_channels(server.name, channel.name, channel.type[0], 0, 0, [])


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return
    username = message.author.name
    user_message = message.content
    channel = message.channel
    print(f"{username} said: {user_message} in {channel}")
    time = datetime.now()
    messages(
        server=message.guild.name,
        channel=channel.name,
        content=user_message,
        author=username,
        timestamp=time,
    )
    update_channels(message.guild.name, channel.name)
    await send_message(message, user_message)


@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        time = datetime.now(timezone("Asia/Kolkata"))
        print(f"{member.name} joined {after.channel.name} at {time}")
        user = get_voice(member.guild.name, after.channel.name, member.name)
        if user:
            join_voice(user, time)
        else:
            add_voice(
                server=member.guild.name,
                channel=after.channel.name,
                username=member.name,
                last_joined=time,
                last_left=None,
                total_time=0,
            )
        update_channels(member.guild.name, after.channel.name)
    elif before.channel is not None and after.channel is None:
        time = datetime.now(timezone("Asia/Kolkata"))
        print(f"{member.name} left {before.channel.name} at {time}")
        user = get_voice(member.guild.name, before.channel.name, member.name)
        total_time = (time - user[0].to_dict()["last_joined"]).total_seconds() + user[
            0
        ].to_dict()["total_time"]
        leave_voice(user, time, total_time)
        update_channels(member.guild.name, before.channel.name)


@client.event
async def on_guild_channel_create(channel):
    add_channels(channel.guild.name, channel.name, channel.type[0], 0, 0, [])


@client.event
async def on_guild_channel_delete(channel):
    print(f"Channel {channel.name} deleted")


@client.event
async def on_message_delete(message):
    print(f"Message {message.content} deleted")
    delete_message(
        message.guild.name, message.channel.name, message.content, message.author.name
    )


def main() -> None:
    client.run(TOKEN)


if __name__ == "__main__":
    main()
