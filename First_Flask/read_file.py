import pandas as pd
import os
import csv
from sqlalchemy import text

try:
    from .sql.database import db_session, init_db, engine
    print('OK')
except:
    import sys
    sys.path.insert(0, r"""D:\Learn\Python\repos\First_Flask\First_Flask\sql""")
    from database import db_session, init_db, engine
    from models import Entries, Categories
    print('Except')

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

def expanse2db(df):
    res_df = pd.DataFrame()
    df = df[df['Revenu'] == '0']
    res_df["title"]=df["Catégorie 1"] 
    res_df["comment"]=df["Remarques"] 
    res_df["expanses"]=df["Dépense"] 
    try:
        res_df["expanses"]=res_df["expanses"].astype('float')
    except:
        res_df["expanses"]=res_df["expanses"].str.replace(',', '.').astype('float')
    res_df["date_exp"]=df["Date"] 
    res_df=res_df.rename_axis('id')
    return res_df

def income2db(df):
    res_df = pd.DataFrame()
    df = df[df['Dépense'] == '0']
    res_df["title"]=df["Catégorie 1"] 
    res_df["comment"]=df["Remarques"] 
    res_df["income"]=df["Revenu"] 
    try:
        res_df["income"]=res_df["income"].astype('float')
    except:
        res_df["income"]=res_df["income"].str.replace(',', '.').astype('float')
    res_df["date_exp"]=df["Date"] 
    res_df=res_df.rename_axis('id')
    return res_df

def send_exp(df, engine=engine):
    print("send expanse")
    print(df)
    sql = text("""SELECT title, comment, expanses, "date_exp" FROM entries""")
    with engine.connect() as db:
        sql_df = pd.read_sql(sql=sql, con=db)
        df=df[(~df.comment.isin(sql_df.comment)) | (~df.expanses.isin(sql_df.expanses))]
        df.to_sql('entries', con=db, if_exists='append', index=False)

def send_inc(df, engine=engine):
    print("send income")
    print(df)
    sql = text("""SELECT title, comment, income, "date_exp" FROM entries""")
    with engine.connect() as db:
        sql_df = pd.read_sql(sql=sql, con=db)
        df=df[(~df.comment.isin(sql_df.comment)) | (~df.income.isin(sql_df.income))]
        df.to_sql('entries', con=db, if_exists='append', index=False)

def send_inc2(df, engine=engine):
    print("send income2")
    print(df)
    inc = {"title": None, "comment": None, "income": None, "date_exp": None}
    keys = df.columns
    print(df.index)

    for ind in df.index:
        print(ind)
        inc["title"] = df['title'][ind]
        inc["comment"] = df['comment'][ind]
        inc["income"] = df['income'][ind]
        inc["date_exp"] = df["""date_exp"""][ind]
        e = Entries(title=inc["title"], comment=inc["comment"], income=inc["income"], date_exp=inc["date_exp"])
        print(inc)
        db_session.add(e)
        db_session.commit()

def dwnl2db_inc(path):
    df = read_csv(path)
    inc_df = income2db(df)
    print(inc_df)
    send_inc(inc_df)

def dwnl2db_exp(path):
    df = read_csv(path)
    exp_df = expanse2db(df)
    print(exp_df)
    send_exp(exp_df)


if __name__ == "__main__":
    path = r"D:\Learn\Python\backup_android_budget\Compte Courant-20230620-203137.csv"
    df = read_csv(path)
    #print(html_style(df.to_html(classes="data", header="true")))
    print(df.columns)
    rslt_df = df[df['Dépense'] == '0'] 
    print(rslt_df)
    exp_df = expanse2db(df)
    print(exp_df)
    inc_df = income2db(df)
    print(inc_df)
    send_exp(exp_df)
    send_inc(inc_df)
    
    

    #send2db(res_df)
    
