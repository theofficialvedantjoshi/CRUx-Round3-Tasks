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
