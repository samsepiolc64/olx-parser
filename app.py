from flask import Flask, render_template, request, redirect, url_for
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
import os



load_dotenv()
app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
tl = Timeloop()

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)


def multi(page):
    # print("parent:", os.getppid())
    # print("child:", os.getpid())
    print(page)
    offers = GetOffers(getenv('URL'), page)
    offers.get_offers()


def loop_searching(pages):
    print('next itteration')
    try:
        for page in range(1, int(pages)):
            p = Process(target=multi, args=(page,), name="pool")
            # p.setDaemon(True)
            p.start()
            procArray.append(p)
            #p.join()
    except:
        pass


# ***********************************
# ***       MAIN route            ***
# ***********************************

@app.route('/')
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


    return render_template('index.html', count=count, tags=tags, version=version)


# ***********************************
# ***   SETTINGS operations       ***
# ***********************************

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    base = Database()
    settings = base.fetch_settings()
    return render_template('index.html', settings=settings)


@app.route('/settings-init')
def setinit():
    base = Database()
    # base.create_db(getenv('SQL_DROP_SETTINGS')) #tworzenie tabeli ustawien
    base.create_db(getenv('SQL_DEL_SETTINGS')) #czyszczenie tabeli ustawien
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
    return render_template('index.html', links=links, settingsLinks=settings)

    # return redirect('/search')


# ***********************************
# ***   OFFERS operations         ***
# ***********************************

@app.route('/clear-offers')
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
def stopadd():
    # print("dlugosc tablicy:", len(procArray))
    # for p in procArray:
    #     p.setDaemon(False)
    #     p.terminate
    #     procArray.remove(p)
    #
    # print("dlugosc tablicy po terminate:", len(procArray))

    # loop_searching()

    tl.stop()

    # restart_program()
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
def search():
    # base = Database()
    # links = base.fetch_search()
    # settings = base.fetch_settings()
    # return render_template('index.html', links = links, settingsLinks = settings)
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



    return render_template('index.html', links=links, settingsLinks=settings)


# ***********************************
# *** transfer XLS file to base   ***
# ***********************************


@app.route('/excel', methods=['GET', 'POST'])
def excel():
    base = Database()
    xxx = base.base_to_xlsx()

    #
    # import win32ui
    # winobj = win32ui.CreateFileDialog(1, ".pdf", "", 0,
    #     "PDF Files (*.pdf)|*.pdf|All Files (*.*)|*.*|")
    # winobj.DoModal()
    # # return jsonify({'filepath': winobj.GetPathName()})




    #
    # from tkinter import Tk
    # from tkinter.filedialog import askopenfilename
    # root = Tk()
    # root.withdraw()
    # # ensure the file dialog pops to the top window
    # root.wm_attributes('-topmost', 1)
    # fname = askopenfilename(parent=root)
    # # return jsonify({'filepath': fname})
    #

    return render_template('index.html', info=xxx)


@app.route('/upload', methods=['GET', 'POST'])
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
