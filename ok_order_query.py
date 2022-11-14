import hmac
import base64
import requests
import json
import time
import datetime
from telegram_lib import sendMessage
from keys import *
sendMessage('ok pd order start.')


proxies = {
   'https': 'http://127.0.0.1:7890'
}

def get_time():
	now = datetime.datetime.utcnow()
	t = now.isoformat("T", "milliseconds")
	return t + "Z"

def signature(timestamp, method, request_path, body,secret_key):
	if str(body) == '{}' or str(body) == 'None':
		body = ''
	message = str(timestamp) + str.upper(method) + request_path + str(body)
	mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
	d = mac.digest()
	return base64.b64encode(d)

def get_header(endpoint):
	body= {}
	request= 'GET'
	header = dict()
	header['CONTENT-TYPE'] = 'application/json'
	header['OK-ACCESS-KEY'] = okx_api_key
	current_time = get_time()
	header['OK-ACCESS-SIGN'] = signature(current_time, request, endpoint , body, okx_api_secret)
	header['OK-ACCESS-TIMESTAMP'] = str(current_time)
	header['OK-ACCESS-PASSPHRASE'] = okx_api_pass
	return header

def GetPendingOrders():
	endpoint= '/api/v5/trade/orders-pending'
	url = okx_base_url + endpoint
	headers = get_header(endpoint)
	try:
		r = requests.get(url, headers=headers, proxies=proxies)
		r_data = r.json()
		#instId,px,sz,ordType,side
		if (r_data['code'] == '0'):
			return r_data['data']
	except Exception as e:
		print('!EXCEPTION\n', e)
		print(r)

def showOrders(orders):
	for order in orders:
		print(order['ETH-USDT-SWAP'], order['type'], order['side'], order['px'], order['sz'])

def checkOrderDiff(orders):
	for order in orders:
		print(order['ETH-USDT-SWAP'], order['type'], order['side'], order['px'], order['sz'])


tickCount = 0
orderData = GetPendingOrders()
sendMessage(str(len(orderData)) + ' pending orders')
showOrders(orderData)
while True:


	time.sleep(2)
	print('----------------------',tickCount)
	tickCount += 1
