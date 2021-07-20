import psycopg2
import urllib.parse as up

from flask import Flask,g
from flask import render_template,jsonify

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(os.path.dirname(os.path.realpath(__file__)), '.env')
load_dotenv(dotenv_path)

DATABASE_URL = os.environ.get("DATABASE_URL")

up.uses_netloc.append("postgres")
url = up.urlparse(DATABASE_URL)
dbconn = psycopg2.connect(database=url.path[1:],
user=url.username,
password=url.password,
host=url.hostname,
port=url.port
)



def create_app():
#create_app is a keyword.
	app= Flask("pim")
	app.config.from_mapping(
		DATABASE= "pimdb"
	)
		
	@app.route("/")
	def index():
		return "hello"
		
	
	@app.route("/login")
	def loginpage():
		cursor = dbconn.cursor()
		username= 'navenBIGD'
		name='NAVEEN'
		password='1234567'
		cursor.execute("SELECT id,pwd from users where uname=%s",(username,))
		temp= cursor.fetchone()
		
		if temp:
			deets,passcode=temp
			if passcode==password:
				return "Sett."
			else:
				return "Wrong Passcode."
		else:
			return "Please complete the registration."
				

	
	@app.route("/register")
	def registration():
		cursor = dbconn.cursor()
		username= 'naveenBIGD'
		name='NAVEEN'
		password='1234567'
		cursor.execute("INSERT INTO users (name, uname, pwd) VALUES(%s, %s, %s)",(name, username, password))
		dbconn.commit()
		return "details entered"
	
	return app	

