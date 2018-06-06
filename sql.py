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
        self.db = pymysql.connect(config.mql_url,
                                  config.mql_user,
                                  config.mql_pswd,
                                  config.mql_db,
                                  charset="utf8")

    def db_close(self):
        self.db.close()

    def get_coins(self, params):
        commit_num = 10
        if 'commit_num' in params:
            commit_num = int(params['commit_num'])

        try:
            cursor = self.db.cursor()
            all_results = {}
            for coin_info in config.info:
                coin = coin_info["coin_full_name"]
                sql_get_coins = \
                    "select coin, repo_name, additions, deletions, total, \
                        collect_time, author, committer, create_time, \
                        commit_time, html_url, commit_sha, content \
                    from repo_commits \
                    where coin = '%s' \
                    order by commit_time desc limit 0,%d" % (
                        coin, commit_num)
                cursor.execute(sql_get_coins)
                coin_results = []
                for i in range(cursor.rowcount):
                    record = cursor.fetchone()
                    coin_result = {}

                    coin_result['coin'] = record[0]
                    coin_result['repo_name'] = record[1]
                    coin_result['additions'] = record[2]
                    coin_result['deletions'] = record[3]
                    coin_result['total'] = record[4]
                    coin_result['collect_time'] = record[5]
                    coin_result['author'] = record[6]
                    coin_result['committer'] = record[7]
                    coin_result['create_time'] = record[8]
                    coin_result['commit_time'] = record[9]
                    coin_result['html_url'] = record[10]
                    coin_result['commit_sha'] = record[11]
                    coin_result['content'] = record[12]

                    coin_results.append(coin_result)

                all_results[coin] = coin_results

            cursor.close()
            return {"code": 1000, "success": True, "message": "get coins successfully", "data": all_results}
        except BaseException as e:
            print(e)
            return {"code": 2001, "success": False, "message": "get coins error", "data": None}

    def get_commits_num(self, params):
        if 'period' in params:
            period = int(params['period'])
        else:
            period = 7

        # now_time = datetime.datetime.now()
        # yes_time = now_time + datetime.timedelta(days=(0-period))
        # str_yes = yes_time.strftime('%Y-%m-%d %H:%M:%S')

        sql_cmt_num = \
            "select coin, count(*), sum(additions), sum(deletions), sum(total) \
            from repo_commits \
            where TO_DAYS(now()) - TO_DAYS(commit_time) < %d \
            group by coin " % period

        try:
            cursor = self.db.cursor()
            cursor.execute(sql_cmt_num)
            results = {}
            for i in range(cursor.rowcount):
                record = cursor.fetchone()

                result = {}
                result['commits_num'] = int(record[1])
                result['additions'] = int(record[2])
                result['deletions'] = int(record[3])
                result['total'] = int(record[4])

                results[record[0]] = result

            cursor.close()
            return {"code": 1000, "success": True, "message": "get commits num successfully", "data": results}
        except BaseException as e:
            print(e)
            return {"code": 2002, "success": False, "message": "get commits num error", "data": None}

    def get_last(self, params):
        sql_get_last = ""  # 完整的sql语句
        sql_where_condition = ""  # sql语句中where子句
        sql_dateformat = ""  # select语句中date部分
        result_dict = {}
        loop_times = 8  # week的looptime
        period = ""
        if 'period' in params:
            period = str(params['period'])
            if period == 'day':
                loop_times = 30
            elif period == 'month':
                loop_times = 6
        else:
            period = "week"

        for i in range(1, loop_times + 1):
            if period == 'week':
                sql_where_condition = "YEARWEEK(date_format(commit_time,'%%Y-%%m-%%d'),1) = YEARWEEK(now(),1)- %d" % i
                sql_dateformat = "WEEK(date_format(max(commit_time),'%Y-%m-%d'))"
            elif period == 'month':
                sql_where_condition = "date_format(commit_time, '%%Y %%m') = date_format(DATE_SUB(curdate(), INTERVAL %d MONTH),'%%Y %%m')" % i
                sql_dateformat = "date_format(max(commit_time), '%Y-%m')"
            elif period == 'day':
                sql_where_condition = "TO_DAYS( NOW( ) ) - TO_DAYS( commit_time) = %d" % i
                sql_dateformat = "date_format(max(commit_time), '%Y-%m-%d')"  # 待验证

            if 'coin' in params:
                coin = params['coin']
                sql_get_last = \
                    "select coin, count(*), sum(additions), sum(deletions), sum(total),  %s\
                    from repo_commits \
                    WHERE %s \
                    AND coin = '%s'" % (sql_dateformat, sql_where_condition, coin)
            else:
                sql_get_last = \
                    "select coin, count(*), sum(additions), sum(deletions), sum(total), %s \
                    from repo_commits \
                    WHERE %s \
                    group by coin " % (sql_dateformat, sql_where_condition)
            try:
                cursor = self.db.cursor()
                cursor.execute(sql_get_last)
                for j in range(cursor.rowcount):
                    record = cursor.fetchone()

                    result = {}  # result是单个period内，单个币种的字典

                    if not record[0]:  # 若没有查询结果会返回一行NULL，这里做一个安全检查
                        break
                    result['commits_num'] = int(record[1])
                    result['additions'] = int(record[2])
                    result['deletions'] = int(record[3])
                    result['total'] = int(record[4])

                    if period == 'week':
                        week_num = int(record[5])
                        week_num += 1
                        result['week'] = week_num
                    elif period == 'month':
                        result['month'] = record[5]
                    elif period == 'day':
                        result['day'] = record[5]
                    if record[0] in result_dict:
                        result_dict[record[0]].append(result)
                    else:
                        result_dict[record[0]] = []
                        result_dict[record[0]].append(result)

                cursor.close()
            except BaseException as e:
                print(e)
                return {"code": 2003, "success": False, "message": "从repo_commits获取数据时出错", "data": None}
        return {"code": 1000, "success": True, "message": "get_last成功", "data": result_dict}

    def get_rank(self, params):
        # wait to adj
        rank1_rate = 0.1
        rank2_rate = 0.1
        rank3_rate = 0.35
        rank4_rate = 0.35
        rank5_rate = 0.1

        sql_get_rank = \
            "select coin, count(*), sum(additions), sum(deletions), sum(total) \
            from repo_commits \
            where YEARWEEK(date_format(commit_time,'%Y-%m-%d'),1) = YEARWEEK(now(),1)- 1 \
            group by coin "

        if 'period' in params:
            if params['period'] == 'month':
                sql_get_rank = \
                    "select coin, count(*), sum(additions), sum(deletions), sum(total) \
                    from repo_commits \
                    where date_format(commit_time, '%%Y %%m') = date_format(DATE_SUB(curdate(), INTERVAL 1 MONTH),'%%Y %%m') \
                    group by coin "
            elif not params['period'] == 'week':
                return {"code": 2004, "success": False, "message": "参数错误", "data": None}

        try:
            cursor = self.db.cursor()
            cursor.execute(sql_get_rank)
            coins_dict = {}
            for i in range(cursor.rowcount):
                record = cursor.fetchone()

                result = {}
                result['commits_num'] = int(record[1])
                result['additions'] = int(record[2])
                result['deletions'] = int(record[3])
                result['total'] = int(record[4])

                coins_dict[record[0]] = result

            cursor.close()
        except BaseException as e:
            print(e)
            return {"code": 2005, "success": False, "message": "从repo_commits获取数据时出错", "data": None}

        return_dict = {}
        coin_total_dict = {}
        coins_list = coins_dict.keys()
        coins_num = len(coins_list)

        rank1_num = rank1_rate * coins_num
        rank12_num = (rank1_rate + rank2_rate) * coins_num
        rank123_num = (rank1_rate + rank2_rate + rank3_rate) * coins_num
        rank1234_num = (1 - rank5_rate) * coins_num

        coins_all_list = []
        for dict in config.info:
            coins_all_list.append(dict['coin_full_name'])

        for coinName in coins_list:
            return_dict[coinName] = 5
            coin_total_dict[coinName] = coins_dict[coinName]['commits_num']  # 这里也可以改成是commit数，或total数
        for coinName in coins_all_list:
            if coinName not in return_dict:
                return_dict[coinName] = 0

        coin_total_list = list(coin_total_dict.items())
        coin_total_list.sort(key=lambda x: x[1])
        for i in range(int(rank1234_num)):
            return_dict[coin_total_list[i][0]] -= 1
        for i in range(int(rank123_num)):
            return_dict[coin_total_list[i][0]] -= 1
        for i in range(int(rank12_num)):
            return_dict[coin_total_list[i][0]] -= 1
        for i in range(int(rank1_num)):
            return_dict[coin_total_list[i][0]] -= 1

        return {"code": 1000, "success": True, "message": "get rank成功", "data": return_dict}

    def sortDictByValue(self, dict):  # return a turple_list
        lst = list(dict.items())
        lst.sort(key=lambda x: x[1])
        lst.reverse()
        return lst

    def get_frequency(self, params):
        if 'coin' not in params:
            return {"code": 2018, "success": False, "message": "参数错误", "data": None}

        coin = params['coin']

        index_results = []
        value_results = []

        now = datetime.datetime.now()

        # days
        my_params = {'coin': coin, 'period': 'day'}
        day_return = self.get_last(my_params)
        if day_return['code'] == 1000:
            day_return = day_return['data']
        else:
            return {"code": 2019, "success": False, "message": "api执行错误", "data": None}
        index_result_day = []
        value_result_day = [0, 0, 0, 0, 0, 0, 0]
        for i in range(1, 8):
            day = now + datetime.timedelta(days=-i)
            day = datetime.datetime.strftime(day, "%Y-%m-%d")
            index_result_day.append(day)
        j = 0
        if len(list(day_return.values())) == 0:
            minn = 0
        else:
            minn = min(len(list(day_return.values())[0]), 7)
        for i in range(minn):
            key = list(day_return.keys())[0]
            if day_return[key][j]['day'] == index_result_day[i]:
                value_result_day[i] = day_return[key][j]['total']
                j += 1
        index_result_day.reverse()
        value_result_day.reverse()
        index_results.append(index_result_day)
        value_results.append(value_result_day)

        # weeks
        my_params = {'coin': coin, 'period': 'week'}
        day_return = self.get_last(my_params)
        if day_return['code'] == 1000:
            day_return = day_return['data']
        else:
            return {"code": 2019, "success": False, "message": "api执行错误", "data": None}
        index_result_day = []
        value_result_day = [0, 0, 0, 0]
        '''
            something wrong here
        '''
        # for i in range(1, 5):
        for i in range(4):
            week = int(datetime.datetime.strftime(now, "%W")) - i
            index_result_day.append(week)
        j = 0
        if len(list(day_return.values())) == 0:
            minn = 0
        else:
            minn = min(len(list(day_return.values())[0]), 4)
        for i in range(minn):
            key = list(day_return.keys())[0]
            if day_return[key][j]['week'] == index_result_day[i]:
                value_result_day[i] = day_return[key][j]['total']
                j += 1
        index_result_day.reverse()
        value_result_day.reverse()
        index_results.append(index_result_day)
        value_results.append(value_result_day)

        # months
        my_params = {'coin': coin, 'period': 'month'}
        day_return = self.get_last(my_params)
        if day_return['code'] == 1000:
            day_return = day_return['data']
        else:
            return {"code": 2019, "success": False, "message": "api执行错误", "data": None}
        index_result_day = []
        value_result_day = [0, 0, 0, 0, 0, 0]
        month = datetime.datetime.now()
        for i in range(1, 7):
            month = datetime.date(month.year, month.month, 1)
            month = month + datetime.timedelta(days=-1)
            month_tmp = datetime.datetime.strftime(month, "%Y-%m")
            index_result_day.append(month_tmp)
        j = 0
        if len(list(day_return.values())) == 0:
            minn = 0
        else:
            minn = min(len(list(day_return.values())[0]), 6)
        for i in range(minn):
            key = list(day_return.keys())[0]
            if day_return[key][j]['month'] == index_result_day[i]:
                value_result_day[i] = day_return[key][j]['total']
                j += 1
        index_result_day.reverse()
        value_result_day.reverse()
        index_results.append(index_result_day)
        value_results.append(value_result_day)

        result = [index_results, value_results]
        return {"code": 1000, "success": True, "message": "get frequency successfully", "data": result}

    def login(self, params):
        if 'code' not in params:
            return {"code": 2020, "success": False, "message": "获取code失败", "data": None}
        code = params['code']

        url = "https://api.weixin.qq.com/sns/jscode2session?appid=" + \
              config.appid + "&secret=" + config.secret + \
              "&js_code=" + code + "&grant_type=authorization_code"
        result = requests.get(url=url).json()

        urlStr1 = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + config.appid + "&secret=" + config.secret
        result1 = requests.get(url=urlStr1).json()
        accessToken = ""
        if 'access_token':
            accessToken = result1['access_token']
        else:
            return {"code": 2021, "success": False, "message": "获取access_token失败", "data": None}

        if 'openid' in result:
            openid = result['openid']

            urlStr2 = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=" + accessToken + "&openid=" + openid
            result2 = requests.get(url=urlStr2).json()
            nickname = ""
            # if 'nickname' in result2:
            #    nickname = result2['nickname']
            # print("nickname: "+nickname)
            # else:
            #    return {"code": 2022, "success": False, "message": "获取用户信息失败", "data": {'openid': openid}}

            try:
                sql = "INSERT INTO user_info (user_id, nickname) VALUES ('%s', '%s')" % (openid, nickname)
                sql_select = "SELECT user_id, nickname FROM user_info WHERE user_id = '%s'" % openid
                cursor = self.db.cursor()
                cursor.execute(sql_select)
                if cursor.rowcount > 0:
                    record = cursor.fetchone()
                    if record[0]:
                        if record[1] == nickname:
                            return {"code": 1000, "success": True, "message": "数据库存在该用户，无需更新，登录成功", "data": openid}
                        else:
                            sql = "UPDATE user_info SET nickname = '%s' WHERE user_id = '%s'" % (nickname, openid)
                cursor.close()

                cursor = self.db.cursor()
                cursor.execute(sql)
                self.db.commit()
                cursor.close()
            except BaseException as e:
                print(e)
            return {"code": 1000, "success": True, "message": "数据库更新成功， 登录成功", "data": {'openid': openid}}
        else:
            return {"code": 2023, "success": False, "message": "获取openid错误", "data": result}

    def get_personal_coins(self, params):
        coin_list = []
        if "user_id" not in params:
            return {"code": 2006, "success": False, "message": "参数错误", "data": None}
        sql = "select coin from personal_coins where user_id = '%s'" % params['user_id']
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            for j in range(cursor.rowcount):
                record = cursor.fetchone()
                if record[0]:
                    coin_list.append(record[0])
            cursor.close()
        except BaseException as e:
            print(e)
            return {"code": 2007, "success": False, "message": "从数据库获取自选币表时出错", "data": None}

        # ------- delete the errcode 2008 -------
        # if len(coin_list) == 0:
        #     return {"code": 2008, "success": False, "message": "该用户还没有自选的币", "data": None}

        return {"code": 1000, "success": True, "message": "成功获取自选币信息", "data": coin_list}

    def insert_personal_coin(self, params):
        if "user_id" not in params or "coin" not in params:
            return {"code": 2009, "success": False, "message": "参数错误", "date": None}
        sql_select = "select user_id, coin from personal_coins where user_id = '%s' and coin = '%s'" % (
            params['user_id'], params['coin'])
        sql_insert = "INSERT INTO personal_coins (user_id, coin, select_time) VALUES ('%s', '%s', NOW())" % (
            params['user_id'], params['coin'])
        try:
            cursor = self.db.cursor()
            cursor.execute(sql_select)
            if cursor.rowcount > 0:
                result = cursor.fetchone()
                if result[1]:
                    return {"code": 2010, "success": False, "message": "该币已经在数据库了", "data": None}
            cursor.close()
        except BaseException as e:
            print(e)
            return {"code": 2011, "success": False, "message": "从数据库获取自选币表时出错", "data": None}
        try:
            cursor = self.db.cursor()
            cursor.execute(sql_insert)
            self.db.commit()
            cursor.close()
        except BaseException as e:
            print(e)
            return {"code": 2012, "success": False, "message": "向数据库插入元组时出错", "data": None}
        return {"code": "1000", "success": True, "message": "插入成功", "data": params['coin']}

    def delete_personal_coin(self, params):
        if "user_id" not in params or "coin" not in params:
            return {"code": 2013, "success": False, "message": "参数错误", "date": None}
        sql_select = "select user_id, coin from personal_coins where user_id = '%s' and coin = '%s'" % (
            params['user_id'], params['coin'])

        sql_delete = "delete from personal_coins where user_id = '%s' and coin = '%s'" % (
            params['user_id'], params['coin'])
        try:
            cursor = self.db.cursor()
            cursor.execute(sql_select)
            if cursor.rowcount < 0:
                return {"code": 2014, "success": False, "message": "数据库没有此项", "data": None}
            else:
                result = cursor.fetchone()
                if not result[1]:
                    return {"code": 2015, "success": False, "message": "查找到值为null", "data": None}
            cursor.close()
        except BaseException as e:
            print(e)
            return {"code": 2016, "success": False, "message": "从数据库获取自选币表时出错", "data": None}
        try:
            cursor = self.db.cursor()
            cursor.execute(sql_delete)
            self.db.commit()
            cursor.close()
        except BaseException as e:
            print(e)
            return {"code": 2017, "success": False, "message": "从数据库删除元组时出错", "data": params['coin']}
        return {"code": "1000", "success": True, "message": "删除成功", "data": params['coin']}

    def get_coins_list(self, params):
        if 'period' not in params or 'user_id' not in params:
            return {"code": 2024, "success": False, "message": "参数错误", "data": None}
        period = params['period']

        rank_result = self.get_rank({'period': period})
        if rank_result['code'] == 1000:
            data = rank_result['data']
        else:
            return rank_result
        data = self.sortDictByValue(data)
        coins_list = []

        full_short = {}
        for i in config.info:
            full_short[i['coin_full_name']] = i['coin_short_name']

        re = self.get_personal_coins(params)

        # ------- delete the errcode 2008 -------
        # if re['code'] == 1000:
        #     personal_coins = re['data']
        # elif re['code'] == 2008:
        #     personal_coins = {}
        # else:
        #     return re

        if re['code'] != 1000:
            return re
        personal_coins = re['data']

        # get coins market rank
        ticker_data = self.get_ticker()

        for coin in data:
            element = {}
            coin_full_name = coin[0]
            coin_short_name = full_short[coin_full_name]
            low_short_name = coin_short_name.lower()
            element['a'] = 'https://www.banbaofruit.com/images/' \
                           + low_short_name + '.png'
            element['b'] = coin_short_name
            element['c'] = coin[1]

            # get coins rank
            import coinName2Id
            name_id = coinName2Id.data
            low_coin_full_name = coin_full_name.lower()
            if low_coin_full_name in name_id:
                id = str(name_id[low_coin_full_name])
                if id in ticker_data:
                    coin_rank = ticker_data[id]['rank']
                    element['current_price'] = ticker_data[id]['quotes']['CNY']['price']
                else:
                    coin_rank = 99999
                    element['current_price'] = 0
            else:
                coin_rank = 99999
                element['current_price'] = 0
            element['d'] = coin_rank
            # -------

            element['full_name'] = coin_full_name
            if coin_full_name in personal_coins:
                element['is_selected'] = 1
            else:
                element['is_selected'] = -1
            coins_list.append(element)

        # order by market rank
        if 'order_by' in params and params['order_by'] == 'market_rank':
            coins_list.sort(key=lambda x: x['d'])
        #

        # transfer 99999 to '-' in market rank
        # for i in coins_list:
        #     if i['d'] == 99999:
        #         i['d'] = '-'

        return {"code": 1000, "success": True, "message": "获取成功", "data": coins_list}

    def coinmarketcap(self, sub_url, params):
        url = "https://api.coinmarketcap.com/v1/" + sub_url
        try:
            result = requests.get(url=url, data=params).json()
            if 'error' not in result:

                # 大整数之间用逗号分隔
                if sub_url[:6] == 'ticker':
                    if result[0]['market_cap_usd'] is not None:
                        result[0]['market_cap_usd'] = self.num_to_dotNUm(result[0]['market_cap_usd'])
                    if result[0]['available_supply'] is not None:
                        result[0]['available_supply'] = self.num_to_dotNUm(result[0]['available_supply'])
                    if result[0]['total_supply'] is not None:
                        result[0]['total_supply'] = self.num_to_dotNUm(result[0]['total_supply'])
                    if result[0]['max_supply'] is not None:
                        result[0]['max_supply'] = self.num_to_dotNUm(result[0]['max_supply'])

                return {"code": 1000, "success": True, "message": "获取成功", "data": result}
            else:
                return {"code": 2025, "success": False, "message": result['error'], "data": None}
        except BaseException as e:
            print(e)
            return {"code": 2025, "success": False, "message": "获取失败", "data": None}

    def num_to_dotNUm(self, num_str):
        num = float(num_str)
        num = int(num)
        if num != 0:
            a = num % 1000
            num = int(num / 1000)
            dotNum = str(a)
            dotNum = dotNum.zfill(3)
        else:
            return num_str

        while num != 0:
            a = num % 1000
            num = int(num / 1000)
            if num > 0:
                dotNum = str(a).zfill(3) + ',' + dotNum
            else:
                dotNum = str(a) + ',' + dotNum
        return dotNum

    def get_ticker(self):
        data = {}
        try:
            filename = './temp.json'
            file = open(filename, "r")
            data = json.load(file)
            file.close()
            return data
        except BaseException as e:
            return {}

'''
    def get_ticker(self):
        url = "https://api.coinmarketcap.com/v2/ticker/?convert=cny&limit=100&"
        start = 1
        data = {}
        try:
            for start in range(1, 201, 100):
                re_url = url + 'start=' + str(start)
                rank_data = requests.get(re_url).json()['data']
                data.update(rank_data)
            return data
        except BaseException as e:
            return {}
'''