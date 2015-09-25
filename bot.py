# -*- coding: utf-8 -*-
 
import telebot 
from telebot import types 
import time
import csv
import random

from config import TOKEN
from config import admin

import sys
reload(sys) 
sys.setdefaultencoding("utf-8")

usuarios = [line.rstrip('\n') for line in open('usuarios.txt')]

musica_filename = 'musica.csv'
log_filename = 'log.txt'
usuarios_filename = 'usuarios.txt'

yt_link = 'https://www.youtube.com/'

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
              'print': 'Muestra todas las canciones almacenadas y su nota',
}
            
#keyboard
rateSelect = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
rateSelect.add('-1', '1', '2')

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
    help_text = "Estos son los comandos disponibles: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page
        
@bot.message_handler(commands=['hola'])
def command_hola(m):
	cid = m.chat.id
	bot.send_message( cid, 'Hi')
	

@bot.message_handler(commands=['add'])
def command_aniade(m):
	cid = m.chat.id
	msg = bot.send_message( cid, 'A continuación introduzca un enlace válido', reply_markup=forceReply)
	bot.register_next_step_handler(msg, process_add)
	
def process_add(message):
    try:
        cid = message.chat.id
        song = message.text
        if yt_link in song:
    		song = song[len(yt_link):]
    		if not musica.has_key(song):
    			musica[song] = 0
    			open(musica_filename,'w').close()
    			dict_to_csv(musica_filename,musica)
    			bot.reply_to( message, 'Nueva cancion añadida')
    		else:
    			bot.reply_to( message, 'Esa canción ya está almacenada')
    	else:
    			bot.reply_to( message, 'Enlace no válido')
    except Exception as e:
        bot.reply_to(message, 'oooops')
		

@bot.message_handler(commands=['remove'])
def command_remove(m):
	cid = m.chat.id
	link = m.text[m.text.find(" ")+1:]
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
		

@bot.message_handler(commands=['play'])
def command_play(m):
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
        rate = int(message.text)
        bot.reply_to(message, 'Almacenada puntuacion: '+ str(rate), reply_markup=hideBoard)
        musica[prev_link] = int(musica[prev_link]) + rate
        prev_link = None
        dict_to_csv(musica_filename,musica)
    except Exception as e:
        bot.reply_to(message, 'oooops')
        
@bot.message_handler(commands=['print'])
def command_print(m):
    cid = m.chat.id
    salida = ''
    if musica:
        for akey in musica.keys():
            salida += 'Enlace: ' + yt_link+akey + ' | ' + 'Nota: ' + str(musica[akey]) + '\n'
        bot.send_message(cid, salida, disable_web_page_preview=True)
    else:
        bot.send_message(cid, 'La lista está vacía')

@bot.message_handler(commands=['reset_rate'])
def command_reset_rate(m):
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
    cid = m.chat.id
    if str(cid) == admin:
        global musica
        musica = {}
        dict_to_csv(musica_filename,musica)
        bot.send_message(cid, 'Base de datos borrada')
    else:
        bot.send_message(cid, 'No puedes utilizar este comando')
        
@bot.message_handler(commands=['madd'])
def command_maniade(m):
	cid = m.chat.id
	newlink = m.text[m.text.find(" ")+1:] #Eliminamos /add
	for word in newlink.split():
	    if word:
    		if yt_link in word:
    			word = word[len(yt_link):]
    			if not musica.has_key(word):
    				musica[word] = 0
    				open(musica_filename,'w').close()
    				dict_to_csv(musica_filename,musica)
    				bot.send_message( cid, 'Nueva cancion añadida')
    			else:
    				bot.send_message( cid, 'Esa canción ya está almacenada')
    		else:
    			bot.send_message( cid, 'Enlace no válido')
    			

################################################################################

#Peticiones
bot.polling(none_stop=True) # Con esto, le decimos al bot que siga funcionando incluso si encuentra algún fallo.
