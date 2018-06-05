# -*- coding: utf-8 -*-

import config
import pymysql
import traceback
import requests
import json


class sql(object):
    def __init__(self):
        self.db = pymysql.connect('111.231.142.150',
                                  config.mql_user,
                                  config.mql_pswd,
                                  config.mql_db,
                                  charset="utf8")
        print("database connect success!")
        self.collect_coins()

    def collect_coins(self):
        # filename = "temp.json"
        url = "https://api.coinmarketcap.com/v2/listings/"
        coin = 1

        data = requests.get(url).json()['data']
        print("get coinmarketcap.com data success!")
        for coin in data:
            sql = "insert into coin_info(id, full_name, symbol, website_slug \
                ) values (%d, %s, %s, %s)" % (
                int(coin['id']),
                self.db.escape(coin['name']),
                self.db.escape(coin['symbol']),
                self.db.escape(coin['website_slug']))

            cursor = self.db.cursor()
            cursor.execute(sql)
            cursor.close()
            self.db.commit()
            print(coin['id'], coin['name'])

sql()

