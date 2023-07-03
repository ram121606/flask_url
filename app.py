
from flask import Flask,request,jsonify,redirect
from flask_cors import CORS
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
cors = CORS(app)

app.config['MYSQL_HOST'] = os.environ.get('DB_HOST')
app.config['MYSQL_USER'] = os.environ.get('DB_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASS')
app.config['MYSQL_DB'] = os.environ.get('DB_DATABASE')

mysql = MySQL(app)

@app.route('/')
def home():
    return "Success"

@app.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    result = "False"
    cur = mysql.connection.cursor()
    cur.execute("select username from users where username = '" + username + "'")
    userres = cur.fetchone()
    cur.execute("select password from users where password = '" + password + "'")
    passwordres = cur.fetchone()
    if(userres is not None or passwordres is not None):
        result = "True"
    else:    
        cur.execute("insert into users(username, password) values(%s, %s)",(username,password))
        mysql.connection.commit()
    cur.close()
    return jsonify({'result':result})

@app.route("/login",methods=["POST"])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    result = "False"
    cur = mysql.connection.cursor()
    cur.execute("select username from users where username = '" + username + "' and password = '" + password + "' ")
    res = cur.fetchone()
    if(res is not None):
        result = "True"
    cur.close()
    return jsonify({'result':result})

@app.route("/url",methods=['POST'])
def url():
    data = request.get_json()
    username = data['username']
    url = data['url']
    nickname = data['nickname']
    cur = mysql.connection.cursor()
    cur.execute("select username,org_url from url where username = '" + username + "' and org_url = '" + url + "' ")
    res = cur.fetchone()
    print(res)
    exists = "False"
    if(res is not None):
        cur.execute("select short_url from url where username = '" + username + "' and org_url = '" + url + "' ")
        result = cur.fetchone()[0]
    else:
        cur.execute("select nickname from url where username = '" + username +"' and nickname ='" + nickname + "' ")
        nickres = cur.fetchone()
        print(nickres)
        if(nickres is not None):
            exists = "True"
            result = ""
        else:
            result = username + "/" + nickname
            cur.execute("insert into url(username, org_url, nickname, short_url) values(%s, %s, %s, %s)",(username, url, nickname, result))
            mysql.connection.commit()
    cur.close()
    return jsonify({'host':os.environ.get('FLASK_HOST')+result , 'exists':exists})

@app.route("/<username>/<nickname>",methods=['GET'])
def route(username,nickname):
    cur = mysql.connection.cursor()
    cur.execute("select org_url from url where username = '" + username + "' and nickname = '" + nickname +"' ")
    res = cur.fetchone()
    print(res)
    return redirect(res[0])


if __name__ == "__main__":
    app.run(debug=True)