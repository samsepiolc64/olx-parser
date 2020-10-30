from flask import Flask, render_template
from database import Database
from getoffers import GetOffers
from sys import argv
from os import getenv
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route('/setup')
def setup():
    base = Database(getenv('DB_NAME'))
    base.create_db(getenv('SQL'))

@app.route('/add')
def add():
    for page in range(1, 25):
        return(f'strona {page}')
        offers = GetOffers(getenv('URL'), page)
        offers.get_offers()

@app.route('/list/<search>')
def index(search):
    #print('lista linkow')
    base = Database(getenv('DB_NAME'))
    links = base.fetch_link(title=search)
    return render_template('index.html', zm = list(links))
    #for link in links:
    #    print(link[2])



def main():
    if len(argv) > 1 and argv[1] == 'setup':
        setup()
    if len(argv) > 1 and argv[1] == 'list':
        index(search = argv[2])
    if len(argv) > 1 and argv[1] == 'add':
        add()

if __name__ == "__main__":
    #main()
    app.run(debug=True)