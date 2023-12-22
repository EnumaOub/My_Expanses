import pandas as pd

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
     
from sqlalchemy import create_engine, delete, func, and_
from sqlalchemy import text

from My_Budget.sql.database import db_session, init_db, engine
from My_Budget.sql.models import Account


def del_duplicate():
    subq = (
        db_session.query(Account.name, func.min(Account.id).label("min_id"))
        .group_by(Account.name)
    ) .subquery('date_min_id')
    sq = (
        db_session
        .query(Account.id)
        .join(subq, and_(
            Account.name == subq.c.name,
            Account.id != subq.c.min_id)
        )
    ).subquery("subq")
    dq = (
        db_session
        .query(Account)
        .filter(Account.id.in_(sq))
    ).delete(synchronize_session=False)
    db_session.commit()

def update_acc():
    print("UPDATE ACCOUNT")
    sql1 = text("""SELECT account, taux FROM entries""")
    sql2 = text("""SELECT account, taux FROM account""")
    with engine.begin() as db:
        df_entries = pd.read_sql(sql=sql1, con=db)
        df_cat = pd.read_sql(sql=sql2, con=db)
        df_entries=df_entries.drop_duplicates().dropna()
        df_entries=df_entries[(~df_entries.account.isin(df_cat.account))]
        df_entries.to_sql('account', schema='public', con=db, if_exists='append', index=False)

def add_accounts_from_list(lst_cat):
    categ = {"account": None}
    for k in lst_cat:
        try:
            cat= str(k)
        except Exception as error:
            print(error)
            print("Can't convert into string")
            print(k)
        categ["name"] = cat
        e = Account(account=categ["name"])
        if db_session.query(Account.id).filter_by(account=cat).first() is None:
            db_session.add(e)
            db_session.commit()
    del_duplicate()
    
def add_account():
    e = Account(taux=request.form['taux'],account=request.form['account'])
    
    db_session.add(e)
    db_session.commit()


def get_all_acc(lst = True):
    
    cat_tot = []
    cat_comp = []
    with engine.connect() as db:
        tot = db.execute(text("SELECT id, account, taux FROM public.account")).fetchall()
        for val in tot:
            categ = {"id": None, "account": None, "taux": None}
            categ["id"]=val[0]
            categ["account"]=val[1]
            categ["taux"]=val[2]
            cat_comp.append(categ)
            cat_tot.append(val[1])
    if lst:
        return cat_tot
    else:
        return cat_comp
   

if __name__ == "__main__":
    print()


