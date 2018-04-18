# -*- coding: utf-8 -*-
# !flask/bin/python
from flask import Flask, jsonify
from flask import request
import sql

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 让支持jsonify中文


@app.route('/get_coins', methods=['GET'])
def get_coins():
    mysql = sql.sql()
    result = mysql.get_coins(request.args)
    mysql.db_close()
    return jsonify(result)


@app.route('/get_commits_num')
def get_commits_num():
    mysql = sql.sql()
    result = mysql.get_commits_num(request.args)
    mysql.db_close()
    return jsonify(result)


@app.route('/get_last')
def get_last():
    mysql = sql.sql()
    result = mysql.get_last(request.args)
    mysql.db_close()
    return jsonify(result)


@app.route('/get_rank')
def get_rank():
    mysql = sql.sql()
    result = mysql.get_rank(request.args)
    mysql.db_close()
    return jsonify(result)


@app.route('/get_frequency')
def get_frequency():
    mysql = sql.sql()
    result = mysql.get_frequency(request.args)
    mysql.db_close()
    return jsonify(result)


@app.route('/login')
def login():
    mysql = sql.sql()
    result = mysql.login(request.args)
    mysql.db_close()
    return jsonify(result)


@app.route('/get_personal_coins')
def get_personal_coins():
    mysql = sql.sql()
    result = mysql.get_personal_coins(request.args)
    mysql.db_close()
    return jsonify(result)


@app.route('/insert_personal_coin')
def insert_personal_coin():
    mysql = sql.sql()
    result = mysql.insert_personal_coin(request.args)
    mysql.db_close()
    return jsonify(result)


@app.route('/delete_personal_coin')
def delete_personal_coin():
    mysql = sql.sql()
    result = mysql.delete_personal_coin(request.args)
    mysql.db_close()
    return jsonify(result)


@app.route('/get_coins_list')
def get_coins_list():
    mysql = sql.sql()
    result = mysql.get_coins_list(request.args)
    mysql.db_close()
    return jsonify(result)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', debug=True, ssl_context=(
        'ssl/1_www.banbaofruit.com_bundle.crt',
        'ssl/2_www.banbaofruit.com.key'
    ))
