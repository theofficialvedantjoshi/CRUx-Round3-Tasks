# CRUx-Round 3-Tasks

This repository contains my submissions for the CRUx Dev Inductions Round 3.

## Task 1 - Discord Analytics Bot:

"StatTron" a Discord bot that provides detailed analytics of server activity, visualized through various graphs and charts. The bot offers several commands to display different types of statistics and trends within the server.

### Features
*  Data Collection: Tracks and stores users activity data. The data is stored in a Firestore database on Google cloud.
*  Graphs and plots: Uses Seaborn to plot timeseries activity data based on several commands.
*  Framework: Uses the popular python discord.py library to send, recieve and react to messages on discord.

### Commands
*   !stat overview: Server overview which shows total messages sent, number of active users, and other relevant metrics.

*   !stat user <hourly/daily/weekly>: User specific stats that shows the number of messages sent, time spent in voice channels, and other relevant metrics for the specified user. The timeframe can be hourly(for todays day), daily, or weekly.

*   !stat channel: Channel specific stats that shows the most active users in the channel and usage analytics

*   !stat top: List the top 10 users ranked by the number of messages sent and time spent in voice channels.

*   !stat versus <@user1> <@user2>: Compare the number of messages sent and time spent in voice channels between two users.

*   !stat heatmap server/channel_name: Generate a heatmap of message activity over the course of a week for the entire server or a specific channel.

*   !stat trends channel_name: trends in server activity, such as increasing or decreasing message frequency over a specific period

*   !stat spikes daily/hourly: Visualise spikes in message activity for a specific channel over a specific timeframe

*   !stat cloud server/channel: Perform a content analysis of messages to identify common keywords and topics. Visualise these using a word cloud.

*   !stat sentiment: Analyse and plot the sentiment of messages in that channel over time to observe changes in overall server mood.

*   !stat help command: This command gives more information on a specific command

### Usage
The Bot has been hosted on a virtual linux server. Use the link to invite the bot to your server 

https://discord.com/oauth2/authorize?client_id=1246443201401716848&permissions=17979303652352&integration_type=0&scope=bot

Remember the bot won't instantly show the server stats because it has not recorded any data.

## Task 2 - CLI TOTP Two Factor Authenticator:

This CLI application helps you manage two-factor authentication (TOTP) codes for various services. It includes functionality to add, remove, modify, and show TOTP codes, as well as to import/export services with encrypted JSON files.

### Features

* Add Service: Add a new service with a TOTP seed, usernames can be mentioned to save different seeds for the same service.

* Remove Service: Delete an existing service seed.

* Modify Service: Edit the name or seed of a service.

* Show Code: Display the current TOTP code for a service.

* Copy Code: Copy code to clipboard.

* QR Code: Display the TOTP seed as a QR code for easy addition to an authenticator app like google authenticator.

* Import/Export: Import and export services and their TOTP seeds as JSON files for portability into password protected zip files.

* Database: Uses a secure, encrypted sqlite database for storing services and their TOTP seeds.


### Directory Structure
```plaintext
Task 2 - 2FA CLI/
    ├── data/
    |   ├── totp.db
    |   └──exported_services.json
    ├── temp/
    |   ├── seed-temp-file(deleted on adding service)
    |   └── key.key(key to decrypt database)
    ├── add_service.py
    ├── encryption.py
    ├── json_file.py
    ├── modify_service.py
    ├── show_service.py
    ├── remove_service.py
    └── main.py
```
### Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/theofficialvedantjoshi/CRUx-Round3-Tasks.git
    ```
2. Create a python virtual environment:
    ```sh
    python -m venv myenv
    myenv/Scripts/activate
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Create a .env file in the parent directory and fill it in according to the .env.example file
5. Running the authenticator
    ```sh
    & myenv/Scripts/python.exe "Task 2 - 2FA CLI/main.py"
    ```
6. Use the commands in the CLI app.
    
