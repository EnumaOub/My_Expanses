# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 19:02:40 2023

@author: rayan
"""

import os
from datetime import datetime

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
     
from sqlalchemy import create_engine, delete
from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg2 

import pandas as pd

from .sql.database import db_session, init_db, engine
from .sql.models import Entries, Categories

from .expanses import input_id, add_expanse, get_total, get_expanse
from .categories import add_categories_from_list, get_all_cat



app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'First_Flask.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
    


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')
    
    
@app.route('/')
def show_entries():
    data=input_id()
    entries = get_expanse()
    a=get_expanse(exp_val=entries[3],all=False)

    expanse_tot = get_total()

    kd_exp=["Alimentation","Loyer","Epargne", "Loisirs","Vacances", "Divers", "Sport", "Abonnements"]
    add_categories_from_list(kd_exp)
    cat_exp = get_all_cat()
    print(cat_exp)
    today_date = datetime.today().strftime("%Y-%m-%d")


    return render_template('show_entries.html', entries=entries, data=data, expanse_tot=expanse_tot, kd_exp=cat_exp, today_date=today_date)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    add_expanse()
    return redirect(url_for('show_entries'))




@app.route('/del',methods=['GET', 'POST'])
def del_entry():
    if not session.get('logged_in'):
        abort(401)
    
    print("DELETE")
    select = request.form['id_data']
    print(select)
    
    Entries.query.filter_by(id=int(select)).delete()
    db_session.commit()
    
    return redirect(url_for('show_entries'))



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
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/data')
def show_data():

    return render_template('study.html')