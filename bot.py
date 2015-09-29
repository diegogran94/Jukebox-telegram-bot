# -*- coding: utf-8 -*-
 
import telebot 
from telebot import types
import time
import csv
import random

from config import TOKEN
from config import admin

import lxml
from lxml import etree
import urllib

import sys
reload(sys) 
sys.setdefaultencoding("utf-8")

usuarios = [line.rstrip('\n') for line in open('usuarios.txt')]

tiempo_arranque = int(time.time())

musica_filename = 'musica.csv'
log_filename = 'log.txt'
usuarios_filename = 'usuarios.txt'

yt_link = 'https://www.youtube.com/watch?'
yt_example = 'https://www.youtube.com/watch?v=AeszddU2VyI'
yt_example_id = yt_example[len(yt_link):]

prev_link = None

musica = {}
with open(musica_filename, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            musica[row[0]] = row[1]
            
commands = {  # command description used in the "help" command
              'help': 'Muestra los comandos disponibles',
              'add': 'Añade una cancion a la base de datos',
              'play': 'Devuelve una cancion y permite puntuarla',
              'top': 'Muestra las 5 canciones con mayor puntuación'
}


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

#Escibe en un fichero .csv el contenido de un diccionario
#NOTA: No escribe cabecera
def dict_to_csv(filename,dic):
    with open(filename, 'wb') as f:
        w = csv.writer(f)
        w.writerows(dic.items())

#Lee el contenido de un archivo csv y lo pasa a un diccionario
#NOTA: Falla si se le introduce un fichero csv con cabcera
#NOTA2: Por ahora solo funciona correctamente con dos columnas de datos(clave, valor)
def csv_to_dict(filename,dic):
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            dic[row[0]] = row[1]
            
            
#Comprueba si es un mensaje antiguo para no ejecutarlo
def check_time(m):
    if tiempo_arranque > m.date:
        sys.exit()
        
def yt_title(link):
    youtube = etree.HTML(urllib.urlopen(link).read())
    video_title = youtube.xpath("//span[@id='eow-title']/@title")
    return ''.join(video_title)

#Añade una canción a la base de datos
#song = Link de una canción de YT
def add_song(song,message):
    if yt_link in song:
    	song = song[len(yt_link):]
    	song = song[song.find('v'):]
    	song = song[:len(yt_example_id)]

    	if not musica.has_key(song):
    		musica[song] = 0
    		open(musica_filename,'w').close()
    		dict_to_csv(musica_filename,musica)
    		bot.reply_to( message, 'Nueva cancion añadida')
    	else:
    		bot.reply_to( message, 'Esa canción ya está almacenada')
    else:
    	bot.reply_to( message, 'Enlace no válido')
    
    
            
################################################################################
#COMANDOS


@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    bot.send_message( cid, "Hola, soy Jukebox bot, usa /help para ver una lista \
        de todas las ordenes disponibles")
    if not str(cid) in usuarios:
        usuarios.append(str(cid))
        aux = open( usuarios_filename, 'a')
        aux.write( str(cid) + "\n")
        aux.close()
        
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "Estos son los comandos disponibles: \n\n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n\n"
    help_text += "Si detectas algún error o tienes alguna sugerencia no dudes en \
    contactar conmigo: @lIlllIIIlIlIIl"
    bot.send_message(cid, help_text)  # send the generated help page
        
@bot.message_handler(commands=['ping'])
def command_hola(m):
	check_time(m)
	cid = m.chat.id
	bot.send_message( cid, "Pong"+ ' ' + happy_emoji)
	

@bot.message_handler(commands=['add'])
def command_aniade(m):
	check_time(m)
	cid = m.chat.id
	msg = bot.send_message( cid, 'A continuación introduzca un enlace válido', reply_markup=forceReply)
	bot.register_next_step_handler(msg, process_add)
	
def process_add(message):
    try:
        cid = message.chat.id
        song = message.text
        add_song(song,message)
    except Exception as e:
        bot.reply_to(message, 'Ha habido un error')
		

@bot.message_handler(commands=['remove'])
def command_remove(m):
	check_time(m)
	cid = m.chat.id
	link = m.text[m.text.find(" ")+1:]
	if str(cid) == admin:
		if link:
			if yt_link in link:
				link = link[len(yt_link):]
				if musica.has_key(link):
					musica.pop(link)
					dict_to_csv(musica_filename,musica)
					bot.send_message(cid,'Cancion eliminada')
				else:
					bot.send_message(cid,'Esa canción no está almacenada')
			else:
				bot.send_message( cid, 'Enlace no válido')
		else:
			bot.send_message( cid, 'Introduzca un enlace')
	else:
		bot.send_message( cid, 'No tienes acceso a este comando')
		

@bot.message_handler(commands=['play'])
def command_play(m):
    check_time(m)
    cid = m.chat.id
    if musica: #Comprobamos que no esta vacio
        rand_link = random.choice(musica.keys())
        global prev_link
        prev_link = rand_link
        bot.send_message( cid, yt_link+rand_link)
        
        msg = bot.send_message(cid, "Puntua esta cancion:", reply_markup=rateSelect)
        bot.register_next_step_handler(msg, process_rate)
    else:
        bot.send_message(cid, 'La lista está vacía')

        
def process_rate(message):
    try:
        chat_id = message.chat.id
        global prev_link
        key = message.text
        rate = emojis[key]
        bot.reply_to(message, 'Almacenada puntuacion: '+ str(rate), reply_markup=hideBoard)
        musica[prev_link] = int(musica[prev_link]) + rate
        prev_link = None
        dict_to_csv(musica_filename,musica)
    except Exception as e:
        bot.reply_to(message, 'oooops')
      
 
#@bot.message_handler(commands=['print'])
def command_print(m):
    check_time(m)
    cid = m.chat.id
    salida = 'Lista de canciones: \n'
    if musica:
        for akey in musica.keys():
            salida += '\n' + yt_title(yt_link+akey) + '\n' + \
            '     Enlace: ' + yt_link+akey + ' | ' + 'Nota: ' + str(musica[akey]) + '\n'
        bot.send_message(cid, salida, disable_web_page_preview=True)
    else:
        bot.send_message(cid, 'La lista está vacía')


@bot.message_handler(commands=['reset_rate'])
def command_reset_rate(m):
    check_time(m)
    cid = m.chat.id
    if str(cid) == admin:
        for i in musica.keys():
            musica[i] = 0
        dict_to_csv(musica_filename,musica)
        bot.send_message(cid, 'Las puntuaciones han sido borradas')
    else:
        bot.send_message(cid, 'No puedes utilizar este comando')

    
@bot.message_handler(commands=['reset_all'])
def command_reset_all(m):
    check_time(m)
    cid = m.chat.id
    if str(cid) == admin:
        global musica
        musica = {}
        dict_to_csv(musica_filename,musica)
        bot.send_message(cid, 'Base de datos borrada')
    else:
        bot.send_message(cid, 'No puedes utilizar este comando')

#TESTING
@bot.message_handler(commands=['madd'])
def command_maniade(m):
	check_time(m)
	cid = m.chat.id
	if str(cid) == admin:
		newlink = m.text[m.text.find(" ")+1:] #Eliminamos /add
		print newlink
		for word in newlink.split():
		    add_song(word,m)
	else:
		bot.send_message(cid, 'No puedes utilizar este comando')

@bot.message_handler(commands=['top'])			
def command_top(m):
    try:
    	check_time(m)
    	cid = m.chat.id
    	top_lista = musica.items()
    	top_lista_sorted = sorted(top_lista, key=lambda tup: tup[1], reverse=True)
    	#print top_lista_sorted
    	salida = 'Top5 de canciones: \n'
    	cont = 0
    	for ele in top_lista_sorted:
    	    cont += 1
    	    salida += '|' + str(ele[1]) +'| '+ yt_title(yt_link+ele[0])  \
    	    + " " + yt_link+ele[0]  + '\n'
    	    if cont == 5:
    	        break
            
    	bot.send_message(cid, salida, disable_web_page_preview=True)
    except Exception as e:
        bot.reply_to(m,"Ha habido un error")
        print e
        

################################################################################

#Peticiones
bot.polling(none_stop=True) # Con esto, le decimos al bot que siga funcionando incluso si encuentra algún fallo.
