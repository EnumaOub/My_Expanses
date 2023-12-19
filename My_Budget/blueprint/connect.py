from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, Blueprint
from jinja2 import TemplateNotFound
from flask import current_app

from My_Budget.blueprint.home import main

connect = Blueprint('login', __name__,
                        template_folder='templates')


### deal with the login
@connect.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != current_app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != current_app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('home.show_entries'))
    return render_template('login.html', error=error)

### deal with the logout
@connect.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('budget.show_entries'))
