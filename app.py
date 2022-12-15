from flask import Flask, render_template, request, redirect, url_for, Response, flash, session
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
# from flask_wtf import FlaskForm
# from flask_wtf.file import FileField, FileRequired
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
# from flask_wtf import wtforms
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from database import Database
from getoffers import GetOffers
from xlsx2db import Xlsx2Db
from os import getenv
from dotenv import load_dotenv
from multiprocessing import Process
from timeloop import Timeloop
from datetime import timedelta
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import multiprocessing
import os
from django.core.paginator import Paginator
import sys
# import psutil

# sys.path.append("./views")
# from views.views import *


load_dotenv()
app = Flask(__name__)
Bootstrap(app)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
tl = Timeloop()

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return null

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'loggedin' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap

# def restart_program():
#     python = sys.executable
#     os.execl(python, python, *sys.argv)

def multi(page, username):
    print(page)
    offers = GetOffers(getenv('URL'), page, username)
    offers.get_offers()

def loop_searching(pages):

        # jobs = []
        for page in range(1, int(pages)):
            p = Process(target=multi, args=(page,session['username'],))
            # jobs.append(p)
            p.daemon = True
            p.start()
        # print(jobs)
        # for j in jobs:
        #     j.join()



class RegisterForm(FlaskForm):
    username = StringField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Login")

# ***********************************
# ***       MAIN route            ***
# ***********************************

@app.route('/')
@login_required
def start():
    global procArray
    procArray = []

    # print(os.getppid())
    # print(os.getpid())

    base = Database()
    tags = base.fetch_tags()
    count = base.count_row_offers()
    version = getenv('VERSION')

    # print("children:", multiprocessing.active_children())
    # for p in multiprocessing.active_children():
    #     if p.name == "pool":
    #         print("aktywny")
    #     else:
    #         print("nieaktywny")

    return render_template('index.html', count=count, tags=tags, version=version, username=session["username"])




# ***********************************
# ***          LOGIN              ***
# ***********************************

@app.route('/login', methods=['GET', 'POST'])
def login():
    base = Database()
    form = LoginForm()
    if request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        account = base.login_user(username)
        if account:
            password_rs = account['password']
            if check_password_hash(password_rs, password):
                session["loggedin"] = True
                session["id"] = account["id"]
                session["username"] = account["username"]
                return redirect(url_for("search"))
            else:
                flash("Incorrect username/password")
        else:
            flash("Incorrect username/passord")
    return render_template('index.html', login=1, form=form)

# ***********************************
# ***           LOGOUT            ***
# ***********************************

@app.route('/logout')
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for("login"))

# ***********************************
# ***          REGISTER           ***
# ***********************************

@app.route('/register', methods=['GET', 'POST'])
def register():
    base = Database()
    form = RegisterForm()
    if form.validate_on_submit():
        # password = bcrypt.generate_password_hash(form.password.data)
        password = generate_password_hash(form.password.data)
        username = form.username.data
        base.register_user(username, password)
        return redirect(url_for('login'))
    return render_template('index.html', register=1, form=form)

# ***********************************
# ***           PROFILE           ***
# ***********************************

@app.route('/profile')
@login_required
def profile():
    base = Database()
    account = base.profile_user(session["id"])
    return render_template('index.html', profile=1, account=account)

# ***********************************
# ***   SETTINGS operations       ***
# ***********************************

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    base = Database()
    settings = base.fetch_settings()
    return render_template('index.html', settings=settings)

@app.route('/settings-init')
def setinit():
    base = Database()

     base.create_db(getenv('SQL_DROP_USERS')) #tworzenie tabeli uzytkownikow
    #base.create_db(getenv('SQL_USERS'))

     base.create_db(getenv('SQL_DROP_SETTINGS')) #tworzenie tabeli ustawien
    #base.create_db(getenv('SQL_DEL_SETTINGS')) #czyszczenie tabeli ustawien
    base.create_db(getenv('SQL_SETTINGS'))
    base.settings_init(getenv('DURATION_SET_INIT'), getenv('PAGES_SET_INIT'), getenv('LINKS_ALL_SET_INIT'),
                       getenv('LINKS_PHRASES_SET_INIT'), getenv('LINKS_ANTYPHRASES_SET_INIT'),
                       getenv('LINKS_FAVORITE_SET_INIT'), getenv('LINKS_VISITED_SET_INIT'))
    return render_template('index.html', info="settings initioation")

@app.route('/settings-save', methods=['GET', 'POST'])
def setsave():
    base = Database()
    data = request.form.to_dict(flat=False)
    base.save_settings(data)
    links = base.fetch_search(filtr=0)
    settings = base.fetch_settings()
    # return render_template('index.html', links=links, settingsLinks=settings)
    return render_template('index.html', settings=settings)
    # return redirect('/search')

# ***********************************
# ***   OFFERS operations         ***
# ***********************************

@app.route('/clear-offers')
@login_required
def setup():
    base = Database()
    # use if initiate OFFER table
    # base.create_db(getenv('SQL_DROP_OFFER'))
    # rem if initiate OFFER table
    base.create_db(getenv('SQL_DEL_OFFER'))
    base.create_db(getenv('SQL_OFFER'))
    # base.create_db(getenv('SQL_XLSX'))
    return render_template('index.html', info="drop old and create new tables")

@app.route('/add')
@login_required
def add():
    base = Database()
    settings = base.fetch_settings()
    loop_searching(settings[1][2])
    @tl.job(interval=timedelta(seconds=float(settings[0][2])))
    def sample_job_every_xxxs():
        loop_searching(settings[1][2])
    tl.start()
    return render_template('index.html', info="parse new data")

