from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, Blueprint

from My_Budget.sql.database import db_session, init_db, engine

from My_Budget.functions.account import add_accounts_from_list, get_all_acc, add_account
from My_Budget.sql.models import Account

account = Blueprint('account', __name__,
                        template_folder='My_Budget\\templates')



### Called when we add an account
@account.route('/account/add', methods=['POST'])
def add_account_val():
    print("ADD ACCOUNT")
    if request.form['account'] != None:
        add_account()
        return redirect(url_for('account.show_acc'))

### delete catagories
@account.route('/account/del_cat/<id_val>')
def del_cat(id_val=None):
    if not session.get('logged_in'):
        abort(401)
    
    print("DELETE ACCOUNT")
    select = id_val # Get id of category to delete
    
    Account.query.filter_by(id=int(select)).delete()
    db_session.commit()
    
    return redirect(url_for('account.show_acc'))




### Show account
@account.route('/account', methods=['GET', 'POST'])
def show_acc():
    print("Categories")
    
    entries = get_all_acc(lst=False) # Get all categories in database
    return render_template('account.html', entries=entries)