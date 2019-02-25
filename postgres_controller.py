import psycopg2

def add_user(connection,id_usuario, first_name, last_name, username, chat_id):
	cursor = connection.cursor()

	cursor.execute("select 1 from users where id=%s limit 1;", (id_usuario,))

	if cursor.fetchone() is None:
		data = (username, id_usuario, last_name, first_name, chat_id)
		cursor.execute("insert into users values(%s,%s,%s,%s,%s)",data)
		connection.commit()

def song_was_added(connection,url):
	cursor = connection.cursor()
	cursor.execute("select 1 from songs where id=%s limit 1",(url,))
	return cursor.fetchone() is not None

def add_song_db(connection, url, title):
	cursor = connection.cursor()
	data = (url, title, 0)
	cursor.execute("insert into songs values(%s,%s,%s)",data)
	connection.commit()

def get_rand_song(connection):
	cursor = connection.cursor()
	cursor.execute("select * from songs order by random() limit 1")
	return cursor.fetchone()

def update_rate(connection, url, rate):
	cursor = connection.cursor()
	cursor.execute("update songs set rate=rate+%s where id=%s",(rate,url))
	connection.commit()

def clear_all_rates(connection):
	cursor = connection.cursor()
	cursor.execute("update songs set rate=0")
	connection.commit()

def clear_all_songs(connection):
	cursor = connection.cursor()
	cursor.execute("delete from songs")
	connection.commit()

def get_top_songs(connection):
	cursor = connection.cursor()
	cursor.execute("select * from songs order by Rate desc limit 5;")
	return cursor.fetchall()