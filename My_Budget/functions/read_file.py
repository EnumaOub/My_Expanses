import pandas as pd
import csv
from sqlalchemy import text
import numpy as np
import xlrd

try:
    from My_Budget.sql.database import db_session, init_db, engine
    from My_Budget.sql.models import Entries, Categories, Budget
except:
    import sys
    sys.path.insert(1, r'D:\Learn\Python\repos\First_Flask\My_Budget\sql')
    from database import db_session, init_db, engine
    from models import Entries, Categories, Budget

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


def get_delimiter(path, bytes = 4096):
    sniffer = csv.Sniffer()
    data = open(path, "r").read(bytes)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter

def read_csv(path):
    if ".xls" in path:
        print('Read xls')
        df = pd.read_excel(path, skiprows=[0, 1],
                           usecols=["Date operation",
                                    "Categorie operation", "Sous Categorie operation",
                                    "Montant operation"])
        print()
        
        df.columns = ["Date", 'Remarques', 'Catégorie 1', 'Montant']
        df.loc[df['Catégorie 1'] == "A catégoriser", 'Catégorie 1'] = "Unknown"
        df['Montant'] = pd.to_numeric(df['Montant'], downcast="float")
        df['Montant'] = df['Montant'].astype(float).round(2)
        mask = df['Montant'] < 0
        df['Revenu'] = df['Montant'].mask(mask).round(2)
        df['Dépense'] = df['Montant'].mask(~mask).round(2).abs()
        df = df.fillna("0")
    else:
        delimiter = get_delimiter(path)
        df = pd.read_csv(path,delimiter=delimiter)
    return df

def html_style(df):
    df=df.replace('<th>','<th scope="col">')
    df=df.replace('<tr>','<tr class="table-primary">')
    df=df.replace('"dataframe data"','"table table-hover"')
    return df

def getsolde(path):
    if ".xls" in path:
        data = xlrd.open_workbook(path)
        py_sheet = data.sheet_by_index(0)
        solde = py_sheet.cell_value(0, 2)
        e = Entries(solde=solde)
        db_session.add(e)
        db_session.commit()

def delentrie():
    with engine.connect() as db:
        db.execute(text("""DELETE FROM public.entries"""))

def expanse2db(df):
    res_df = pd.DataFrame()
    df = df[df['Revenu'] == '0']
    res_df["title"]=df["Catégorie 1"] 
    res_df["comment"]=df["Remarques"] 
    res_df["expanses"]=df["Dépense"] 
    try:
        res_df["expanses"]=res_df["expanses"].astype('float').round(2)
    except:
        res_df["expanses"]=res_df["expanses"].str.replace(',', '.').astype('float').round(2)
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
        res_df["income"]=res_df["income"].astype('float').round(2)
    except:
        res_df["income"]=res_df["income"].str.replace(',', '.').astype('float').round(2)
    res_df["date_exp"]=df["Date"] 
    res_df=res_df.rename_axis('id')
    return res_df

def send_exp(df, engine=engine):
    print("send expanse")
    sql = text("""SELECT title, comment, expanses, "date_exp" FROM entries""")
    with engine.begin() as db:
        sql_df = pd.read_sql(sql=sql, con=db)
        df=df[(~df.comment.isin(sql_df.comment)) | (~df.expanses.isin(sql_df.expanses))]
        df.to_sql('entries', con=db, if_exists='append', index=False)

def send_inc(df, engine=engine):
    print("send income")
    sql = text("""SELECT title, comment, income, "date_exp" FROM entries""")
    with engine.begin() as db:
        sql_df = pd.read_sql(sql=sql, con=db)
        df=df[(~df.comment.isin(sql_df.comment)) | (~df.income.isin(sql_df.income))]
        df.to_sql('entries', con=db, if_exists='append', index=False)

def send_inc2(df, engine=engine):
    print("send income2")

    inc = {"title": None, "comment": None, "income": None, "date_exp": None}

    for ind in df.index:
        inc["title"] = df['title'][ind]
        inc["comment"] = df['comment'][ind]
        inc["income"] = df['income'][ind]
        inc["date_exp"] = df["""date_exp"""][ind]
        e = Entries(title=inc["title"], comment=inc["comment"], income=inc["income"], date_exp=inc["date_exp"])

        db_session.add(e)
        db_session.commit()

def dwnl2db_inc(path):
    df = read_csv(path)
    inc_df = income2db(df)
    send_inc(inc_df)


def dwnl2db_exp(path):
    df = read_csv(path)
    exp_df = expanse2db(df)
    send_exp(exp_df)


if __name__ == "__main__":
    path = r"D:\Learn\Python\Money\export_17_12_2023_13_09_36.xls"
    df = read_csv(path)
    data = xlrd.open_workbook(path)
    py_sheet = data.sheet_by_index(0)
    print(py_sheet.cell_value(0, 2))
    exp_df = expanse2db(df)
    print(exp_df)
    inc_df = income2db(df)
    print(inc_df)
    send_exp(exp_df)
    send_inc(inc_df)
    
    

    #send2db(res_df)
    
