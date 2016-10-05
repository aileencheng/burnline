# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
import sys
    
# create our application
app = Flask(__name__)
app.config.from_object(__name__)

# load default config and override config from an eivronmental variable
app.config.update(dict( 
    DATABASE=os.path.join(app.root_path, 'burnline.db'), 
    SECRET_KEY='development key', 
    USERNAME='admin', 
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    '''Connects to the specified database.'''
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
    
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    
@app.cli.command('initdb')
def initdb_command():
    '''Initializes the database.'''
    
    init_db()
    print 'Initialized database.'
    # need to log out

    
def get_db():
    '''Opens a new database connection if there is none yet for the 
    current application context.'''
    
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
    
@app.teardown_appcontext
def close_db(error):
    '''Closes the database again at the end of the request.'''
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    if 'user' in session:
    
        # delete later
        cur = db.execute('SELECT * FROM users')
        all_user_info = cur.fetchall()
        cur = db.execute('SELECT * FROM tasks')
        all_task_info = cur.fetchall()
        print >> sys.stderr, all_user_info
        print >> sys.stderr, ''
        print >> sys.stderr, all_task_info
        # stop deleting
    
        user = session['user']
        cur = db.execute('SELECT start_time, end_time FROM users \
                            WHERE username = ?', [user])
        timeline = cur.fetchone()
        
        cur = db.execute('SELECT title, description, weight, complete \
                        FROM tasks \
                        WHERE username=? \
                        ORDER BY id DESC', [user])
        tasks = cur.fetchall()
    else:
        tasks = []
        timeline = None
    return render_template('show_entries.html', tasks=tasks, timeline=timeline)
    
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    
    title = request.form['title']
    description = request.form['description']
    weight = request.form['weight']
    if request.form.has_key('complete'):
        complete = 1
    else:
        complete = 0
    username = session['user']
    
    db = get_db()
    db.execute('INSERT into tasks (username, title, description, weight, \
                complete) values (?, ?, ?, ?, ?)', 
                [username, title, description, weight, complete])
    db.commit()
    flash('New task was successfully posted')
    return redirect(url_for('show_entries'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cur = db.execute('SELECT username, password FROM users')
        all_login_info = cur.fetchall()
        
        user_exist = False
        pwd_correct = False
        for login_info in all_login_info:
            if login_info.username == username:
                user_exist = True
                # also need to check if password is correct
                if login_info.password == password:
                    pwd_correct = True
        
        if not user_exist:
            error = 'This timeline does not yet exist.'
        elif not pwd_correct:
            error = 'This password is incorrect.'
        else: 
            session['logged_in'] = True
            session['user'] = username
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)
    
@app.route('/new', methods=['GET', 'POST'])
def new_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        
        # need to check if the user exists
        db = get_db()
        cur = db.execute('SELECT username FROM users')
        all_users = cur.fetchall()
        
        # see if this username is already taken
        user_exist = False
        for user in all_users:
            if username == user.username:
                user_exist = True
        
        if user_exist:
            error = 'This username already exists. Please pick another one.'
        else: 
            session['logged_in'] = True
            session['user'] = username
            
            db.execute(
                'INSERT INTO users (username, password, start_time, end_time) \
                VALUES (?, ?, ?, ?)', 
                [username, password, start_time, end_time])
            db.commit()
                
            flash('New timeline has been created and you were logged in.')
            return redirect(url_for('show_entries'))
    return render_template('new_login.html', error=error)
    
    
    
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
                