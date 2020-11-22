from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from database import Database
from getoffers import GetOffers
from xlsx2db import Xlsx2Db
from sys import argv
from os import getenv
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, View
import pandas as pd
from dotenv import load_dotenv

# from rq import Queue
# from worker import conn
#
# from utils import count_words_at_url
#
# q = Queue(connection=conn)
#
# result = q.enqueue(count_words_at_url, 'http://heroku.com')


load_dotenv()
app = Flask(__name__)
Bootstrap(app)
nav = Nav(app)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')

class UploadForm(FlaskForm):
    xlsxfile = FileField('', validators=[FileRequired()])

@nav.navigation('mysite_navbar')
def create_navbar():
    start_view = View('Start', 'start')
    search_view = View('Show links', 'search')
    upload_view = View('Upload Excel', 'upload')
    add_data_view = View('Add pages', 'add')
    setup_view = View('Clear and create database', 'setup')
    admin_view = Subgroup('Create data',
                upload_view,
                add_data_view,
                setup_view
             )
    return Navbar('OLX Parser', start_view, admin_view, search_view)

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
    return render_template('index.html', info = "create tables")

@app.route('/add')
def add():
    offers = GetOffers(getenv('URL'))
    offers.get_offers()
    return render_template('index.html', info = "add data")

@app.route('/list/<search>')
def index(search):
    base = Database()
    links = base.fetch_link(title = search)
    return render_template('index.html', zm = list(links))

@app.route('/search')
def search():
    base = Database()
    links = base.fetch_search()
    return render_template('index.html', links = links)

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        return 'Form Successfully Submitted!'
    return render_template('upload.html', form = form)

@app.route('/phrases', methods = ['GET', 'POST'])
def phrases():
    if request.method == 'POST':
        user_csv = request.form['xlsxfile']
        data = pd.read_excel(user_csv, index_col=None, header=None).values
        xlsx = Xlsx2Db()
        xlsx.xlsx2db(data)
        return render_template('index.html', data = data, show = True)

def main():
    if len(argv) > 1 and argv[1] == 'setup':
        setup()
    if len(argv) > 1 and argv[1] == 'list':
        index(search = argv[2])
    if len(argv) > 1 and argv[1] == 'add':
        add()

if __name__ == "__main__":
    app.run(debug=True)