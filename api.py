#!flask/bin/python
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


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', debug=True)
