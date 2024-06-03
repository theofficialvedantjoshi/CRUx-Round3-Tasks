import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from datetime import datetime
from activity import messages
from response import get_response

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
    await send_message(message, user_message)


@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        time = datetime.now()
        print(f"{member.name} joined {after.channel.name} at {time}")
    elif before.channel is not None and after.channel is None:
        time = datetime.now()
        print(f"{member.name} left {before.channel.name} at {time}")


def main() -> None:
    client.run(TOKEN)


if __name__ == "__main__":
    main()
