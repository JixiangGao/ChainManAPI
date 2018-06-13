# -*- coding: utf-8 -*-

import json
import config
import pymysql
import requests
import time


def connection():
    return pymysql.connect(config.mql_url,
                           config.mql_user,
                           config.mql_pswd,
                           config.mql_db,
                           charset="utf8")


def get_ticker(conn):
    url = "https://api.coinmarketcap.com/v2/ticker/?convert=cny&limit=100&structure=array&"
    try:
        for start in range(1, 1700, 100):
            re_url = url + 'start=' + str(start)
            rank_data = requests.get(re_url).json()['data']
            for coin in rank_data:
                commit_to_database(coin, conn)
    except BaseException as e:
        print(e)


def commit_to_database(coin, conn):
    id, name, circulating_supply, price, volume_24h, \
    market_cap, pc1h, pc24h, pc7d, rank, last_updated = \
        coin['id'], coin['name'], coin['circulating_supply'], \
        coin['quotes']['CNY']['price'], coin['quotes']['CNY']['volume_24h'], \
        coin['quotes']['CNY']['market_cap'], coin['quotes']['CNY']['percent_change_1h'], \
        coin['quotes']['CNY']['percent_change_24h'], coin['quotes']['CNY']['percent_change_7d'], \
        coin['rank'], coin['last_updated']

    last_updated_array = time.localtime(last_updated)
    last_updated_time = time.strftime("%Y-%m-%d %H:%M:%S", last_updated_array)

    sql = "insert into coin_current(id, full_name, circulating_supply, price, volume_24h, \
        market_cap, percent_change_1h, percent_change_24h, percent_change_7d, rank, last_updated) \
        values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
        id, name, circulating_supply, price, volume_24h, market_cap, pc1h, pc24h, pc7d, rank, last_updated_time
    )

    try:
        cur = conn.cursor()
        cur.execute(sql)
        cur.close()
        conn.commit()
        print(name)
    except Exception as e:
        print(id, name, '-------------')
        print(e)


while True:
    try:
        conn = connection()
        get_ticker(conn)
    except BaseException as e:
        print(e)
        traceback.print_exc()
    finally:
        # time.sleep(5)
        for i in range(60*24):
            ######
            time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print(time_now, "remain %dm" % (60*24 - i))
            time.sleep(60)



