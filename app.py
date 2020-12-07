from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, View
from database import Database
from getoffers import GetOffers
from xlsx2db import Xlsx2Db
from os import getenv
from dotenv import load_dotenv
from multiprocessing import Process

from timeloop import Timeloop
from datetime import timedelta

import time
import pandas as pd


load_dotenv()
app = Flask(__name__)
Bootstrap(app)
nav = Nav(app)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
tl = Timeloop()


class UploadForm(FlaskForm):
    xlsxfile = FileField('', validators=[FileRequired()])

@nav.navigation('mysite_navbar')
def create_navbar():
    start_view = View('Start', 'start')
    # searchold_view = View('Show links old', 'searchold')
    search_view = View('Show links new', 'search')
    upload_view = View('Upload Excel', 'upload')
    add_data_view = View('Add pages', 'add')
    stop_add_data_view = View('Stop add pages', 'stopadd')
    setup_view = View('Clear and create database', 'setup')
    admin_view = Subgroup('Create data',
                upload_view,
                add_data_view,
                stop_add_data_view,
                setup_view
             )
    return Navbar('OLX Parser', start_view, admin_view, add_data_view, stop_add_data_view, search_view)

def multi(page):
    print(page)
    offers = GetOffers(getenv('URL'), page)
    offers.get_offers()

def loop_searching():
    print('kolejna petla')
    processes = []
    try:
        for page in range(1,10):
            p = Process(target=multi, args=(page,))
            processes.append(p)
            p.start()
    except:
        pass

@app.route('/')
def start():
    return render_template('index.html', page = "100")

@app.route('/setup')
def setup():
    base = Database()
    base.create_db(getenv('SQL_DROP_OFFER'))
    base.create_db(getenv('SQL_DROP_XLSX'))
    base.create_db(getenv('SQL_OFFER'))
    base.create_db(getenv('SQL_XLSX'))
    return render_template('index.html', info = "drop old and create new tables")

@app.route('/add')
def add():
    loop_searching()
    @tl.job(interval=timedelta(seconds=360))
    def sample_job_every_xxxs():
        loop_searching()
    tl.start()
    return render_template('index.html', info = "parse new data")

@app.route('/stopadd')
def stopadd():
    tl.stop()
    return render_template('index.html', info="add stop")

@app.route('/searchold')
def searchold():
    base = Database()
    links = base.fetch_searchold()
    return render_template('index.html', links = links)

@app.route('/search')
def search():
    base = Database()
    links = base.fetch_search()
    return render_template('index.html', links = links)

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    # base = Database()
    # base.create_db(getenv('SQL_DROP_XLSX'))
    # base.create_db(getenv('SQL_XLSX'))
    form = UploadForm()
    if form.validate_on_submit():
        return 'Form Successfully Submitted!'
    return render_template('upload.html', form = form)

@app.route('/phrases', methods = ['GET', 'POST'])
def phrases():
    if request.method == 'POST':
        user_csv = request.form['xlsxfile']
        data = pd.read_excel(user_csv, index_col=None, header=None, usecols="A,C").values
        xlsx = Xlsx2Db()
        xlsx.xlsx2db(data)
        return render_template('index.html', info = "add new tags", data = data, show = True)

if __name__ == "__main__":
    app.run(debug=True)