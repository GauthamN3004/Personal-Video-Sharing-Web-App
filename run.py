from flask import Flask,render_template,flash,request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import datetime
import pytz

app = Flask(__name__)
app.secret_key = "APakdjne348s.APnfusjku2284"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(30),nullable = False, unique = True)
    password = db.Column(db.String(64),nullable = False)
    posts = db.relationship('posts',backref = 'author',lazy = True)

    def __repr__(self):
        return f"users('{self.username}','{self.id}')"

class posts(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(30),nullable = False,unique = True)
    link = db.Column(db.String(100),nullable = False)
    time_stamp = db.Column(db.DateTime,nullable = False,default = datetime.datetime.now)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable = False)

    def __repr__(self):
        return f"posts('{self.title}','{self.id}')"



@app.route('/')
def start():
    session["username"] = "no one here !!"
    session["loggedin"] = False
    session["user_id"] = -1
    return redirect(url_for("login"))


@app.route('/home/')
def home():
    if(session["loggedin"] == True):
        pts = posts.query.all()
        if(len(pts)>1):
            pts = pts[::-1]
        return render_template("home.html",my_pts = pts)
    else:
        return redirect(url_for('login'))

@app.route('/login/',methods = ['POST','GET'])
def login():
    if(session["loggedin"]== True):
        return redirect(url_for("home"))
    if(request.method == 'POST'):
        uname = request.form["username"]
        pw = request.form["password"]
        users_data = users.query.filter_by(username=uname).all()
        if(len(users_data)==1):
            users_data = users_data[0]
            if(sha256_crypt.verify(pw,users_data.password)):
                session["loggedin"] = True
                session["username"] = uname
                session["user_id"] = users_data.id
                return redirect(url_for('home'))

            else:
                flash("Wrong Username or Password !",category='error')
                return render_template("login.html")

        else:
            flash("Wrong Username or Password !",category='error')
            return render_template("login.html")
    return render_template("login.html")

@app.route('/register/',methods = ['POST','GET'])
def register():
    if request.method == "POST":
        uname = request.form['username']
        passw = request.form['pass']
        re_password = request.form['re_pass']

        users_data = users.query.filter_by(username=uname).all()
        if(len(users_data)==1):
            flash("Username already exists !")
            return render_template("register.html")
        if passw == re_password:
            user1 = users(username = uname)
            name = user1.username
            pw = sha256_crypt.encrypt(passw)
            user1 = users(username = name,password = pw)
            db.session.add(user1)
            db.session.commit()

            flash("You have successfully registered !","success")
            return redirect(url_for('login'))
        else:
            flash("The passwords do not match !","error")
            return render_template("register.html")

    return render_template("register.html")

@app.route("/new_post/",methods = ["POST","GET"])
def new_post():
    if(session["loggedin"] == True):
        if request.method == "POST":
            title1 = request.form["title"]
            content1 = request.form["content"]
            link1 = request.form["link"]

            post_data = posts.query.filter_by(title = title1).all()
            if(len(post_data) ==1):
                flash("Title already Exists !",category='error')
                return render_template("new_post.html")

            link1 = "https://www.youtube.com/embed/"+link1[link1.find("watch?v=")+8:link1.find("watch?v=")+19]
            post1 = posts(title = title1,link = link1,content = content1,user_id = session["user_id"],time_stamp = datetime.datetime.now(pytz.timezone("Asia/Kolkata")))
            db.session.add(post1)
            db.session.commit()
            flash("Post added Successfully !!!",category='success')
            return render_template("new_post.html")
        else:
            return render_template("new_post.html")
    else:
        return redirect(url_for('login'))

@app.route("/my_posts/",methods = ["POST","GET"])
def my_posts():
    if(session["loggedin"] == True):
        pts = posts.query.filter_by(user_id = session["user_id"]).all()
        if(len(pts)>1):
            pts = pts[::-1]
        if(request.method=='POST'):
            try:
                if(request.form["delete"]):
                    del_id = request.form['delete']
                    del_list = posts.query.filter_by(id = del_id)
                    for del_post in del_list:
                        db.session.delete(del_post)
                    db.session.commit()

                    flash("The post has been deleted successfully !",'success')
                    return redirect(url_for("my_posts"))
            
            except:
                k=0

        return render_template("my_posts.html",my_pts = pts)
    else:
        return redirect(url_for('login'))

@app.route("/search/",methods=["POST","GET"])
def search():
    if(request.method == 'POST'):
        search_text = request.form["search"]
        pts = posts.query.all()
        new_pts = []
        for p in pts:
            if(p.title.lower().find(search_text.lower())>=0 or p.content.lower().find(search_text.lower())>=0):
                new_pts.append(p)
        if(len(new_pts)>1):
            new_pts = new_pts[::-1]
        return render_template("search.html",val = search_text,my_pts = new_pts,length = len(new_pts)) 
    else:
        return render_template("search.html",val = "") 

@app.route("/logout")
def logout():
    session.pop("loggedin",False)
    session.pop("username","")
    flash("You have successfully Logged Out!",category="success")
    return redirect(url_for('start'))

if __name__ == "__main__":
    app.run(debug=True)