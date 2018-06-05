# -*- coding: utf-8 -*-

import json
import sys
sys.path.append("..")
import config

filename = './coin_repo0.json'
file = open(filename, "r")
data = json.load(file)
file.close()

info = config.info
count = 0

for coin in data:
    coin_name = coin['coin_full_name'].lower()
    flag = 0
    for i in info:
        if coin_name == i['coin_full_name'].lower():
            flag = 1
            break
    if flag == 1:
        continue
    if coin['coin_repo'] == '------------------------------':
        continue

    # 仅查询包含/的项目
    if '/' in  coin['coin_repo']:
        count += 1
        print(("{'coin_short_name': '%s', 'coin_full_name': '%s', 'repo_name': '%s'},") %(coin['coin_short_name'], coin['coin_full_name'], coin['coin_repo']))

    # 只找其中200个
    if count == 200:
        break

print(count)
