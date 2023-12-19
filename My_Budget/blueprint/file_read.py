import os
import pandas as pd

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, Blueprint
from jinja2 import TemplateNotFound
from flask import current_app


ALLOWED_EXTENSIONS = {'csv', 'xls'}

from My_Budget.functions.read_file import read_csv, html_style, dwnl2db_inc, dwnl2db_exp

file = Blueprint('file', __name__,
                        template_folder='templates')



#########################################
############ FILE_READING ###############
#########################################


### get file selected
@file.route('/file_add/uploads/<name>')
def download_file(name):
    print(name)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], name)

### check if its a file we allowed
def allowed_file(filename):
    print(filename.rsplit('.', 1)[1].lower())
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

### read and show csv
@file.route('/file_add', methods=['POST'])
def get_path():
    if not session.get('logged_in'):
        abort(401)
    
    df=read_csv() # Read file
    return render_template('file_read.html', show_table=1, file_table=df)

### Read csv
@file.route('/file_read', methods=['GET', 'POST'])
def get_file():
    print("FILE READ")
    
    file_table=None
    try:
        file = request.files['file']
        print(file)
        show_table = True
        if file.filename != '':

            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
            print(file_path)
            file.save(file_path)
            pd.set_option('display.width', 1000)
            pd.set_option('colheader_justify', 'center')

            file_table=read_csv(file_path)
            if request.form.get('check_exp') == 'Depense':
                print("File Reading Depenses")
                dwnl2db_exp(file_path)
            if  request.form.get('check_inc') == 'Revenu':
                print("File Reading Revenu")
                dwnl2db_inc(file_path)
            file_table=[html_style(file_table.to_html(classes='data', header="true"))]
            
    except Exception as error:
        print("An exception occurred:", error)
        show_table = False

    return render_template('file_read.html', show_table=show_table, file_table=file_table)