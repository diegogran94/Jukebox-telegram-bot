# Jukebox-telegram-bot

Telegram bot writen in python wich recommends you songs and lets you give them score. Also, you can add songs for others to hear and rate them.

Bot name: [@Jukebox_bot](https://telegram.me/jukebox_bot)

## Available commands

- **play** -> Returns a song and lets you rate it.
- **add** -> Add a song to the database.
- **help** -> Shows available commands
- **top** -> Returns top 5 songs

For the proper usage you have to create the following files:
- **config.py** -> It will contain the token for accesing the telegram bot api and the admin ID (for restricted commands).
- **log.txt** -> It reccords all events that arrive to the bot.

## Create sqlite database

To create the sqlite database and tables use:
```
sqlite3 data.db < init_db.sql
```

## Create config.py file

The config.py file must have de following structure:
```
TOKEN='your_bot_token'
admin='admin_id'
```

Contact:

- [Telegram](http://telegram.me/lIlllIIIlIlIIl)

