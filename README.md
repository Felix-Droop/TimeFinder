# TimeFinder

A discord bot to find common available times for meetings.

## Usage

### Prerequisites

Apart from a discord account and running server you will need Python 3 (.7+) and the following packages:

```
discord.py (1.3.3)
python-dotenv (0.13.0)
portion (2.0.1)
```

It might also run on older/newer versions of the above software.

### Installing

* Create a bot for your server/guild at discordapp.com/developers. 
* Clone this this repository and add a .env file with the following content:

```
TOKEN={your-bot's-token}
GUILD={your-server/guild's-name}
```

### Run

Run `main.py` with your Python 3 distribution. It should connect to your server, where you can find out more about the command interface by typing `!help`. 

If you give yourself the role "Bot Admin" on your server, you will get direct messages about the internal state of the program every time someone enters a command. This feature exists mainly for debugging purposes.

### Usage

All members of a discord server register time intervals to indicate when they are available. 
You can modify these intervals with `!add` and `!remove`. Afterwards these intervals can be displayed with `!show_me` or `!show_all`. Common available time intervals are computed with `!when`.

For more information about all commands and workflows call `!help` and `!tutorial`

## Contributing

I work on this project mainly for fun and don't expect any contributions. But if you like the bot and want to add a feature, don't hesitate to make a pull request!

## Acknowledgments

* Great guide I used to start this project: https://realpython.com/how-to-make-a-discord-bot-python/.
* You could just use Doodle or something like that.
