import hmac
import base64
import requests
import json
import time
import datetime
from telegram_lib import *
from keys import *

tgTestMode = False
sendMessage('ok pd order start.', test = tgTestMode)
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

#处理普通未成交订单
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
		print('!Get Order Error: ', e)
		return None
	return pdOrders

def showOrders(orders):
	for orderId in orders:
		order = orders[orderId]
		print(order['instId'], order['ordType'], order['side'], order['px'], order['sz'])
		sendMessage(orderToString(order), test = tgTestMode)

def orderToString(order):
	return order['instId'] + ' ' +  order['ordType'] + ' ' +  order['side'] + ' ' +  order['px'] + ' ' +  order['sz']

def checkOpenOrderDiff(newOrders):
	#check new order
	for newOrderId in newOrders:
		if (orderData.get(newOrderId) == None):
			orderData[newOrderId] = newOrders[newOrderId]
			sendMessage('新订单: ' + orderToString(newOrders[newOrderId]), test = tgTestMode)
	#check if order is same
	if (len(orderData) == len(newOrders)):
		return
	#delete filled order
	orderToDelete = []
	for oldOrderId in orderData:
		if (newOrders.get(oldOrderId) == None):
			sendMessage('订单消失: ' + orderToString(orderData[oldOrderId]), test = tgTestMode)
			orderToDelete.append(oldOrderId)
	for orderId in orderToDelete:
		orderData.pop(orderId)

#处理条件订单
def GetPendingConditionalOrders():
	pdConditionalOrders = {}
	endpoint= '/api/v5/trade/orders-algo-pending?ordType=conditional'
	url = okx_base_url + endpoint
	headers = get_header(endpoint)
	try:
		r = requests.get(url, headers=headers, proxies=proxies)
		r_data = r.json()
		# print(r_data)
		if (r_data['code'] == '0'):
			for o in r_data['data']:
				pdConditionalOrders[o['algoId']] = o
		else:
			return None
	except Exception as e:
		print('!Get pd conditional Order Error: ', e)
		return None
	return pdConditionalOrders

def showConditionalOrders(orders):
	for algoId in orders:
		order = orders[algoId]
		print(ConditionalOrderToString(order))
		sendMessage(ConditionalOrderToString(order), test = tgTestMode)

def ConditionalOrderToString(order):
	result = order['instId'] + ' ' +  order['ordType'] + ' ' +  order['side'] + ' '
	result += '触发价 ' + order['tpTriggerPx'] + '  下单价 ' + order['tpOrdPx'] + ' ' +  order['sz'] + ' '
	return result

def checkConditionalOrderDiff(newOrders):
	#check new order
	for newOrderId in newOrders:
		if (conditionalOrderData.get(newOrderId) == None):
			conditionalOrderData[newOrderId] = newOrders[newOrderId]
			sendMessage('新条件订单: ' + ConditionalOrderToString(newOrders[newOrderId]), test = tgTestMode)
	#check if order is same
	if (len(conditionalOrderData) == len(newOrders)):
		return
	#delete filled order
	orderToDelete = []
	for oldOrderId in conditionalOrderData:
		if (newOrders.get(oldOrderId) == None):
			sendMessage('条件订单消失: ' + ConditionalOrderToString(conditionalOrderData[oldOrderId]), test = tgTestMode)
			orderToDelete.append(oldOrderId)
	for orderId in orderToDelete:
		conditionalOrderData.pop(orderId)


#处理OCO订单
def GetPendingOcoOrders():
	pdOcoOrders = {}
	endpoint= '/api/v5/trade/orders-algo-pending?ordType=oco'
	url = okx_base_url + endpoint
	headers = get_header(endpoint)
	try:
		r = requests.get(url, headers=headers, proxies=proxies)
		r_data = r.json()
		# print(r_data)
		if (r_data['code'] == '0'):
			for o in r_data['data']:
				pdOcoOrders[o['algoId']] = o
		else:
			return None
	except Exception as e:
		print('!Get pd oco Order Error: ', e)
		return None
	return pdOcoOrders

def showOcoOrders(orders):
	for algoId in orders:
		order = orders[algoId]
		print(OcoOrderToString(order))
		sendMessage(OcoOrderToString(order), test = tgTestMode)

def OcoOrderToString(order):
	result = order['instId'] + ' ' +  order['ordType'] + ' ' +  order['side'] + ' '
	result += '触发价 ' + order['tpTriggerPx'] + '  下单价 ' + order['tpOrdPx'] + ' ' +  order['sz'] + ' '
	result += '触发价 ' + order['slTriggerPx'] + '  下单价 ' + order['slOrdPx'] + ' ' +  order['sz'] + ' '
	return result

def checkOcoOrderDiff(newOrders):
	#check new order
	for newOrderId in newOrders:
		if (ocoOrderData.get(newOrderId) == None):
			ocoOrderData[newOrderId] = newOrders[newOrderId]
			sendMessage('新OCO订单: ' + OcoOrderToString(newOrders[newOrderId]), test = tgTestMode)
	#check if order is same
	if (len(ocoOrderData) == len(newOrders)):
		return
	#delete filled order
	orderToDelete = []
	for oldOrderId in ocoOrderData:
		if (newOrders.get(oldOrderId) == None):
			sendMessage('OCO订单消失: ' + OcoOrderToString(ocoOrderData[oldOrderId]), test = tgTestMode)
			orderToDelete.append(oldOrderId)
	for orderId in orderToDelete:
		ocoOrderData.pop(orderId)



tickCount = 0
orderData = GetPendingOrders()
sendMessage(str(len(orderData)) + '笔未成交限价单', test = tgTestMode)
showOrders(orderData)

conditionalOrderData = GetPendingConditionalOrders()
sendMessage(str(len(conditionalOrderData)) + '笔条件订单', test = tgTestMode)
showConditionalOrders(conditionalOrderData)

ocoOrderData = GetPendingOcoOrders()
sendMessage(str(len(ocoOrderData)) + '笔OCO订单', test = tgTestMode)
showOcoOrders(ocoOrderData)

if not tgTestMode:
	lastMessageId = bot.get_updates()[-1].message.message_id
	print('init msg id' + str(lastMessageId))

while True:
	newOrders = GetPendingOrders()
	if newOrders is None:
		time.sleep(1)
		print('Get order failed')
		continue
	checkOpenOrderDiff(newOrders)

	newOrders = GetPendingConditionalOrders()
	if newOrders is None:
		time.sleep(1)
		print('Get conditional order failed')
		continue
	checkConditionalOrderDiff(newOrders)

	newOrders = GetPendingOcoOrders()
	if newOrders is None:
		time.sleep(1)
		print('Get OCO order failed')
		continue
	checkOcoOrderDiff(newOrders)

	if not tgTestMode:
		try:
			message = bot.get_updates()[-1].message
			if (lastMessageId != message.message_id):
				lastMessageId = message.message_id
				sendMessage('receive command: ' + message.text, test = tgTestMode)
				showOrders(orderData)
				showConditionalOrders(conditionalOrderData)
				showOcoOrders(ocoOrderData)
		except Exception as e:
			print('!Update message error: ', e)
	time.sleep(1)
	# print('----------------------',tickCount)
	tickCount += 1
