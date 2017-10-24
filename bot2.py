from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter, CallbackQueryHandler
from telegram import MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
import logging

from funciones_sqlite import *

import lxml
from lxml import etree
import urllib.request

yt_link = 'https://www.youtube.com/watch?v='
yt_link_mobile = 'https://youtu.be/'
len_id_link = 11

#Emojis
like_emoji = u'\U0001F44D'
dislike_emoji = u'\U0001F44E'
happy_emoji = u'\U0001f604'
dot_emoji = u'\U000026AB'

emojis = {dislike_emoji:-1,like_emoji:1,like_emoji+like_emoji:2}

updater = Updater('137411198:AAFaj-Jx0JfwQ2UnI3UJc4rdhSk065_2w4U')
dp = updater.dispatcher

class YtFilter(BaseFilter):
    def filter(self, message):
        return (yt_link in message.text) or (yt_link_mobile in message.text)

def ping_handler(bot, update):
    update.message.reply_text('Pong!')

def yt_title(link):
	youtube = etree.HTML(urllib.request.urlopen(link).read())
	video_title = youtube.xpath("//span[@id='eow-title']/@title")
	return ''.join(video_title)

def add_song(song):

	valid_link = False

	song_link = song

	if yt_link in song:
		song_link = song_link[len(yt_link):]
		song_link = song_link[:len_id_link]
		valid_link = True

	if yt_link_mobile in song_link:
		song_link = song_link[len(yt_link_mobile):]
		song_link = song_link[:len_id_link]
		valid_link = True

	if valid_link:
		if not existe_cancion(song_link):
			title = yt_title(song)
			inserta_cancion(song_link,title)
			msg = 'New song added'
		else:
			msg = 'This song is already stored'
	else:
		msg = 'Invalid link'

	return(msg)

def add_song_handler(bot, update):
	reply = add_song(update.message.text)
	update.message.reply_text(reply)
    
def play_handler(bot, update):

	keyboard =[[InlineKeyboardButton(dislike_emoji,callback_data="-1"),
				InlineKeyboardButton(dot_emoji,callback_data="0"),
				InlineKeyboardButton(like_emoji,callback_data="+1")]]

	reply_markup = InlineKeyboardMarkup(keyboard)

	rand_link = elegir_cancion_rand()
	if rand_link is None:
		update.message.reply_text("There are no songs available")
		return
	update.message.reply_text(yt_link+rand_link[0], reply_markup=reply_markup)

def button(bot, update):
    query = update.callback_query
    reply_markup = ReplyKeyboardRemove()

    link = query.message.text[len(yt_link):]
    rate = int(query.data)

    cambiar_puntuacion(link,rate)	

    bot.edit_message_text(text=query.message.text,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

    bot.send_message(text="Song rated (%s)" % str(rate),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def top_handler(bot, update):
	top_lista_sorted = devolver_canciones_orden()
	if top_lista_sorted:
		salida = 'Top5 songs: \n'
		cont = 0
		for ele in top_lista_sorted:
			cont += 1
			salida += '|*' + str(ele[1]) +'*| '+ '[' + ele[2]  \
			+ '](' + yt_link+ele[0]  + ')\n'

		bot.send_message(text=salida, chat_id=update.message.chat_id, disable_web_page_preview=True, parse_mode='Markdown')
	else:
		bot.send_message(text="There are no songs available.", chat_id=update.message.chat_id)

def help(bot, update):
	mensaje = open('ayuda.txt', 'r').read()
	update.message.reply_text(mensaje)

def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))

#######################################################################################################

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

dp.add_handler(CommandHandler('help', help))
dp.add_handler(CommandHandler('ping', ping_handler))
dp.add_handler(CommandHandler('play', play_handler))
dp.add_handler(CommandHandler('top', top_handler))
dp.add_handler(CallbackQueryHandler(button))
dp.add_handler( MessageHandler(YtFilter(), add_song_handler) )
dp.add_error_handler(error)

updater.start_polling()
updater.idle()