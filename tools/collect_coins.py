# -*- coding: utf-8 -*-

import config
import pymysql
import time
import traceback
import datetime
import requests
import json


class sql(object):
    def __init__(self):
        self.db = pymysql.connect('111.231.142.150',
                                  config.mql_user,
                                  config.mql_pswd,
                                  config.mql_db,
                                  charset="utf8")
        self.collect_coins()

    def collect_coins(self):
        # filename = "temp.json"
        url = "https://api.coinmarketcap.com/v2/ticker/?convert=cny&limit=100&"
        start = 1
        coin = 1
        try:
            for start in range(1635, 1700, 100):
                re_url = url + 'start=' + str(start)
                rank_data = requests.get(re_url).json()['data']
                print(rank_data)
                for coin in list(rank_data.values()):
                    if coin['max_supply'] == None:
                        sql = "insert into coin_info(id, full_name, symbol, \
                            rank) values (%d, '%s', '%s', %d)" % (
                            int(coin['id']), coin['name'], coin['symbol'],
                            int(coin['rank']))
                    else:
                        sql = "insert into coin_info(id, full_name, symbol, \
                                                rank, max_supply) values (%d, '%s', '%s', %d, %d)" % (
                            int(coin['id']), coin['name'], coin['symbol'],
                            int(coin['rank']), int(coin['max_supply']))


                    cursor = self.db.cursor()
                    cursor.execute(sql)
                    cursor.close()
                    self.db.commit()
                    print(coin['id'], coin['name'])

        except BaseException as e:
            print(e)
            print(coin)
            print(start)

sql()

