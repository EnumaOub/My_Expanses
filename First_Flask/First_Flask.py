# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 19:02:40 2023

@author: rayan
"""

import os
from datetime import datetime
import calendar
import plotly.express as px

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory
     
from sqlalchemy import create_engine, delete
from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg2 

import pandas as pd

from .sql.database import db_session, init_db, engine
from .sql.models import Entries, Categories

from .expanses import input_id, add_expanse, get_total, get_expanse, plot_exp
from .incomes import get_income, plot_inc, add_income
from .categories import add_categories_from_list, get_all_cat, update_cat
from .read_file import read_csv, html_style, income2db, expanse2db, send_inc, send_exp, send_inc2
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = r"D:\Learn\Python\backup_android_budget\new"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv'}

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

    today_date = datetime.today().strftime("%Y-%m-%d")
    num = datetime.today().month
    month=calendar.month_abbr[num]

    expanse_tot = get_total()
    update_cat()
    cat_exp = get_all_cat()
    
    graphJSON=plot_exp(month=month)

    return render_template('show_entries.html', graphJSON=graphJSON, data=data, expanse_tot=round(expanse_tot,2), kd_exp=cat_exp, today_date=today_date, month=month)

@app.route('/add', methods=['POST'])
def add_entry():
    print("ADD ENTRY")
    try:
        if request.form['inc_exp'] == 'on':
            inc_exp = True
    except:
        inc_exp = False
    print(inc_exp)

    if not session.get('logged_in'):
        abort(401)
    if inc_exp:
        print("EXPANSES")
        add_expanse()
    else:
        print("INCOMES")
        add_income()
    return redirect(url_for('show_entries'))




@app.route('/del',methods=['GET', 'POST'])
def del_entry():
    print("DELETE")
    if not session.get('logged_in'):
        abort(401)
    
    select = request.form['id_data']
    print(select)
    
    Entries.query.filter_by(id=int(select)).delete()
    db_session.commit()
    
    return redirect(url_for('show_entries'))

@app.route('/del_row/<id_val>')
def del_row(id_val=None):
    if not session.get('logged_in'):
        abort(401)
    
    print("DELETE ROW")
    select = id_val
    print(select)
    
    Entries.query.filter_by(id=int(select)).delete()
    db_session.commit()
    
    return redirect(url_for('show_data'))



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

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/data', methods=['GET', 'POST'])
def show_data():
    print("SHOW DATA")

    entries = get_expanse()
    incomes = get_income()
    #print(incomes)
    #print(entries)
    return render_template('study.html', entries=entries, incomes=incomes)


@app.route('/file_add', methods=['POST'])
def get_path():
    if not session.get('logged_in'):
        abort(401)
    
    df=read_csv()
    return render_template('file_read.html', show_table=1, file_table=df)

@app.route('/file_read', methods=['GET', 'POST'])
def get_file():
    print("FILE READ")
    print(request.method)
    
    file_table=None
    titles=None
    try:
        file = request.files['file']
        show_table = True
        if file.filename != '':

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            pd.set_option('display.width', 1000)
            pd.set_option('colheader_justify', 'center')

            file_table=read_csv(file_path)
            df = file_table
            file_table=[html_style(file_table.to_html(classes='data', header="true"))]
            
    except:
        show_table = False

    try:
        if request.form.get('check_exp') == 'Depense':
            exp_df = expanse2db(df)
            send_exp(exp_df, engine)
        if  request.form.get('check_inc') == 'Revenu':
            inc_df = income2db(df)
            # print(df.rows())
            # print(inc_df.rows())
            send_inc2(inc_df, engine)
    except:
        pass

    return render_template('file_read.html', show_table=show_table, file_table=file_table)

@app.route('/budget', methods=['GET', 'POST'])
def show_budget():
    print("Budget")
    

    return render_template('budget.html')

@app.route('/del_cat/<id_val>')
def del_cat(id_val=None):
    if not session.get('logged_in'):
        abort(401)
    
    print("DELETE CATEGORY")
    select = id_val
    print(select)
    
    Categories.query.filter_by(id=int(select)).delete()
    db_session.commit()
    
    return redirect(url_for('show_cat'))

@app.route('/add_cat', methods=['POST'])
def add_cat():
    print("ADD CATEGORY")
    if not session.get('logged_in'):
        abort(401)
    categ =  request.form['cat']
    print(categ)
    add_categories_from_list([categ])
    return redirect(url_for('show_cat'))

@app.route('/categories', methods=['GET', 'POST'])
def show_cat():
    print("Categories")
    
    entries = get_all_cat(lst=False)
    print(entries)
    return render_template('categories.html', entries=entries)