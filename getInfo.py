from github import Github
import config
import requests
import pymysql
import time
import datetime
import traceback


class GetInfo(object):
    def __init__(self):
        self.g = Github(config.key)
        self.coins_info = config.info
        self.db = pymysql.connect(config.mql_url,
                                  config.mql_user,
                                  config.mql_pswd,
                                  config.mql_db,
                                  charset="utf8")
        print("start up!")

    def get_commits_info(self):
        for coin in self.coins_info:

            #####
            time_now = time.strftime('%Y-%m-%d %H:%M:%S',
                                     time.localtime(time.time()))
            print(time_now, coin["coin_full_name"])

            info = self.g.get_repo(coin["repo_name"])
            commits = info.get_commits()
            # count = 0
            for commit in commits:
                # count = count + 1
                commit_time = commit.commit.committer.date
                time_2018_1_1 = datetime.datetime.strptime(
                    '2017-11-01 00:00:00', '%Y-%m-%d %H:%M:%S')
                if commit_time < time_2018_1_1:
                    break
                result = self.is_existed(commit)
                if not result:
                    continue

                self.insert_into_db(coin, commit)

    def is_existed(self, commit):
        sha = commit.sha
        sql_is_existed = "select * from repo_commits \
                    where commit_sha = '%s'" % (sha)
        try:
            cursor = self.db.cursor()
            cursor.execute(sql_is_existed)
            if cursor.rowcount != 0:
                cursor.close()
                return False
            cursor.close()
            return True

        except BaseException as e:
            print(e)
            # traceback.print_exc()
            return True

    def insert_into_db(self, coin_info, commit):
        coin = coin_info['coin_full_name']
        repo_name = coin_info['repo_name']
        additions = commit.stats.additions
        deletions = commit.stats.deletions
        total = commit.stats.total
        collect_time = str(time.strftime('%Y-%m-%d %H:%M:%S',
                                         time.localtime(time.time())))
        author = commit.commit.author.name
        committer = commit.commit.committer.name

        create_time = commit.commit.author.date
        create_time = create_time + datetime.timedelta(hours=8)
        create_time = datetime.datetime.strftime(create_time, '%Y-%m-%d %H:%M:%S')

        commit_time = commit.commit.committer.date
        commit_time = commit_time + datetime.timedelta(hours=8)
        commit_time = datetime.datetime.strftime(commit_time, '%Y-%m-%d %H:%M:%S')

        html_url = commit.html_url
        sha = commit.sha

        ############
        # print(coin, commit_time)

        sql_insert = "insert into repo_commits( \
            coin, repo_name, additions, deletions, total, \
            collect_time, author, committer, create_time, \
            commit_time, html_url, commit_sha) values ( \
            '%s', '%s', %d, %d, %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            coin, repo_name, int(additions), int(deletions),
            int(total), collect_time, author, committer,
            create_time, str(commit_time), html_url, sha)

        sql_insert_except = "insert into repo_commits( \
            coin, repo_name, additions, deletions, total, \
            collect_time, create_time, \
            commit_time, , commit_sha) values ( \
            '%s', '%s', %d, %d, %d, '%s', '%s', '%s', '%s')" % (
            coin, repo_name, int(additions), int(deletions),
            int(total), collect_time,
            create_time, str(commit_time), sha)

        try:
            cursor = self.db.cursor()
            cursor.execute(sql_insert)
            cursor.close()
            self.db.commit()
            ######
            time_now = time.strftime('%Y-%m-%d %H:%M:%S',
                                     time.localtime(time.time()))
            print(time_now, coin, commit_time, "insert successfully")

        except BaseException as e:
            print(e)
            # try:
            #     cursor = self.db.cursor()
            #     cursor.execute(sql_insert_except)
            #     cursor.close()
            #     self.db.commit()
            #     ######
            #     time_now = time.strftime('%Y-%m-%d %H:%M:%S',
            #                              time.localtime(time.time()))
            #     print(time_now, coin, commit_time, "something wrong but insert successfully")
            # except BaseException as ee:
            #     print(ee)
            #     self.db.rollback()
            # traceback.print_exc()
            self.db.rollback()


while True:
    try:
        GetInfo().get_commits_info()
    except BaseException as e:
        print(e)
        traceback.print_exc()
    finally:
        # time.sleep(5)
        for i in range(30):
            ######
            time_now = time.strftime('%Y-%m-%d %H:%M:%S',
                                     time.localtime(time.time()))
            print(time_now, "ramain %dm" % (30 - i))
            time.sleep(60)

