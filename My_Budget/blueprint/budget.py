from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, Blueprint
from jinja2 import TemplateNotFound

from My_Budget.sql.database import db_session, init_db, engine
from My_Budget.sql.models import Budget

from My_Budget.functions.budget import budget_id, addbudget, get_budget
from My_Budget.functions.categories import get_all_cat


budget = Blueprint('budget', __name__,
                        template_folder='templates')

#########################################
############ BUDGET #####################
#########################################

### Delete an entry for the budget
@budget.route('/budget/del',methods=['GET', 'POST'])
def del_budget():
    print("DELETE")
    if not session.get('logged_in'):
        abort(401)
    
    select = request.form['id_data']
    print(select)
    
    Budget.query.filter_by(id=int(select)).delete()
    db_session.commit()
    
    return redirect(url_for('budget.show_budget'))

### Add an entry for the budget
@budget.route('/budget/add_budget', methods=['POST'])
def add_budget():
    print("ADD BUDGET")

    if not session.get('logged_in'):
        abort(401)
    addbudget()
    
    return redirect(url_for('budget.show_budget'))

### Delete an entry for the budget by id
@budget.route('/budget/del_row_bdg/<id_val>')
def del_row_bdg(id_val=None):
    print("TESTTT")
    if not session.get('logged_in'):
        abort(401)
    
    print("DELETE ROW")
    print(id_val)
    select = id_val  # Get id of budget to delete
    
    Budget.query.filter_by(id=int(select)).delete() # delete by id
    db_session.commit()
    
    return redirect(url_for('budget.show_budget'))

### Get all budget and show them
@budget.route('/budget', methods=['GET', 'POST'])
def show_budget():
    print("Budget")
    
    data=budget_id() # Get Budget
    entries = get_budget() # Get Budget data
    cat_exp = get_all_cat() # Get categories to associate with budget
    
    return render_template('budget.html', data=data, entries=entries, kd_exp=cat_exp)