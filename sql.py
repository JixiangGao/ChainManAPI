# -*- coding: utf-8 -*-

import config
import pymysql
import time
import traceback
import datetime
import requests


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
            return all_results
        except BaseException as e:
            print(e)
            return {'code': '1010', 'msg': 'get coins error'}

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
            return results
        except BaseException as e:
            print(e)
            return {'code': '1020', 'msg': 'get commits num error'}

    def get_last(self, params):
        sql_get_last = ""  # 完整的sql语句
        sql_where_condition = ""  # sql语句中where子句
        sql_dateformat = ""  # select语句中date部分
        result_dict = {}
        loop_times = 20  # week的looptime
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
                sql_where_condition = "YEARWEEK(date_format(commit_time,'%%Y-%%m-%%d')) = YEARWEEK(now())- %d" % i
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
                # traceback.print_exc()
                return {'code': '1030', 'msg': 'get last error'}

        return result_dict

    def get_rank(self, params):
        # wait to adj
        rank1_rate = 0.05
        rank2_rate = 0.1
        rank3_rate = 0.4
        rank4_rate = 0.35
        rank5_rate = 0.1

        sql_get_rank = \
            "select coin, count(*), sum(additions), sum(deletions), sum(total) \
            from repo_commits \
            where YEARWEEK(date_format(commit_time,'%Y-%m-%d')) = YEARWEEK(now())- 1 \
            group by coin "

        if 'period' in params:
            if params['period'] == 'month':
                sql_get_rank = \
                    "select coin, count(*), sum(additions), sum(deletions), sum(total) \
                    from repo_commits \
                    where date_format(commit_time, '%%Y %%m') = date_format(DATE_SUB(curdate(), INTERVAL 1 MONTH),'%%Y %%m') \
                    group by coin "

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
            return {'code': '1040', 'msg': 'get rank error'}

        return_dict = {}
        coin_total_dict = {}
        coins_list = coins_dict.keys()
        coins_num = len(coins_list)

        rank1_num = rank1_rate * coins_num
        rank12_num = (rank1_rate + rank2_rate) * coins_num
        rank123_num = (rank1_rate + rank2_rate + rank3_rate) * coins_num
        rank1234_num = (1 - rank5_rate) * coins_num

        for coinName in coins_list:
            return_dict[coinName] = 1
            coin_total_dict[coinName] = coins_dict[coinName]['commits_num']  # 这里也可以改成是commit数，或total数

        coin_total_list = list(coin_total_dict.items())
        coin_total_list.sort(key=lambda x: x[1])
        for i in range(int(rank1234_num)):
            return_dict[coin_total_list[i][0]] += 1
        for i in range(int(rank123_num)):
            return_dict[coin_total_list[i][0]] += 1
        for i in range(int(rank12_num)):
            return_dict[coin_total_list[i][0]] += 1
        for i in range(int(rank1_num)):
            return_dict[coin_total_list[i][0]] += 1

        return return_dict

    def get_frequency(self, params):
        coin = params['coin']

        index_results = []
        value_results = []

        now = datetime.datetime.now()

        # days
        my_params = {'coin': coin, 'period': 'day'}
        day_return = self.get_last(my_params)
        index_result_day = []
        value_result_day = [0, 0, 0, 0, 0, 0, 0]
        for i in range(1, 8):
            day = now + datetime.timedelta(days=-i)
            day = datetime.datetime.strftime(day, "%Y-%m-%d")
            index_result_day.append(day)
        j = 0
        # print (list(day_return.values()))
        if len(list(day_return.values())) == 0:
            minn = 0
        else:
            minn = min(len(list(day_return.values())[0]), 7)
        for i in range(minn):
            key = list(day_return.keys())[0]
            if day_return[key][j]['day'] == index_result_day[i]:
                value_result_day[i] = day_return[key][j]['total']
                j += 1
        index_results.append(index_result_day)
        value_results.append(value_result_day)

        # weeks
        my_params = {'coin': coin, 'period': 'week'}
        day_return = self.get_last(my_params)
        index_result_day = []
        value_result_day = [0, 0, 0, 0]
        '''
            something wrong here
        '''
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
        index_results.append(index_result_day)
        value_results.append(value_result_day)

        # months
        my_params = {'coin': coin, 'period': 'month'}
        day_return = self.get_last(my_params)
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
        index_results.append(index_result_day)
        value_results.append(value_result_day)

        result = [index_results, value_results]
        return result

    def login(self, params):
        if 'code' not in params:
            return {}

        code = params['code']
        url = "https://api.weixin.qq.com/sns/jscode2session?appid=" + \
              config.appid + "&secret=" + config.secret + \
              "&js_code=" + code + "&grant_type=authorization_code"
        # print(url)
        # print(code)
        # result = {}
        result = requests.get(url=url).json()
        # print(result)
        if 'openid' in result:
            openid = result['openid']
            return {'openid': openid}
        else:
            return result
