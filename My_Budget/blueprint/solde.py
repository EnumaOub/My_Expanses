from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, Blueprint

from My_Budget.sql.database import db_session, init_db, engine

from My_Budget.functions.incomes import add_solde

solde = Blueprint('solde', __name__,
                        template_folder='My_Budget\\templates')


### Main Solde
@solde.route('/solde', methods=['POST', 'GET'])
def solde_val():
    print("ACCOUNT")
    return render_template('solde.html')


### Called when we add an solde
@solde.route('/solde/add', methods=['POST'])
def add_solde_val():
    print("ADD SOLDE")
    if request.form['solde'] != None:
        add_solde()
        return redirect(url_for('solde.solde_val'))
    
    
