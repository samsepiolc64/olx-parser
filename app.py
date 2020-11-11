from flask import Flask, render_template, request
from database import Database
from getoffers import GetOffers
from xlsx2db import Xlsx2Db
from sys import argv
from os import getenv
import pandas as pd
#import csv
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route('/')
def start():
    return render_template('index.html')

@app.route('/setup')
def setup():
    base = Database(getenv('DB_NAME'))
    base.create_db(getenv('SQL_OFFER'))
    base.create_db(getenv('SQL_XLSX'))

@app.route('/add')
def add():
    for page in range(1, 25):
        offers = GetOffers(getenv('URL'), page)
        offers.get_offers()

@app.route('/list/<search>')
def index(search):
    base = Database(getenv('DB_NAME'))
    links = base.fetch_link(title = search)
    return render_template('index.html', zm = list(links))

@app.route('/search')
def search():
    base = Database(getenv('DB_NAME'))
    links = base.fetch_search()
    return render_template('index.html', zm = links)

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    return render_template('upload.html')

@app.route('/phrases', methods = ['GET', 'POST'])
def phrases():
    if request.method == 'POST':
        user_csv = request.form['csvfile']
        data = pd.read_excel(user_csv, index_col=None, header=None).values
        xlsx = Xlsx2Db()
        xlsx.xlsx2db(data)
        return render_template('phrases.html', data=data)

def main():
    if len(argv) > 1 and argv[1] == 'setup':
        setup()
    if len(argv) > 1 and argv[1] == 'list':
        index(search = argv[2])
    if len(argv) > 1 and argv[1] == 'add':
        add()

if __name__ == "__main__":
    app.run(debug=True)