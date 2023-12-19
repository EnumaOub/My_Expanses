import os
from datetime import datetime
import calendar
import pandas as pd

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, Blueprint
from jinja2 import TemplateNotFound

from My_Budget.sql.database import db_session, init_db, engine
from My_Budget.sql.models import Groceries

from My_Budget.functions.expanses import add_expanse
from My_Budget.functions.budget import get_all_bdg
from My_Budget.functions.categories import get_all_cat, update_cat
from My_Budget.functions.groceries import add_grocery, get_grocery

groceries = Blueprint('groceries', __name__,
                        template_folder='templates')

#########################################
############ Groceries ##################
#########################################

### Called when we delete an grocery by choosing an id
@groceries.route('/groceries/del_gcr/<id_gcr>')
def del_gcr(id_gcr=None):
    if not session.get('logged_in'):
        abort(401)
    
    print("DELETE GROCERY")
    select = id_gcr # Get id of row to delete
    Groceries.query.filter_by(id=int(select)).delete() # Delete by id
    db_session.commit()
    
    return redirect(url_for('groceries.show_grocery'))

### Called when we add grocery to entry by choosing an id

@groceries.route('/groceries/send_gcr/<id_gcr>/<title>/<expanse>/<comment>/<budget_title>/<date_exp>')
def send_gcr(title=None, expanse=None, comment=None,
              budget_title=None, date_exp=None, id_gcr=None):
    if not session.get('logged_in'):
        abort(401)
    
    print("ADD GROCERY TO EXPANSES")
    select = id_gcr # Get id of row to delete
    print()
    add_expanse([title, comment, expanse, date_exp, budget_title])
    Groceries.query.filter_by(id=int(select)).delete() # Delete by id
    db_session.commit()
    
    return redirect(url_for('groceries.show_grocery'))

### Called when we add grocery to entry by choosing an id

@groceries.route('/groceries/add_gcr_table/<id_gcr>/<title>/<expanse>/<comment>/<budget_title>/<link>')
def add_gcr_table(title=None, expanse=None, comment=None,
              budget_title=None, link=None, id_gcr=None):
    if not session.get('logged_in'):
        abort(401)
    
    print("ADD GROCERY")
    add_grocery([title, comment, expanse, link, budget_title])

    return redirect(url_for('groceries.show_grocery'))

### Called when we add an entry
@groceries.route('/groceries/add_gcr', methods=['POST'])
def add_gcr():
    print("ADD GROCERY")
    if not session.get('logged_in'):
        abort(401)
    add_grocery()

    return redirect(url_for('groceries.show_grocery'))

### get all groceries and show them in a table
@groceries.route('/groceries', methods=['GET', 'POST'])
def show_grocery():
    print("SHOW GROCERIES")

    entries = get_grocery()
    update_cat() # Update all categories
    cat_exp = get_all_cat() # get all categories to use for add entries
    bdg = get_all_bdg() # get all budgets to use for add entries
    
    

    return render_template('groceries.html', entries=entries, kd_exp=cat_exp,
                            bdg=bdg)