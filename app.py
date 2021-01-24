from flask import Flask, render_template, request, redirect
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
import multiprocessing



load_dotenv()
app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
tl = Timeloop()

# class UploadForm(FlaskForm):
#     xlsxfile = FileField('', validators=[FileRequired()])

def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)

def multi(page):
    print(page)
    offers = GetOffers(getenv('URL'), page)
    offers.get_offers()

def loop_searching(pages):
    print('next itteration')
    try:
        for page in range(1,int(pages)):
            p = Process(target=multi, args=(page,))
            p.start()
    except:
        pass

# ***********************************
# ***       MAIN route            ***
# ***********************************

@app.route('/')
def start():
    base = Database()
    tags = base.fetch_tags()
    count = base.count_row_offers()
    version = getenv('VERSION')
    return render_template('index.html', count = count, tags = tags, version = version)


# ***********************************
# ***   SETTINGS operations       ***
# ***********************************

@app.route('/settings', methods = ['GET', 'POST'])
def settings():
    base = Database()
    settings = base.fetch_settings()
    return render_template('index.html', settings = settings)

@app.route('/settings-init')
def setinit():
    base = Database()
    #base.create_db(getenv('SQL_DEL_SETTINGS'))
    base.create_db(getenv('SQL_SETTINGS'))
    base.settings_init(getenv('DURATION_SET_INIT'),getenv('PAGES_SET_INIT'))
    return render_template('index.html', info = "settings initioation")

@app.route('/settings-save', methods = ['GET', 'POST'])
def setsave():
    base = Database()
    if request.method == 'POST':
        data = request.form.to_dict(flat=False)
        base.save_settings(data)
        return render_template('index.html', info = "settings save")

# ***********************************
# ***   OFFERS operations         ***
# ***********************************

@app.route('/clear-offers')
def setup():
    base = Database()
    # use if initiate OFFER table
    #base.create_db(getenv('SQL_DROP_OFFER'))
    # rem if initiate OFFER table
    base.create_db(getenv('SQL_DEL_OFFER'))
    base.create_db(getenv('SQL_OFFER'))
    #base.create_db(getenv('SQL_XLSX'))
    return render_template('index.html', info = "drop old and create new tables")

@app.route('/add')
def add():
    base = Database()
    settings = base.fetch_settings()
    loop_searching(settings[1][2])
    @tl.job(interval=timedelta(seconds=float(settings[0][2])))
    def sample_job_every_xxxs():
        loop_searching(settings[1][2])
    tl.start()
    return render_template('index.html', info = "parse new data")

@app.route('/stop-add')
def stopadd():
    #loop_searching()
    tl.stop()
    #restart_program()
    return render_template('index.html', info = "add stop")

@app.route('/offers-save', methods = ['GET', 'POST'])
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

@app.route('/search', methods=['GET','POST'])
def search():
    check = []
    base = Database()
    links = base.fetch_search()
    if request.method == 'POST':
        check = request.form.getlist('options')
    return render_template('index.html', links = links, check = check)

# ***********************************
# *** transfer XLS file to base   ***
# ***********************************

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    base = Database()
    base.create_db(getenv('SQL_DEL_XLSX'))
    base.create_db(getenv('SQL_XLSX'))
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