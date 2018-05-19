# -*- coding: utf-8 -*-

import pymysql
import time
import traceback
import datetime
import requests
import json

#starttime = datetime.datetime.now()

def save_ticker_to_file():
	filename = "temp.json"
	url = "https://api.coinmarketcap.com/v2/ticker/?convert=cny&limit=100&"
	start = 1
	data = {}
	try:
		for start in range(1, 201, 100):
			re_url = url + 'start=' + str(start)
			rank_data = requests.get(re_url).json()['data']
			data.update(rank_data)
	except BaseException as e:
		data = {}
		print("error")
	file = open(filename, "w")
	file.write(json.dumps(data))
	file.close()

#endtime = datetime.datetime.now()
#print((endtime - starttime))

while True:
    try:
        save_ticker_to_file()
    except BaseException as e:
        print(e)
        traceback.print_exc()
    finally:
        # time.sleep(5)
        for i in range(10):
            ######
            time_now = time.strftime('%Y-%m-%d %H:%M:%S',
                                     time.localtime(time.time()))
            print(time_now, "ramain %dm" % (10 - i))
            time.sleep(600)

