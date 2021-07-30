import psycopg2
import urllib.parse as up

from flask import Flask,g,request
from flask import render_template,jsonify
from flask_cors import CORS,cross_origin
from datetime import date

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
	app= Flask(__name__)
	#CORS(app)
	app.config.from_mapping(
		DATABASE= "pimdb"
	)

#########################################################################################################################
		
	@app.route("/")
	#@cross_origin()
	def index():
		response = jsonify(message="Simple server is running")
		return response
		
#########################################################################################################################		
		
	@app.route("/login", methods=["POST"])
	#@cross_origin())
	def loginpage():
		cursor = dbconn.cursor()
		#print('haha')
		#print(request.form)
		
		username= request.json['username']
		password= request.json['password']
		cursor.execute("SELECT id,pwd,name from users where uname=%s",(username,))
		temp= cursor.fetchone()
		if temp:
			deets,passcode,names=temp
			if passcode==password:
				return jsonify({"id":deets,"name":names,"username":username,"password":password})
			else:
				return jsonify(message="Incorrect password")
		else:
			return jsonify(message="Complete the registration")

#########################################################################################################################

	@app.route("/register", methods=["POST"])
	def registration():
		cursor = dbconn.cursor()
		name= request.json['name']
		username= request.json['username']
		password= request.json['password']
		cursor.execute("INSERT INTO users (name, uname, pwd) VALUES(%s, %s, %s)",(name, username, password))
		dbconn.commit()
		
		cursor = dbconn.cursor()
		cursor.execute("SELECT MAX(id) from users")
		userid= cursor.fetchall()[0][0]
		dbconn.commit()
		
		return jsonify({"id":userid,"name":name,"username":username,"password":password})
	
#########################################################################################################################	
	
	@app.route("/fillnote", methods=["POST"])
	def fillnotes():
		cursor = dbconn.cursor()
		dated=str(date.today())
		userid= request.json['id']
		ntitle= request.json['title']
		description= request.json['description']
		hashtag_ids= request.json['hashtags']
		hash_id=[v.strip() for v in hashtag_ids.split(',')]
		
				
		cursor.execute("INSERT INTO notes (title,dcp,dates,hids,uid) VALUES(%s, %s, %s, %s, %s)",(ntitle, description, dated, hashtag_ids, userid))
		dbconn.commit()
		
		#to get notesid 
		cursor = dbconn.cursor()
		cursor.execute("SELECT MAX(nid) from notes where uid=%s",(userid,))
		notesid= cursor.fetchall()[0][0]
		dbconn.commit()
		
		hashidlist=[]
		
		for hashes in hash_id:	
				cursor = dbconn.cursor()
				
				cursor.execute("INSERT INTO hashtags (label,nid,uid) SELECT %s, %s, %s where NOT exists( select 1 from hashtags where label=%s)",(hashes, notesid, userid, hashes))
				dbconn.commit()
				cursor = dbconn.cursor()
				cursor.execute("SELECT hid from hashtags where label=%s and uid=%s",(hashes,userid))
				hashids= cursor.fetchall()[0][0]
				
				hashidlist.append(hashids)
				dbconn.commit()
		
		
		return jsonify({"notesid":notesid, "title":ntitle, "description":description, "date":dated, "hashtags":hashtag_ids, "hashtagids": hashidlist ,"id":userid})

#########################################################################################################################

	@app.route("/getallnotes", methods=["GET"])
	def getnotes():
		cursor = dbconn.cursor()
		userid= request.json['id']		
		
		cursor.execute("SELECT nid,title,dcp,dates,hids from notes where uid= %s",(userid,))
		temp= cursor.fetchall()
		
		result=[]
		for notesid,ntitle,description,dated,hashtag_ids in temp:
				dicts={"notesid":notesid, "title":ntitle, "description":description, "date":dated, "hashtags":hashtag_ids,"id":userid}
				result.append(dicts)
	
		return jsonify(result)

#########################################################################################################################
		
	@app.route("/update", methods=["PUT"])
	def updatenote():
		dated=str(date.today())
		cursor = dbconn.cursor()
		userid= request.json['id']
		notesid= request.json['notesid']
		ntitle= request.json['title']
		description= request.json['description']
		hashtag_ids= request.json['hashtags']
		hash_id=[v.strip() for v in hashtag_ids.split(',')]
		
		
		cursor = dbconn.cursor()
		cursor.execute("UPDATE notes SET title=%s, dcp=%s, dates=%s, hids=%s where nid=%s and uid=%s",(ntitle, description, dated, hashtag_ids, notesid, userid))
		cursor.execute("DELETE FROM hashtags where nid=%s and uid=%s",(notesid, userid))
		dbconn.commit()
		
		hashidlist=[]
		for hashes in hash_id:	
				cursor = dbconn.cursor()
				cursor.execute("INSERT INTO hashtags (label,nid,uid) SELECT %s, %s, %s where NOT exists( select 1 from hashtags where label=%s)",(hashes, notesid, userid, hashes))
				dbconn.commit()
				cursor = dbconn.cursor()
				cursor.execute("SELECT hid from hashtags where label=%s and uid=%s",(hashes,userid))
				hashids= cursor.fetchall()[0][0]
				hashidlist.append(hashids)
				dbconn.commit()
		
		cursor = dbconn.cursor()
		cursor.execute("SELECT title,dcp,dates,hids from notes where nid= %s and uid=%s",(notesid,userid))
		values= cursor.fetchall()
		dbconn.commit()
		return jsonify({"notesid":notesid, "title":ntitle, "description":description, "date":dated, "hashtags":hashtag_ids, "hashtagids": hashidlist ,"id":userid})	
		
#########################################################################################################################		
				
	@app.route("/delete", methods=["DELETE"])
	def deletenote():
		cursor = dbconn.cursor()
		userid= request.json['id']
		notesid= request.json['notesid']
		
		cursor.execute("SELECT title,dcp,dates,hids from notes where uid= %s and nid=%s",(userid,notesid))
		temp= cursor.fetchone()
		ntitle,description,dated,hashtag_ids=temp
		dbconn.commit()
		
		cursor = dbconn.cursor()
		cursor.execute("SELECT hids from notes where uid= %s and nid=%s",(userid,notesid))
		hashidlist= cursor.fetchone()
		dbconn.commit()
		
		
		cursor = dbconn.cursor()
		cursor.execute("DELETE FROM hashtags where nid=%s and uid=%s",(notesid, userid))
		cursor.execute("DELETE FROM notes where nid=%s and uid=%s",(notesid, userid))
		dbconn.commit()
		return jsonify({"notesid":notesid, "title":ntitle, "description":description, "date":dated, "hashtags":hashtag_ids, "hashtagids": hashidlist ,"id":userid})

#########################################################################################################################
	
	@app.route("/hashtags", methods=["GET"])
	def gethashtags():
		cursor = dbconn.cursor()
		userid= request.json['id']
		cursor.execute("SELECT hid,label from hashtags where uid= %s",(userid,))
		values= cursor.fetchall()
		dbconn.commit()
		result=[]
		for hashid,hashes in values:
			dicts={"hashtagid":hashid, "hashtag":hashes}
			result.append(dicts)
		
		return jsonify(result)		
	
	return app	

