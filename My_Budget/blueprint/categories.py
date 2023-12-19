import os

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, Blueprint
from jinja2 import TemplateNotFound

from My_Budget.sql.database import db_session, init_db, engine
from My_Budget.sql.models import Categories

from My_Budget.functions.categories import add_categories_from_list, get_all_cat

cat = Blueprint('categories', __name__,
                        template_folder='templates')


#########################################
############ CATEGORIES #################
#########################################

### delete catagories
@cat.route('/categories/del_cat/<id_val>')
def del_cat(id_val=None):
    if not session.get('logged_in'):
        abort(401)
    
    print("DELETE CATEGORY")
    select = id_val # Get id of category to delete
    
    Categories.query.filter_by(id=int(select)).delete()
    db_session.commit()
    
    return redirect(url_for('categories.show_cat'))

### Add categories
@cat.route('/categories/add_cat', methods=['POST'])
def add_cat():
    print("ADD CATEGORY")
    if not session.get('logged_in'):
        abort(401)
    categ =  request.form['cat'] # Get category put by operator

    add_categories_from_list([categ]) # send to Database
    return redirect(url_for('categories.show_cat'))

### Show categories
@cat.route('/categories', methods=['GET', 'POST'])
def show_cat():
    print("Categories")
    
    entries = get_all_cat(lst=False) # Get all categories in database
    return render_template('categories.html', entries=entries)
