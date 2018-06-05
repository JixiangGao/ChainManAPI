# -*- coding: utf-8 -*-

import config
import pymysql
import traceback
import requests
import json

'''
    2018/6/2
    将coin_repo0.json中的repo信息保存到数据库
    总共1260条
    没有repo信息的存为unknown
'''


filename = './coin_repo0.json'
file = open(filename, "r")
data = json.load(file)
file.close()

db = pymysql.connect('111.231.142.150',
                                  config.mql_user,
                                  config.mql_pswd,
                                  config.mql_db,
                                  charset="utf8")
print("database connect success!")

count = 0

for coin in data:
    name = db.escape(coin['coin_full_name'])
    short_name = db.escape(coin['coin_short_name'])
    repo = db.escape(coin['coin_repo'])
    count += 1
    if coin['coin_repo'] == '------------------------------':
        repo = db.escape('unknown')
        count -= 1

    sql = "update coin_info set github_repo = %s \
        where full_name=%s and symbol=%s" % (repo, name, short_name)

    cursor = db.cursor()
    cursor.execute(sql)
    cursor.close()
    db.commit()
    print(name, count)
