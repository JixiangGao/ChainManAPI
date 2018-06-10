# -*- coding: utf-8 -*-

import json
import sys
import config
import pymysql

filename = './coinmarketcap_info.json'
file = open(filename, "r")
data = json.load(file)
file.close()

info = config.info

result = {}
print (111)

for coin in info:
    l_coin = coin['coin_full_name'].lower()
    flag = 0
    for i in data:
        if i['name'].lower() == l_coin:
            flag = 1
            if i['name'] == coin['coin_full_name']:
                continue
            else:
                result[coin['coin_full_name']] = i['name']
                print(coin['coin_full_name'], i['name'])
    if flag == 0:
        print('Not find', coin['coin_full_name'])


connect = pymysql.connect('111.231.142.150',
                            'chainman',
                            'cman123..',
                            'chainman',
                            charset="utf8")

for record in result:
    try:
        # print(record)
        sql = "update personal_coins set coin='%s' where coin='%s'" % (
            result[record], record)
        cursor = connect.cursor()
        cursor.execute(sql)
        print("update '%s' to '%s'" % (record, result[record]))
        cursor.close()
        connect.commit()
    except Exception as e:
        print(e)
        print('error "%s"' % record)
