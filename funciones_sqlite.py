# -*- coding: utf-8 -*-

import sqlite3
import sys

#FUNCIONES PARA MANEJAR LA TABLA CANCIONES

def existe_cancion(url):

    con = sqlite3.connect('data.db')

    with con:
        c = con.cursor()
        c.execute("select 1 from canciones where Name=? limit 1",(url,))

        return c.fetchone() is not None

def elegir_cancion_rand():

    con = sqlite3.connect('data.db')

    with con:
        c = con.cursor()
        c.execute("select * from canciones order by random() limit 1")

        return c.fetchone()

def inserta_cancion(url,title):

    con = sqlite3.connect('data.db')

    with con:
        c = con.cursor()
        c.execute("insert into canciones values(?,0,?)",(url,title))

def cambiar_puntuacion(url,rate):

    con = sqlite3.connect('data.db')

    with con:
        c = con.cursor()
        c.execute("update canciones set Rate=? where Name=?",(rate,url))

def devolver_canciones_orden():
    con = sqlite3.connect('data.db')

    with con:
        c = con.cursor()
        c.execute("select * from canciones order by Rate desc limit 5;")

        return c.fetchall()

def limpiar_rate():
    con = sqlite3.connect('data.db')

    with con:
        c = con.cursor()
        c.execute("update canciones set rate=0;")

def limpiar_canciones():
    con = sqlite3.connect('data.db')

    with con:
        c = con.cursor()
        c.execute("delete from canciones;")


#FUNCIONES PARA MANEJAR LA TABLA USUARIOS

def inserta_usuario_nuevo(id_usuario, first_name, last_name, username):
    con = sqlite3.connect('data.db')

    with con:
        c = con.cursor()
        c.execute("select 1 from usuarios where Id=? limit 1",(id_usuario,))

        if c.fetchone() is None:
            c.execute("insert into usuarios values(?,?,?,?)",(id_usuario, first_name, last_name, username))
