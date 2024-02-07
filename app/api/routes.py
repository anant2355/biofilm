from flask import Blueprint, render_template, request

views = Blueprint('views',__name__)
@views.route('/')
def home():
    return render_template("base.html")

@views.route('/search')
def search():
    return render_template('search.html') 

auth = Blueprint('auth',__name__)
@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return "<p>logout</p>"




@auth.route('/uploadImage')
def uploadImage():
    return render_template("uploadImage.html")

