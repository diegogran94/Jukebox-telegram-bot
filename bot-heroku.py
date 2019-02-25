import logging
import os
import psycopg2
from psycopg2 import Error

import lxml
from lxml import etree
import urllib.request

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter, CallbackQueryHandler
from postgres_controller import *

# DATABASE_URL = os.environ['DATABASE_URL']

# conn = psycopg2.connect(DATABASE_URL, sslmode='require')

#Emojis
like_emoji = u'\U0001F44D'
dislike_emoji = u'\U0001F44E'
happy_emoji = u'\U0001f604'
dot_emoji = u'\U000026AB'

emojis = {dislike_emoji:-1,like_emoji:1,like_emoji+like_emoji:2}


keyboard = [[InlineKeyboardButton(dislike_emoji,callback_data="-1"),
			InlineKeyboardButton(dot_emoji,callback_data="0"),
			InlineKeyboardButton(like_emoji,callback_data="+1")]]

rateSelect = InlineKeyboardMarkup(keyboard)

yt_link = 'https://www.youtube.com/watch?v='
yt_link_mobile = 'https://youtu.be/'
len_id_link = 11

def is_a_yt_link(link):
	return (yt_link in link) or (yt_link_mobile in link)

class FilterYtLink(BaseFilter):
	def filter(self, message):
		return is_a_yt_link(message.text)

filter_ytlink = FilterYtLink()

def yt_title(link):
	youtube = etree.HTML(urllib.request.urlopen(link).read())
	video_title = youtube.xpath("//span[@id='eow-title']/@title")
	return ''.join(video_title)

try:
	connection = psycopg2.connect(user = "postgres",
									password = "123456",
									host = "127.0.0.1",
									port = "5432",
									database = "postgres")

except (Exception, psycopg2.DatabaseError) as error_e :
	print ("Error while connecting to PostgreSQL", error_e)

def start(bot, update):
	user = update.message.from_user
	update.effective_message.reply_text("Hii! " + user.first_name)

	add_user(connection, user.id, user.first_name, user.last_name, user.username, update.message.chat.id)

def add_song(bot, update):
	message = update.message.text

	if not is_a_yt_link(message):
		update.message.reply_text('Not a song')
		return

	update.message.reply_text('Song detected...')

	valid_link = False

	song_link = message

	if yt_link in message:
		song_link = song_link[len(yt_link):]
		song_link = song_link[:len_id_link]
		valid_link = True

	if yt_link_mobile in song_link:
		song_link = song_link[len(yt_link_mobile):]
		song_link = song_link[:len_id_link]
		valid_link = True

	if valid_link:
		if not song_was_added(connection, song_link):
			title = yt_title(message)
			add_song_db(connection,song_link,title)
			update.message.reply_text('New song added')
		else:
			update.message.reply_text('This song is already stored')
	else:
		update.message.reply_text('Invalid link')

def play(bot, update):
	rand_link = get_rand_song(connection)

	if rand_link is None:
		update.message.reply_text("There are no songs available")
		return
	update.message.reply_text(yt_link+rand_link[0], reply_markup=rateSelect)

def callback_handler(bot, update, chat_data):
	query = update.callback_query
	try:
		prev_link = query.message.text[len(yt_link):]
		rate = int(query.data)
		
		update_rate(connection,prev_link,rate)
		bot.edit_message_text(query.message.text,chat_id=query.message.chat.id,message_id=query.message.message_id)
		bot.answer_callback_query(query.id,"Song rated ("+str(rate)+")")

	except Exception as e:
		update.message.reply_text('There was an error')
		print(e)

def get_top_5(bot, update):
	top_song = get_top_songs(connection)
	if(top_song):
		return_str = 'Top5 songs: \n'
		for row in top_song:
			return_str += '|*' + str(row[2]) +'*| '+ '[' + row[1]  \
			+ '](' + yt_link+row[0]  + ')\n'
		update.message.reply_text(return_str, disable_web_page_preview=True, parse_mode='Markdown')
	else:
		update.message.reply_text("There are no songs available")

def ping(bot, update):
	update.message.reply_text("Pong " + happy_emoji)

def error(bot, update, error):
	logger.warning('Update "%s" caused error "%s"', update, error)


if __name__ == "__main__":
	# Set these variable to the appropriate values

	TOKEN = os.environ.get('TOKEN_BOT')
	print("TOKEN -> " + TOKEN)

	NAME = os.environ.get('APP_NAME')
	print("NAME -> " + NAME)

	# Port is given by Heroku
	PORT = os.environ.get('PORT')

	# Enable logging
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
						level=logging.INFO)
	logger = logging.getLogger(__name__)

	# Set up the Updater
	updater = Updater(TOKEN)
	dp = updater.dispatcher

	# Add handlers
	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(CommandHandler('play', play))
	dp.add_handler(CommandHandler('ping', ping))
	dp.add_handler(CommandHandler('top', get_top_5))
	dp.add_handler(MessageHandler(filter_ytlink, add_song))
	dp.add_handler(CallbackQueryHandler(callback_handler, pass_chat_data=True))
	dp.add_error_handler(error)

	# Start the webhook
	# updater.start_webhook(listen="0.0.0.0",
	#                       port=int(PORT),
	#                       url_path=TOKEN)
	# updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
	updater.start_polling()
	updater.idle()
