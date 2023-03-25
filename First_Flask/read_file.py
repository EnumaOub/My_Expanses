import pandas as pd
import os
import csv
from sqlalchemy import text
try:
    from .sql.database import db_session, init_db, engine
except:
    import sys
    sys.path.insert(0, r"""D:\Learn\Python\repos\First_Flask\First_Flask\sql""")
    from database import db_session, init_db, engine

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


def get_delimiter(path, bytes = 4096):
    sniffer = csv.Sniffer()
    data = open(path, "r").read(bytes)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter

def read_csv(path):
    #path = request.files['path']
    delimiter = get_delimiter(path)
    df = pd.read_csv(path,delimiter=delimiter)
    return df

def html_style(df):
    df=df.replace('<th>','<th scope="col">')
    df=df.replace('<tr>','<tr class="table-primary">')
    df=df.replace('"dataframe data"','"table table-hover"')
    return df

def convert2db(df):
    res_df = pd.DataFrame()
    res_df["title"]=df["Catégorie 1"] 
    res_df["comment"]=df["Remarques"] 
    res_df["expanses"]=df["Dépense"] 
    try:
        res_df["expanses"]=res_df["expanses"].astype('float')
    except:
        res_df["expanses"]=res_df["expanses"].str.replace(',', '.').astype('float')
    res_df["date_exp"]=df["Date"] 
    return res_df

def send2db(df):
    sql = text("""SELECT title, comment, expanses, "date_exp" FROM entries""")
    with engine.connect() as db:
        sql_df = pd.read_sql(sql=sql, con=db)
        keys = sql_df.columns
        df_fin = pd.concat((df, sql_df)).drop_duplicates(subset=['title', 'comment', 'expanses', keys[-1]], keep=False)
        print(df_fin)
        df_fin.to_sql('entries', con=db, if_exists='append', index=False)

if __name__ == "__main__":
    path = r"D:\Learn\Python\backup_android_budget\Compte Courant-20230324-182003.csv"
    df = read_csv(path)
    #print(html_style(df.to_html(classes="data", header="true")))
    print(df.columns)
    res_df = convert2db(df)
    print(res_df)
    send2db(res_df)
    
    #send2db(res_df)
    
