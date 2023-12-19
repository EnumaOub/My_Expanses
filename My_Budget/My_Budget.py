import os

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, Blueprint
from jinja2 import TemplateNotFound

from My_Budget.sql.database import db_session, init_db, engine

from My_Budget.blueprint.exp_inc import table
from My_Budget.blueprint.home import main
from My_Budget.blueprint.connect import connect
from My_Budget.blueprint.file_read import file
from My_Budget.blueprint.budget import budget
from My_Budget.blueprint.categories import cat
from My_Budget.blueprint.groceries import groceries

app = Flask(__name__) # create the application instance 
app.register_blueprint(table)
app.register_blueprint(main)
app.register_blueprint(connect)
app.register_blueprint(file)
app.register_blueprint(budget)
app.register_blueprint(cat)
app.register_blueprint(groceries)
app.config.from_object(__name__) # load config from this file , flaskr.py

UPLOAD_FOLDER = r"D:\Learn\Python\Money"
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


