import telegram
import socks
from keys import *

pp = telegram.utils.request.Request(proxy_url='https://127.0.0.1:7890')
bot = telegram.Bot(token=tg_api_key, request=pp)

def sendMessage(msg, log = True):
	if (log):
		print('Send msg: ' + msg)
	bot.send_message(chat_id, text=msg)