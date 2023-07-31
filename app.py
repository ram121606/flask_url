
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
    cur.execute("select username from users where username = %s",(username,))
    userres = cur.fetchone()
    cur.execute("select password from users where password = %s",(password,))
    passwordres = cur.fetchone()
    if(userres is not None or passwordres is not None):
        result = "True"
    else:    
        cur.execute("insert into users(username, password) values(%s, %s)",(username,password))
        mysql.connection.commit()
    cur.close()
    return {'result':result}

@app.route("/login",methods=["POST"])
def login():
    print(type(request))
    data = request.get_json()
    username = data['username']
    password = data['password']
    result = "False"
    cur = mysql.connection.cursor()
    cur.execute("select username from users where username = %s and password = %s",(username,password))
    res = cur.fetchone()
    if(res is not None):
        result = "True"
    cur.close()
    return {'result':result}

@app.route("/url",methods=['POST'])
def url():
    data = request.get_json()
    username = data['username']
    url = data['url']
    nickname = data['nickname']
    cur = mysql.connection.cursor()
    cur.execute("select username,org_url from url where username = %s and org_url = %s",(username,url))
    res = cur.fetchone()
    print(res)
    exists = "False"
    if(res is not None):
        cur.execute("select short_url from url where username = %s and org_url = %s",(username,url))
        result = cur.fetchone()[0]
    else:
        cur.execute("select nickname from url where username = %s and nickname = %s ",(username,nickname))
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
    return {'host':os.environ.get('FLASK_HOST')+result , 'exists':exists}

@app.route("/<username>/<nickname>",methods=['GET'])
def route(username,nickname):
    cur = mysql.connection.cursor()
    cur.execute("select org_url from url where username = %s and nickname = %s",(username,nickname,))
    res = cur.fetchone()
    print(res)
    cur.close()
    return redirect(res[0])

@app.route("/details/<username>")
def deatisl(username):
    cur = mysql.connection.cursor()
    print(username)
    cur.execute("select short_url,org_url from url where username = %s",(username,))
    res = cur.fetchall()
    return {'result':res}


if __name__ == "__main__":
    app.run(debug=True)