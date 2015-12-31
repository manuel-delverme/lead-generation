# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
import json

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'connected'
PASSWORD = 'world'
# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('GREPR_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
            db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    # cur = g.db.execute('select title, text from entries order by id desc')
    # entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=[])

@app.route('/search', methods=['GET'])
def bad_search():
    return redirect(url_for('home'))

@app.route('/search', methods=['POST'])
def search():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # g.db.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
    # g.db.commit()
    # flash('New entry was successfully posted')
    search_results = []
    search_term = request.form['search_term']
    if search_term == "":
        return "nope"
    with open('../description_scraper/crawl_data.jsonlines') as crawler_results:
        for row in crawler_results:
            if search_term in row:
                entity = json.loads(row)
                if search_term in " ".join(entity['metadata']):
                    search_results.append(entity)
            
    return render_template('show_entries.html', term=search_term, entries=search_results)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=DEBUG)
