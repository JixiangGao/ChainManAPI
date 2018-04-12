#!flask/bin/python
from flask import Flask, jsonify
from flask import request
import sql

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 让支持jsonify中文

mysql = sql.sql()


@app.route('/get_coins', methods=['GET'])
def get_coins():
    result = mysql.get_coins(request.args)
    return jsonify(result)


@app.route('/get_commits_num')
def get_commits_num():
    result = mysql.get_commits_num(request.args)
    return jsonify(result)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', debug=True)
