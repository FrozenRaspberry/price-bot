import hmac
import base64
import requests
import json
import time
import datetime
from telegram_lib import *
from keys import *
sendMessage('ok pd order start.')
lastMessageId = 0

if (need_proxy):
	proxies = {'https': 'http://127.0.0.1:7890'}
else:
	proxies = {}

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
	pdOrders = {}
	endpoint= '/api/v5/trade/orders-pending'
	url = okx_base_url + endpoint
	headers = get_header(endpoint)
	try:
		r = requests.get(url, headers=headers, proxies=proxies)
		r_data = r.json()
		#instId,px,sz,ordType,side
		if (r_data['code'] == '0'):
			for o in r_data['data']:
				pdOrders[o['ordId']] = o
		else:
			return None
	except Exception as e:
		print('!EXCEPTION\n', e)
		return None
	return pdOrders

def showOrders(orders):
	for orderId in orders:
		order = orders[orderId]
		print(order['instId'], order['ordType'], order['side'], order['px'], order['sz'])
		sendMessage(orderToString(order))

def orderToString(order):
	return order['instId'] + ' ' +  order['ordType'] + ' ' +  order['side'] + ' ' +  order['px'] + ' ' +  order['sz']

def checkOpenOrderDiff(newOrders):
	#check new order
	for newOrderId in newOrders:
		if (orderData.get(newOrderId) == None):
			orderData[newOrderId] = newOrders[newOrderId]
			sendMessage('新订单: ' + orderToString(newOrders[newOrderId]))
	#check if order is same
	if (len(orderData) == len(newOrders)):
		return
	#delete filled order
	orderToDelete = []
	for oldOrderId in orderData:
		if (newOrders.get(oldOrderId) == None):
			sendMessage('订单消失: ' + orderToString(orderData[oldOrderId]))
			orderToDelete.append(oldOrderId)
	for orderId in orderToDelete:
		orderData.pop(orderId)


tickCount = 0
orderData = GetPendingOrders()
sendMessage(str(len(orderData)) + ' pending orders')
showOrders(orderData)
lastMessageId = bot.get_updates()[-1].message.message_id
print('init msg id' + str(lastMessageId))

while True:
	newOrders = GetPendingOrders()
	if newOrders is None:
		time.sleep(1)
		print('Get order failed')
		continue
	checkOpenOrderDiff(newOrders)
	message = bot.get_updates()[-1].message
	if (lastMessageId != message.message_id):
		lastMessageId = message.message_id
		sendMessage('receive command: ' + message.text)
		showOrders(orderData)
	time.sleep(1)
	# print('----------------------',tickCount)
	tickCount += 1