@app.route('/stop-add')
@login_required
def stopadd():
    tl.stop()

    # print(procArray[0].is_alive())
    # print(procArray[0].pid)
    # for proc in procArray:
    #     proc.join()
    #     proc.close()

    return render_template('index.html', info="add stop")

@app.route('/offers-save', methods=['GET', 'POST'])
def offersave():
    base = Database()
    if request.method == 'POST':
        data = request.form.to_dict(flat=False)
        base.save_offer(data)
        return redirect('/search')

# @app.route('/searchold')
# def searchold():
#     base = Database()
#     links = base.fetch_searchold()
#     return render_template('index.html', links = links)


# ***********************************
# ***       listing LINKS         ***
# ***********************************

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
        base = Database()
        data = request.form.to_dict(flat=False)
        base.save_settings(data)
        settings = base.fetch_settings()

        for setting in settings:
            if setting[1] == "LinksPhrases":
                Links_Phrases = setting[2]
            if setting[1] == "LinksAntyphrases":
                Links_Antyphrases = setting[2]
            if setting[1] == "LinksFavorite":
                Links_Favorite = setting[2]
            if setting[1] == "LinksVisited":
                Links_Visited = setting[2]

        if Links_Phrases == "true" and Links_Antyphrases == "true" and Links_Favorite == "false" and Links_Visited == "false":
            links = base.fetch_search(filtr=0)
        if Links_Phrases == "true" and Links_Antyphrases == "true" and Links_Favorite == "true" and Links_Visited == "false":
            links = base.fetch_search(filtr=1)
        if Links_Phrases == "true" and Links_Antyphrases == "true" and Links_Favorite == "false" and Links_Visited == "true":
            links = base.fetch_search(filtr=2)
        if Links_Phrases == "true" and Links_Antyphrases == "true" and Links_Favorite == "true" and Links_Visited == "true":
            links = base.fetch_search(filtr=3)

        if Links_Phrases == "true" and Links_Antyphrases == "false" and Links_Favorite == "false" and Links_Visited == "false":
            links = base.fetch_search(filtr=4)
        if Links_Phrases == "true" and Links_Antyphrases == "false" and Links_Favorite == "true" and Links_Visited == "false":
            links = base.fetch_search(filtr=5)
        if Links_Phrases == "true" and Links_Antyphrases == "false" and Links_Favorite == "false" and Links_Visited == "true":
            links = base.fetch_search(filtr=6)
        if Links_Phrases == "true" and Links_Antyphrases == "false" and Links_Favorite == "true" and Links_Visited == "true":
            links = base.fetch_search(filtr=7)

        if Links_Phrases == "false" and Links_Antyphrases == "true" and Links_Favorite == "false" and Links_Visited == "false":
            links = base.fetch_search(filtr=8)
        if Links_Phrases == "false" and Links_Antyphrases == "true" and Links_Favorite == "true" and Links_Visited == "false":
            links = base.fetch_search(filtr=9)
        if Links_Phrases == "false" and Links_Antyphrases == "true" and Links_Favorite == "false" and Links_Visited == "true":
            links = base.fetch_search(filtr=10)
        if Links_Phrases == "false" and Links_Antyphrases == "true" and Links_Favorite == "true" and Links_Visited == "true":
            links = base.fetch_search(filtr=11)

        if ((
                Links_Phrases == "false" and Links_Antyphrases == "false" and Links_Favorite == "false" and Links_Visited == "false") or (
                Links_Phrases == "false" and Links_Antyphrases == "false" and Links_Favorite == "true" and Links_Visited == "true") or (
                Links_Phrases == "false" and Links_Antyphrases == "false" and Links_Favorite == "true" and Links_Visited == "false") or (
                Links_Phrases == "false" and Links_Antyphrases == "false" and Links_Favorite == "false" and Links_Visited == "true")):
            links = 1

        list_paginator = Paginator(links, 30)
        page_num = request.args.get('page')
        page = list_paginator.get_page(page_num)


        context = {
            'count': list_paginator.count,
            'count_pages': list_paginator.num_pages,
            'list_paginator' : list_paginator,
            'page' : page
        }

        return render_template('index.html', context = context,  links=links, settingsLinks=settings, username=session['username'])


# ***********************************
# *** transfer XLS file to base   ***
# ***********************************


@app.route('/excel', methods=['GET', 'POST'])
@login_required
def excel():
    base = Database()
    output = base.base_to_xlsx()
    # return render_template('index.html', info=xxx)
    # return Response(xxx, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=csv-test.csv"})
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=excel-test.xls"})


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    # base = Database()
    # base.create_db(getenv('SQL_DEL_XLSX'))
    # base.create_db(getenv('SQL_XLSX'))

    #
    # form = UploadForm()
    # if form.validate_on_submit():
    #     return 'Form Successfully Submitted!'
    # return render_template('upload.html', form = form)
    #
    return render_template('index.html', upload=True)


@app.route('/phrases', methods=['GET', 'POST'])
def phrases():
    base = Database()
    base.create_db(getenv('SQL_DEL_XLSX'))
    if request.method == 'POST':
        user_csv = request.form['xlsxfile']
        data = pd.read_excel(user_csv, index_col=None, header=None, usecols="A,C").values
        xlsx = Xlsx2Db()
        xlsx.xlsx2db(data)
        return render_template('index.html', info="add new tags")


if __name__ == "__main__":
    app.run(debug=True)