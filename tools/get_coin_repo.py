# -*- coding: utf-8 -*-

import requests
import json
import re

'''
    2018/6/2
    获取了coinmarketcap_info.json中前1260个coin的repo
    保存在coin_repo0.json中
'''

def get_repo(coin_info):
    # slug, name, short = get_coin_website_slug()
    url = "https://coinmarketcap.com/currencies/"
    data = []

    try:
        for i in range(0, len(coin_info)):
            coin = coin_info[i]['website_slug']
            full = coin_info[i]['name']
            s_n = coin_info[i]['symbol']
            coin_url = url + coin
            from urllib.request import urlopen
            html = urlopen(coin_url)
            content = html.read().decode('utf-8')
            searchObj = re.search(r'"(.*)github.com/(.*?) .*"', content, re.M | re.I)

            if searchObj is not None:
                arr = {}
                arr['coin_full_name'] = full
                arr['coin_short_name'] = s_n
                arr['coin_repo'] = searchObj.group(2)[:-1]
                print(i + 1, coin, 'yes')
            else:
                arr = {}
                arr['coin_full_name'] = full
                arr['coin_short_name'] = s_n
                arr['coin_repo'] = '------------------------------'
                print(i + 1, coin, '------------------------------')
            data.append(arr)
            # if i % 100 == 0:
            #     # print(data)
    except Exception as e:
        print(e)
        return None
    return data


def get_coin_website_slug():
    '''
    get coins' name, symbol and website_slug, 
    save to coinmarketcap_info.json
    :return: 
    '''
    filename = "coinmarketcap_info.json"
    url = "https://api.coinmarketcap.com/v2/ticker/?convert=cny&limit=100&"
    info = []

    for start in range(1, 1700, 100):
        re_url = url + 'start=' + str(start)
        rank_data = requests.get(re_url).json()['data']

        for coin in list(rank_data.values()):
            # print(coin['website_slug'])
            coin_info = {}
            coin_info['website_slug'] = coin['website_slug']
            coin_info['name'] = coin['name']
            coin_info['symbol'] = coin['symbol']
            info.append(coin_info)

    file = open(filename, "w")
    file.write(json.dumps(info))
    file.close()



filename = 'coinmarketcap_info.json'
file = open(filename, "r")
coin_data = json.load(file)
file.close()

all_repo_info = []

for i in range(1260, len(coin_data), 10):
    print(i)
    if i+10 < len(coin_data):
        right_pointer = i+10
    else:
        right_pointer = len(coin_data)

    repo_info = get_repo(coin_data[i:right_pointer])
    if repo_info is not None:
        # all_repo_info.update(repo_info)
        all_repo_info = all_repo_info + repo_info
        file = open("coin_repo.json", "w")
        file.write(json.dumps(all_repo_info))
        file.close()
    else:
        break




# data = get_repo()
#
# file = open("coin_repo.json", "w")
# file.write(json.dumps(data))
# file.close()
# print(data)


# get_coin_website_slug()
