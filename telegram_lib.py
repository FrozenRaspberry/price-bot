import telegram
from telegram import Update
from telegram.ext import filters, MessageHandler, ContextTypes

from keys import *

if (need_proxy):
	pp = telegram.utils.request.Request(proxy_url='https://127.0.0.1:7890')
	bot = telegram.Bot(token=tg_api_key, request=pp)
else:
	bot = telegram.Bot(token=tg_api_key)

def sendMessage(msg, log = True, test = False):
	if log:
		print('Send msg: ' + msg)
	if not test:
		bot.send_message(chat_id, text=msg)
