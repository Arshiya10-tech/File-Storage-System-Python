from flask import Flask, request, session,flash,\
render_template, redirect, send_from_directory, url_for, send_file

from flask_sqlalchemy import SQLAlchemy
from os import urandom
import os
import time
#import re
from werkzeug import secure_filename

app = Flask(__name__)


#print('\n\n\n***************************')
#print("app= ",app)
#print('\n\n\n***************************')


app.config.from_object(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = urandom(32)
#print('\n\n\n***************************')

#print('app.config[sql]=',app.config["SQLALCHEMY_DATABASE_URI"])
#instantiation of Database
db = SQLAlchemy(app)


#print('\n\n\n***************************')
#print("db=",db)
#print('\n\n\n***************************')

class users(db.Model):
   username = db.Column('username', db.String(100), primary_key = True)
   password = db.Column(db.String(100))
   #email = db.Column(db.String(100))
   #session = db.Column(db.String(100))

   def __init__(self, username, password):
       self.username=username
       self.password=password
       #self.email = email
       #self.session = session

UPLOAD_FOLDER = path = os.path.expanduser('C:\\Users\\DELL\\Desktop\\atom_project\\storage\\')
#file_loc = ""

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#print('\n\n\n***************************')
#print('\n\n\n')
#print("app.config=",app.config['UPLOAD_FOLDER'])
#print('\n\n\n***************************')

#home page or login page
@app.route("/", methods=["GET", "POST"])
def home():
    #UPLOAD_FOLDER = UPLOAD_FOLDER + "/" +
    error = None
    if request.method == "GET":
        if session.get("LOGGED_IN"):
            return redirect(url_for("dashboard"))
        log_out = False
        registered = False
        error = ""
        if session.get("LOGGED_OUT"):
            log_out = True
            session["LOGGED_OUT"] = True
        if session.get("SHOW_REG_MSG"):
            log_out = False
            registered = True
            session["SHOW_REG_MSG"] = False
        if session.get("LOGIN_ERROR"):
            error = session.get("LOGIN_ERROR")
            del session["LOGIN_ERROR"]
        return render_template('login.html', log_out=log_out, registered=registered, error=error, title="Login Page")
    else:
        users_dict = {}
        #print('\n\n\n***************************')
        #print('\n\n\n')
        for user in users.query.order_by(users.username):
            #print (user.username, user.password)
            users_dict[user.username] = user.password

        if request.form['uname'] in users_dict.keys():# need to check in db for user existence
            print ('username is proper')
            if request.form['psw'] == users_dict[request.form['uname']]:
                print ('password is proper')
                session["LOGGED_IN"] = True
                #global file_loc
                #file_loc = UPLOAD_FOLDER + str(request.form['uname']) + "/"
                session['username'] = str(request.form['uname'])
                return redirect(url_for("dashboard"))
            else:
                session["LOGIN_ERROR"] = 'Invalid Credentials'
                return redirect(url_for('home'))
        else:
            print('username does not exist!')
            session["LOGIN_ERROR"] = 'Invalid User. Please register if not Registered'
            return redirect(url_for('home'))

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if session.get("LOGGED_IN"):
######################################################
        if session.get('username') == 'admin':
            users_list = []

            for user in users.query.order_by(users.username):
                print (user.username)
                users_list.append(user.username)

            return render_template('admin.html', files=users_list)
####################################################
        if session.get('username'):
            file_path = UPLOAD_FOLDER + "\\" + session['username']
            files = os.listdir(file_path)

            #print('\n\n\n***************************')
            #print('Files inside user folder', session['username'])
            #print(files)
            #print('\n\n\n***************************')

            if request.method == 'GET':
                return render_template("dashboard.html", files=files)
            else:
                # Uploading file
                print('inside dashboard post')
                f = request.files['file']
                f.save(file_path + "\\" +secure_filename(f.filename))
                time.sleep(0)
                files = os.listdir(file_path)
                flash("Your file Uploaded succesfully",'success')
                return render_template('dashboard.html', files=files)
        else:
            session['LOGGED_IN'] = False
            return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))

#downloading file
@app.route("/file=<filename>")
def send_file_to_user(filename):
    if session.get("LOGGED_IN"):
        if session.get('username'):
            file_path = UPLOAD_FOLDER + "/" + session['username']


    return send_file(file_path + "/" + str(filename), as_attachment=True, attachment_filename=filename)

#delete files
@app.route("/dfile=<filename>")
def delete(filename):
    print("inside Delete")
    if session.get("LOGGED_IN"):
        if session.get('username'):
            file_path = UPLOAD_FOLDER + "/" + session['username']
            deleting_file=file_path+"\\"+str(filename)
            os.remove(deleting_file)
            flash("your file is deleted")
            return redirect(url_for("dashboard"))




@app.route("/register", methods=["GET", "POST"])
def registration():
    if request.method == "GET":
        return render_template("registration.html", error=False, err_msg="")
    else:
        #print (request.form['uname'])
        #print (request.form['password'])
        #print (request.form['confirm_password'])
        users_dict = {}
        #print('\n\n\n***************************')
        #print('\n\n\n')
        for user in users.query.order_by(users.username):
            #print (user.username, user.password)
            users_dict[user.username] = user.password
        if request.form['uname'] in users_dict.keys():
            return render_template("registration.html", error = True, err_msg="User name already exists!")

        else:
            user = users(request.form['uname'], request.form['password'])
            db.session.add(user)
            db.session.commit()
            #print(os.getcwd())
            #cmd = 'osr ' + UPLOAD_FOLDER + str(request.form['uname'])
            #print(cmd)
            os.mkdir(UPLOAD_FOLDER + str(request.form['uname']))
            flash("Record was successfully added",'success')
            session["SHOW_REG_MSG"] = True
            return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session["LOGGED_IN"] = False
    if "username" in session:
        del session['username']
    session["LOGGED_OUT"] = True
    return redirect(url_for("home"))



if __name__=="__main__":
    app.run("127.0.0.1", 8080, debug=True, threaded=True)
    db.create_all()
    app.run("0.0.0.0", 8080, debug=True)
