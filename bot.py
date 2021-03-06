# -*- coding: utf-8 -*-

import telebot
from telebot import types
import time
import random
from funciones_sqlite import *

from config import TOKEN
from config import admin

import lxml
from lxml import etree
import urllib

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


log_filename = 'log.txt'

yt_link = 'https://www.youtube.com/watch?v='
yt_link_mobile = 'https://youtu.be/'

len_id_link = 11

#Aqui se guarda el link de la cancion para pasarla a la
#funcion que le da una puntuacion
prev_link = None


#Emojis
like_emoji = u'\U0001F44D'
dislike_emoji = u'\U0001F44E'
happy_emoji = u'\U0001f604'
dot_emoji = u'\U000026AB'

emojis = {dislike_emoji:-1,like_emoji:1,like_emoji+like_emoji:2}


rateSelect = types.InlineKeyboardMarkup()
rateSelect.add(types.InlineKeyboardButton(dislike_emoji,callback_data="-1"),
			types.InlineKeyboardButton(dot_emoji,callback_data="0"),
			types.InlineKeyboardButton(like_emoji,callback_data="+1"))


forceReply = types.ForceReply()

#Play
users_who_voted = {}
actual_callback = {}

bot = telebot.TeleBot(TOKEN)

################################################################################

#Listener
def listener(messages):
	for m in messages:
		cid = m.chat.id
		#Si (estoy en un grupo y recibo un comando) o estoy en un chat privado
		#Esto evita que el bot almacene todas las conversaciones del grupo
		if (m.chat.type == 'group' and m.text.startswith("/")) or m.chat.type == 'private':
			if m.content_type == 'text':
				user_id = m.from_user.id
				name = m.from_user.first_name
				last_name = m.from_user.last_name
				username = m.from_user.username
				hour = time.strftime("%H:%M:%S")
				date = time.strftime("%d/%m/%y")
				information = "["+ str(date) + ' ' + str(hour) + ' ' +str(name)  + ' ' + \
				str(last_name) + ' ' + str(user_id) + ' @' + str(username) + "]: " + m.text

				aux = open(log_filename, 'a')
				aux.write( str(information) + "\n")
				aux.close()
				print information

bot.set_update_listener(listener)

################################################################################
#FUNCIONES


def yt_title(link):
	youtube = etree.HTML(urllib.urlopen(link).read())
	video_title = youtube.xpath("//span[@id='eow-title']/@title")
	return ''.join(video_title)

def is_a_yt_link(link):
	return (yt_link in link) or (yt_link_mobile in link)

def add_song(song,message):

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
			bot.reply_to( message, 'New song added')
		else:
			bot.reply_to( message, 'This song is already stored')
	else:
		bot.reply_to( message, 'Invalid link')


################################################################################
#COMANDOS


@bot.message_handler(commands=['start'])
def command_start(m):
	cid = m.chat.id
	bot.send_message( cid, "Hello "+m.from_user.first_name+", I'm Jukebox bot, use\
	 /help to view the list of available commands. (TESTING)")
	inserta_usuario_nuevo(m.from_user.id, m.from_user.first_name, m.from_user.last_name, m.from_user.username)

@bot.message_handler(commands=['help'])
def command_help(m):
	cid = m.chat.id

	try:
		mensaje = open('ayuda.txt', 'r').read()
		bot.send_message(cid,mensaje)

	except Exception as e:
		bot.reply_to(m,'An error has occurred. Please, try it later')

@bot.message_handler(commands=['ping'])
def command_hola(m):
	cid = m.chat.id
	bot.send_message( cid, "Pong"+ ' ' + happy_emoji)
	
@bot.message_handler(commands=['chatid'])
def command_chatid(m):
	cid = m.chat.id
	bot.send_message( cid, cid)


@bot.message_handler(commands=['add'])
def command_add(m):
	cid = m.chat.id
	msg = bot.send_message( cid, 'Now, enter a valid youtube link', reply_markup=forceReply)
	bot.register_next_step_handler(msg, process_add)

def process_add(m):
	try:
		cid = m.chat.id
		song = m.text

		add_song(song,m)

	except Exception as e:
		bot.reply_to(m, 'There was an error')
		print e

@bot.message_handler(func=lambda msg: is_a_yt_link(msg.text))
def pasive_add(m):
	cid = m.chat.id

	add_song(m.text,m)


@bot.message_handler(commands=['play'])
def command_play(m):
	cid = m.chat.id

	rand_link = elegir_cancion_rand()
	if rand_link is None:
		bot.send_message(cid, "There are no songs available, you can add them using /add")
		return
	msg = bot.send_message( cid, yt_link+rand_link[0],reply_markup=rateSelect)
	users_who_voted[cid] = []
	actual_callback[cid] = msg.message_id


#Recibe la ultima callback
@bot.callback_query_handler(func=lambda call: actual_callback[call.message.chat.id]==call.message.message_id)
def play_callback(call):
	try:
		prev_link = call.message.text[len(yt_link):]
		rate = int(call.data)
		
		actual_user = call.from_user
		actual_chat = call.message.chat
		
		if not users_who_voted.has_key(actual_chat.id):
			users_who_voted[actual_chat.id] = []
		
		if actual_user.id in users_who_voted[actual_chat.id]:
			bot.answer_callback_query(call.id,"Ya has votado")
		else:
			users_who_voted[actual_chat.id].append(actual_user.id)
			cambiar_puntuacion(prev_link,rate)		
			#bot.edit_message_text(call.message.text,chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=rateSelect)
			bot.answer_callback_query(call.id,"Song rated ("+str(rate)+")")
			#bot.reply_to(call.message,"Song rated ("+str(rate)+")") #Para debug
	except Exception as e:
		bot.reply_to(call.message, 'There was an error')
		print(e)

#Recibe las callbacks antiguas
@bot.callback_query_handler(func=lambda call: actual_callback[call.message.chat.id]!=call.message.message_id)
def play_pass_callback(call):
	bot.answer_callback_query(call.id,"No puedes votar canciones antiguas")
	
	
@bot.message_handler(commands=['reset_rate'])
def command_reset_rate(m):
	cid = m.chat.id
	if str(cid) == admin:
		limpiar_rate()
		bot.send_message(cid, 'Rates been deleted')
	else:
		bot.send_message(cid, 'You can\'t use this command')


@bot.message_handler(commands=['reset_all'])
def command_reset_all(m):
	cid = m.chat.id
	if str(cid) == admin:
		limpiar_canciones()
		bot.send_message(cid, 'Database deleted')
	else:
		bot.send_message(cid, 'You can\'t use this command')



@bot.message_handler(commands=['top'])
def command_top(m):
	try:
		cid = m.chat.id
		top_lista_sorted = devolver_canciones_orden()
		if top_lista_sorted:
			salida = 'Top5 songs: \n'
			cont = 0
			for ele in top_lista_sorted:
				cont += 1
				salida += '|*' + str(ele[1]) +'*| '+ '[' + ele[2]  \
				+ '](' + yt_link+ele[0]  + ')\n'

			bot.send_message(cid, salida, disable_web_page_preview=True, parse_mode='Markdown')
		else:
			bot.send_message(cid, "There are no songs available, you can add them using /add")
	except Exception as e:
		bot.reply_to(m,"There was an error")
		print e


################################################################################

def main_loop():
    #Comprueba si es un mensaje antiguo para no ejecutarlo
    bot.skip_pending = True
    bot.polling(True)
    while 1:
        time.sleep(3)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\n'
        sys.exit(0)
