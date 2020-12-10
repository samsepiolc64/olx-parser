from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

# from flask_wtf import FlaskForm
# from flask_wtf.file import FileField, FileRequired

from database import Database
from getoffers import GetOffers
from xlsx2db import Xlsx2Db
from os import getenv
from dotenv import load_dotenv
from multiprocessing import Process
from timeloop import Timeloop
from datetime import timedelta
import pandas as pd

load_dotenv()
app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
tl = Timeloop()

# class UploadForm(FlaskForm):
#     xlsxfile = FileField('', validators=[FileRequired()])

def multi(page):
    print(page)
    offers = GetOffers(getenv('URL'), page)
    offers.get_offers()

def loop_searching(run):
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
    base = Database()
    tags = base.fetch_tags()
    #print(tags)
    return render_template('index.html', page = "100", tags = tags)

@app.route('/setup')
def setup():
    base = Database()
    #base.create_db(getenv('SQL_DROP_OFFER'))
    #base.create_db(getenv('SQL_DROP_XLSX'))
    base.create_db(getenv('SQL_OFFER'))
    base.create_db(getenv('SQL_XLSX'))
    return render_template('index.html', info = "drop old and create new tables")

@app.route('/add')
def add():
    loop_searching(run=True)
    @tl.job(interval=timedelta(seconds=300))
    def sample_job_every_xxxs():
        loop_searching(run=True)
    tl.start()
    return render_template('index.html', info = "parse new data")

@app.route('/stopadd')
def stopadd():
    #loop_searching(run=False)
    tl.stop()
    return render_template('index.html', info = "add stop")

@app.route('/searchold')
def searchold():
    base = Database()
    links = base.fetch_searchold()
    return render_template('index.html', links = links)

@app.route('/search')
def search():
    #tl.stop()
    base = Database()
    links = base.fetch_search()
    return render_template('index.html', links = links)

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    # base = Database()
    # base.create_db(getenv('SQL_DEL_XLSX'))

    #
    # form = UploadForm()
    # if form.validate_on_submit():
    #     return 'Form Successfully Submitted!'
    # return render_template('upload.html', form = form)
    #

    return render_template('index.html', upload = True)

@app.route('/phrases', methods = ['GET', 'POST'])
def phrases():
    if request.method == 'POST':
        user_csv = request.form['xlsxfile']
        data = pd.read_excel(user_csv, index_col=None, header=None, usecols="A,C").values
        xlsx = Xlsx2Db()
        xlsx.xlsx2db(data)
        return render_template('index.html', info = "add new tags")

if __name__ == "__main__":
    app.run(debug=True)