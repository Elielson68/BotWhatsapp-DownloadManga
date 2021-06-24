from flask import Flask, request, redirect, url_for, send_from_directory
import requests
from twilio.twiml.messaging_response import MessagingResponse
import os
import random
from manga import MangaDown
from selenium.webdriver.firefox.options import Options
app = Flask(__name__)
firefox_options = Options()
firefox_options.add_argument('--no-sandbox')
firefox_options.add_argument('--disable-dev-shm-usage')
manga = MangaDown(firefox_options)

@app.route('/')
def home():
  return "<h1>Tudo funcionado por aqui!</h1>"

@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    if incoming_msg.startswith("!manga"):
      if "ult_cap" in incoming_msg:
        msg = resp.message()
        msg.body(manga.ultimo_capitulo(incoming_msg))
      if "escolher_manga" in incoming_msg:
        manga_name = manga.escolher_capitulo(incoming_msg)
        msg = resp.message("All done!")
        msg.media("https://whatsappbot.elielsonfernan1.repl.co/baixar/"+manga_name)
    else:
      resp.message().body("Oi")
    return str(resp)

@app.route("/baixar/<manga>")
def baixar(manga):
  print(os.getcwd()+"/static")
  return send_from_directory(os.getcwd()+"/static", filename=manga, as_attachment=True)
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)

