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
from .sql.models import Entries, Categories, Budget

from .expanses import input_id, add_expanse, get_total, get_expanse, plot_exp
from .budget import budget_id, addbudget, get_budget, get_all_bdg
from .incomes import get_income, add_income
from .categories import add_categories_from_list, get_all_cat, update_cat
from .read_file import read_csv, html_style, dwnl2db_inc, dwnl2db_exp
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

### deal with the login
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

### deal with the logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

    
#### Dashboard #####
@app.route('/')
def show_entries():
    data=input_id() # data for what is to delete id and name

    ### Get actual month ###
    today_date = datetime.today().strftime("%Y-%m-%d")
    num = datetime.today().month
    month=calendar.month_abbr[num]
    #############################

    expanse_tot = get_total() # get the total of expanses for the month
    update_cat()
    cat_exp = get_all_cat() # get all categories to use for add entries
    bdg = get_all_bdg() # get all budgets to use for add entries
    
    graphJSON=plot_exp(month=month) # get the plot

    return render_template('show_entries.html', graphJSON=graphJSON, data=data,
                            expanse_tot=round(expanse_tot,2), kd_exp=cat_exp,
                              today_date=today_date, month=month, bdg=bdg)

### Called when we add an entry
@app.route('/add', methods=['POST'])
def add_entry():
    print("ADD ENTRY")
    ### Check if its an expanse or an income
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



### Called when we delete an entry
@app.route('/del',methods=['GET', 'POST'])
def del_entry():
    print("DELETE")
    if not session.get('logged_in'):
        abort(401)
    
    select = request.form['id_data'] # get id of the row we want to delete  
    Entries.query.filter_by(id=int(select)).delete() # delete row by the id
    db_session.commit()
    
    return redirect(url_for('show_entries'))

### Called when we delete an entry by choosing an id
@app.route('/del_row/<id_val>')
def del_row(id_val=None):
    if not session.get('logged_in'):
        abort(401)
    
    print("DELETE ROW")
    select = id_val
    Entries.query.filter_by(id=int(select)).delete()
    db_session.commit()
    
    return redirect(url_for('show_data'))

### get all expanses and incomes and show them in a table
@app.route('/data', methods=['GET', 'POST'])
def show_data():
    print("SHOW DATA")

    entries = get_expanse()
    incomes = get_income()

    return render_template('study.html', entries=entries, incomes=incomes)

### get file selected
@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

### check if its a file we allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

### read and show csv
@app.route('/file_add', methods=['POST'])
def get_path():
    if not session.get('logged_in'):
        abort(401)
    
    df=read_csv()
    return render_template('file_read.html', show_table=1, file_table=df)

### Read csv
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
            dwnl2db_exp(file_path)
        if  request.form.get('check_inc') == 'Revenu':
            dwnl2db_inc(file_path)

    except:
        pass

    return render_template('file_read.html', show_table=show_table, file_table=file_table)

### Delete an entry for the budget
@app.route('/budget/del',methods=['GET', 'POST'])
def del_budget():
    print("DELETE")
    if not session.get('logged_in'):
        abort(401)
    
    select = request.form['id_data']
    print(select)
    
    Budget.query.filter_by(id=int(select)).delete()
    db_session.commit()
    
    return redirect(url_for('show_budget'))

### Add an entry for the budget
@app.route('/add_budget', methods=['POST'])
def add_budget():
    print("ADD BUDGET")

    if not session.get('logged_in'):
        abort(401)
    addbudget()
    
    return redirect(url_for('show_budget'))

### Delete an entry for the budget by id
@app.route('/budget/del_row/<id_val>')
def del_row_bdg(id_val=None):
    if not session.get('logged_in'):
        abort(401)
    
    print("DELETE ROW")
    select = id_val
    print(select)
    
    Budget.query.filter_by(id=int(select)).delete()
    db_session.commit()
    
    return redirect(url_for('show_budget'))

### Get all budget and show them
@app.route('/budget', methods=['GET', 'POST'])
def show_budget():
    print("Budget")
    
    data=budget_id()
    entries = get_budget()
    cat_exp = get_all_cat()
    

    return render_template('budget.html', data=data, entries=entries, kd_exp=cat_exp)

### delete catagories
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

### Add categories
@app.route('/add_cat', methods=['POST'])
def add_cat():
    print("ADD CATEGORY")
    if not session.get('logged_in'):
        abort(401)
    categ =  request.form['cat']
    print(categ)
    add_categories_from_list([categ])
    return redirect(url_for('show_cat'))

### Show categories
@app.route('/categories', methods=['GET', 'POST'])
def show_cat():
    print("Categories")
    
    entries = get_all_cat(lst=False)
    print(entries)
    return render_template('categories.html', entries=entries)