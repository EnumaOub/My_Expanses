from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, Blueprint

from My_Budget.sql.database import db_session, init_db, engine
from My_Budget.sql.models import Entries

from My_Budget.functions.expanses import input_id, add_expanse, get_expanse
from My_Budget.functions.incomes import get_income, add_income
from My_Budget.functions.categories import get_all_cat, update_cat


table = Blueprint('table', __name__,
                        template_folder='My_Budget\\templates')



### Called when we add an entry
@table.route('/data/add', methods=['POST'])
def add_entry():
    print("ADD ENTRY")
    ### Check if its an expanse or an income
    try:
        if request.form['inc_exp'] == 'on':
            inc_exp = True
    except:
        inc_exp = False

    if not session.get('logged_in'):
        abort(401)
    if inc_exp:
        print("EXPANSES")
        add_expanse()
    else:
        print("INCOMES")
        add_income()
    return redirect(url_for('table.show_data'))



### Called when we delete an entry
@table.route('/data/del',methods=['GET', 'POST'])
def del_entry():
    print("DELETE")
    if not session.get('logged_in'):
        abort(401)
    
    select = request.form['id_data'] # get id of the row we want to delete  
    Entries.query.filter_by(id=int(select)).delete() # delete row by the id
    db_session.commit()
    
    return redirect(url_for('table.show_data'))

### Called when we delete an entry by choosing an id
@table.route('/data/del_row/<id_val>')
def del_row(id_val=None):
    if not session.get('logged_in'):
        abort(401)
    
    print("DELETE ROW")
    select = id_val # Get id of row to delete
    Entries.query.filter_by(id=int(select)).delete() # Delete by id
    db_session.commit()
    
    return redirect(url_for('table.show_data'))

### get all expanses and incomes and show them in a table
@table.route('/data', methods=['GET', 'POST'])
def show_data():
    print("SHOW DATA")

    entries = get_expanse()
    incomes = get_income()
    update_cat() # Update all categories
    cat_exp = get_all_cat() # get all categories to use for add entries
    data=input_id() # data for what is to delete id and name


    return render_template('table.html', entries=entries, incomes=incomes,
                           kd_exp=cat_exp,  data=data)


