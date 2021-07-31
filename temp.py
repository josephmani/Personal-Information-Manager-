import psycopg2
import urllib.parse as up

from flask import Flask,g,request
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


cursor = dbconn.cursor()
cursor.execute("select * from hashtags")
values= cursor.fetchall()
for i in values:
    for j in i:
        print(j,end=" - ")
    print('\n')
dbconn.commit()