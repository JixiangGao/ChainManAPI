# -*- coding: utf-8 -*-

import config
import pymysql
import time
import traceback


class sql(object):
    def __init__(self):
        self.db = pymysql.connect(config.mql_url,
                                  config.mql_user,
                                  config.mql_pswd,
                                  config.mql_db,
                                  charset="utf8")

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
                        coin, commit_num )
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






