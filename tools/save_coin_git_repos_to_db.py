import config
import pymysql

info = config.info

connection = pymysql.connect('',
                            '',
                            '',
                            '',
                            charset="utf8")

for coin in info:
    name = coin['coin_full_name']
    repo = coin['repo_name']

    sql = "insert into coin_git_repos(coin, git_repo) values ('%s', '%s')" % (
        name, repo)

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.close()
        connection.commit()
        print(name, "success")
    except:
        print(name, '--------------------------error')

connection.close()