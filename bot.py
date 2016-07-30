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

tiempo_arranque = int(time.time())

log_filename = 'log.txt'

yt_link = 'https://www.youtube.com/watch?'
yt_example = 'https://www.youtube.com/watch?v=AeszddU2VyI'
yt_example_id = yt_example[len(yt_link):]

#Aqui se guarda el link de la cancion para pasarla a la
#funcion que le da una puntuacion
prev_link = None


#Emojis
like_emoji = u'\U0001F44D'
dislike_emoji = u'\U0001F44E'
happy_emoji = u'\U0001f604'

emojis = {dislike_emoji:-1,like_emoji:1,like_emoji+like_emoji:2}

#keyboard
rateSelect = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
rateSelect.add(dislike_emoji, like_emoji, like_emoji+like_emoji)

hideBoard = types.ReplyKeyboardHide()

forceReply = types.ForceReply()

bot = telebot.TeleBot(TOKEN)

################################################################################

#Listener
def listener(messages):
	for m in messages:
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

#Comprueba si es un mensaje antiguo para no ejecutarlo
def check_time(m):
	return tiempo_arranque > m.date


def yt_title(link):
	youtube = etree.HTML(urllib.urlopen(link).read())
	video_title = youtube.xpath("//span[@id='eow-title']/@title")
	return ''.join(video_title)


################################################################################
#COMANDOS


@bot.message_handler(commands=['start'])
def command_start(m):
	cid = m.chat.id
	bot.send_message( cid, "Hola "+m.from_user.first_name+", soy Jukebox bot, usa\
	 /help para ver una lista de todas las ordenes disponibles. (EN PRUEBAS)")
	inserta_usuario_nuevo(m.from_user.id, m.from_user.first_name, m.from_user.last_name, m.from_user.username)

@bot.message_handler(commands=['help'])
def command_help(m):
	cid = m.chat.id

	try:
		mensaje = open('ayuda.txt', 'r').read()
		bot.send_message(cid,mensaje)

	except Exception as e:
		bot.reply_to(m,'Se ha producido un error, intentelo mas tarde')

@bot.message_handler(commands=['ping'])
def command_hola(m):
	#check_time(m)

	cid = m.chat.id
	bot.send_message( cid, "Pong"+ ' ' + happy_emoji)


@bot.message_handler(commands=['add'])
def command_aniade(m):
	#check_time(m)
	cid = m.chat.id
	msg = bot.send_message( cid, 'A continuación introduzca un enlace de Youtube válido', reply_markup=forceReply)
	bot.register_next_step_handler(msg, process_add)

def process_add(message):
	try:
		cid = message.chat.id
		song = message.text

		if yt_link in song:
			song = song[len(yt_link):]
			song = song[song.find('v'):]
			song = song[:len(yt_example_id)]

			if not existe_cancion(song):
				inserta_cancion(song)
				bot.reply_to( message, 'Nueva cancion añadida')
			else:
				bot.reply_to( message, 'Esa canción ya está almacenada')
		else:
			bot.reply_to( message, 'Enlace no válido')

	except Exception as e:
		bot.reply_to(message, 'Ha habido un error')
		print e



@bot.message_handler(commands=['play'])
def command_play(m):
	#check_time(m)
	cid = m.chat.id

	rand_link = elegir_cancion_rand()
	if rand_link is None:
		bot.send_message(cid, "No hay canciones disponibles, puedes añadir una usando /add")
		return
	global prev_link
	prev_link = rand_link
	bot.send_message( cid, yt_link+rand_link[0])

	msg = bot.send_message(cid, "Puntua esta cancion:", reply_markup=rateSelect)
	bot.register_next_step_handler(msg, process_rate)



def process_rate(message):
	try:
		chat_id = message.chat.id
		global prev_link
		key = message.text
		rate = emojis[key]

		cambiar_puntuacion(prev_link[0],prev_link[1]+rate)
		prev_link = None
		bot.reply_to(message, 'Almacenada puntuacion: '+ str(rate), reply_markup=hideBoard)
	except Exception as e:
		bot.reply_to(message, 'oooops')


@bot.message_handler(commands=['reset_rate'])
def command_reset_rate(m):
	#check_time(m)
	cid = m.chat.id
	if str(cid) == admin:
		limpiar_rate()
		bot.send_message(cid, 'Las puntuaciones han sido borradas')
	else:
		bot.send_message(cid, 'No puedes utilizar este comando')


@bot.message_handler(commands=['reset_all'])
def command_reset_all(m):
	#check_time(m)
	cid = m.chat.id
	if str(cid) == admin:
		limpiar_canciones()
		bot.send_message(cid, 'Base de datos borrada')
	else:
		bot.send_message(cid, 'No puedes utilizar este comando')

# @bot.message_handler(commands=['madd'])
# def command_maniade(m):
# 	#check_time(m)
# 	cid = m.chat.id
# 	if str(cid) == admin:
# 		newlink = m.text[m.text.find(" ")+1:] #Eliminamos /add
# 		print newlink
# 		for word in newlink.split():
# 			add_song(word,m)
# 	else:
# 		bot.send_message(cid, 'No puedes utilizar este comando')

@bot.message_handler(commands=['top'])
def command_top(m):
	try:
		#check_time(m)
		cid = m.chat.id
		top_lista_sorted = devolver_canciones_orden()
		if top_lista_sorted:
			salida = 'Top5 de canciones: \n'
			cont = 0
			for ele in top_lista_sorted:
				cont += 1
				salida += '|' + str(ele[1]) +'| '+ yt_title(yt_link+ele[0])  \
				+ " " + yt_link+ele[0]  + '\n'

			bot.send_message(cid, salida, disable_web_page_preview=True)
		else:
			bot.send_message(cid, "No hay canciones disponibles, puedes añadir una usando /add")
	except Exception as e:
		bot.reply_to(m,"Ha habido un error")
		print e


################################################################################

#Peticiones
bot.polling(none_stop=True) # Con esto, le decimos al bot que siga funcionando incluso si encuentra algún fallo.
