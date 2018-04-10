from github import Github
import config
import requests
import pymysql
import time
import datetime


class GetInfo(object):
    def __init__(self):
        self.g = Github(config.key)
        self.coins_info = config.info
        self.db = pymysql.connect(config.mql_url,
                                  config.mql_user,
                                  config.mql_pswd,
                                  config.mql_db,
                                  charset="utf8")

    def get_commits_info(self):
        for coin in self.coins_info:

            info = self.g.get_repo(coin["repo_name"])
            commits = info.get_commits()[:100]
            for commit in commits:
                cmt_time_info = self.get_commit_time_info(commit)
                result = self.insert_into_db(coin, commit, cmt_time_info)
                if not result:
                    break

    def get_commit_time_info(self, commit):
        url = commit.url
        url = url.replace("/commits/", "/git/commits/")
        data = {"client_id": config.client_id,
                "client_secret": config.client_secret}
        commit_time_info = requests.get(url, params=data).json()
        return commit_time_info

    def insert_into_db(self, coin_info, commit, cmt_time_info):
        coin = coin_info['coin_full_name']
        repo_name = coin_info['repo_name']
        additions = commit.stats.additions
        deletions = commit.stats.deletions
        total = commit.stats.total
        collect_time = str(time.strftime('%Y-%m-%d %H:%M:%S',
                                 time.localtime(time.time())))
        author = cmt_time_info['author']['name']
        committer = cmt_time_info['committer']['name']

        create_time = cmt_time_info['author']['date']
        create_time = create_time.replace('T', ' ')
        create_time = create_time.replace('Z', '')
        create_time = datetime.datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
        create_time = create_time + datetime.timedelta(hours=8)
        create_time = datetime.datetime.strftime(create_time, '%Y-%m-%d %H:%M:%S')

        commit_time = cmt_time_info['committer']['date']
        commit_time = commit_time.replace('T', ' ')
        commit_time = commit_time.replace('Z', '')
        commit_time = datetime.datetime.strptime(commit_time, '%Y-%m-%d %H:%M:%S')
        commit_time = commit_time + datetime.timedelta(hours=8)
        commit_time = datetime.datetime.strftime(commit_time, '%Y-%m-%d %H:%M:%S')

        html_url = cmt_time_info['html_url']
        sha = commit.sha

        ############
        print(coin, commit_time)

        sql_is_existed = "select * from repo_commits \
            where commit_sha = '%s'" % (sha)

        sql_insert = "insert into repo_commits( \
            coin, repo_name, additions, deletions, total, \
            collect_time, author, committer, create_time, \
            commit_time, html_url, commit_sha) values ( \
            '%s', '%s', %d, %d, %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            coin, repo_name, int(additions), int(deletions),
            int(total), collect_time, author, committer,
            create_time, str(commit_time), html_url, sha)

        try:
            cursor = self.db.cursor()
            cursor.execute(sql_is_existed)
            if cursor.rowcount != 0:
                cursor.close()
                return False
            print("insert successfully")
            cursor.execute(sql_insert)
            cursor.close()
            self.db.commit()
            return True

        except BaseException as e:
            print(e)
            self.db.rollback()
            return True

while True:
    try:
        GetInfo().get_commits_info()
    except BaseException as e:
        print(e)
    finally:
        for i in range(3660):
            print("ramain %dm %ds" %(i/60, i%60))
            time.sleep(1)

