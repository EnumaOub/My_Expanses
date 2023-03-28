import os

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
     
from sqlalchemy import create_engine, delete, func, and_
from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg2 

import pandas as pd

try:
    from .sql.database import db_session, init_db, engine
    from .sql.models import Entries, Categories
except:
    import sys
    sys.path.insert(0, r"""D:\Learn\Python\repos\First_Flask\First_Flask\sql""")
    from database import db_session, init_db, engine
    from models import Entries, Categories

from datetime import datetime

def del_duplicate():
    subq = (
        db_session.query(Categories.name, func.min(Categories.id).label("min_id"))
        .group_by(Categories.name)
    ) .subquery('date_min_id')
    sq = (
        db_session
        .query(Categories.id)
        .join(subq, and_(
            Categories.name == subq.c.name,
            Categories.id != subq.c.min_id)
        )
    ).subquery("subq")
    dq = (
        db_session
        .query(Categories)
        .filter(Categories.id.in_(sq))
    ).delete(synchronize_session=False)
    db_session.commit()

def update_cat():
    sql1 = text("""SELECT title FROM entries""")
    sql2 = text("""SELECT name FROM categories""")
    with engine.connect() as db:
        df_entries = pd.read_sql(sql=sql1, con=db)
        df_cat = pd.read_sql(sql=sql2, con=db)
        df_entries=df_entries.drop_duplicates().dropna()
        df_entries=df_entries[(~df_entries.title.isin(df_cat.name))]
        df_entries.rename(columns={"title": "name"}, inplace=True)
        df_entries.to_sql('categories', con=db, if_exists='append', index=False)

def add_categories_from_list(lst_cat):
    categ = {"name": None}
    for k in lst_cat:
        try:
            cat= str(k)
        except:
            print("Can't convert into string")
            print(k)
        categ["name"] = cat
        e = Categories(categ["name"])
        if db_session.query(Categories.id).filter_by(name=cat).first() is None:
            db_session.add(e)
            db_session.commit()
    del_duplicate()
    
    

def get_all_cat(lst = True):
    
    cat_tot = []
    cat_comp = []
    with engine.connect() as db:
        tot = db.execute(text("SELECT id, name FROM public.categories")).fetchall()
        for val in tot:
            categ = {"id": None, "name": None}
            categ["id"]=val[0]
            categ["name"]=val[1]
            cat_comp.append(categ)
            cat_tot.append(val[0])
    if lst:
        return cat_tot
    else:
        return cat_comp
   

if __name__ == "__main__":
    lst_cat=[]
    sql1 = text("""SELECT title FROM entries""")
    sql2 = text("""SELECT name FROM categories""")
    with engine.connect() as db:
        df_entries = pd.read_sql(sql=sql1, con=db)
        df_cat = pd.read_sql(sql=sql2, con=db)
        df_entries=df_entries.drop_duplicates().dropna()
        print(df_cat)
        print(df_entries)
        df_entries=df_entries[(~df_entries.title.isin(df_cat.name))]
        df_entries.rename(columns={"title": "name"}, inplace=True)
        print(df_entries)
        df_entries.to_sql('categories', con=db, if_exists='append', index=False)



