import os

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
     
from sqlalchemy import create_engine, delete
from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg2 

import pandas as pd

from .sql.database import db_session, init_db, engine
from .sql.models import Entries

from datetime import datetime

def add_expanse():
    exp = {"title": None, "comment": None, "expanses": None, "date_exp": None}
    exp["title"] = request.form['title']
    exp["comment"] = request.form['comment']
    exp["expanses"] = request.form['expanses']
    exp["date_exp"] = request.form['date_exp']
    e = Entries(exp["title"], exp["comment"], exp["expanses"], exp["date_exp"])
    db_session.add(e)
    db_session.commit()


def input_id():
    data2=[]
    with engine.connect() as db:
        comment = db.execute(text("""SELECT comment FROM public.entries """))
        idd = db.execute(text("""SELECT id FROM public.entries """))
        id_val=[]
        comment_val=[]
        for (idd_v , comment_v )in zip(idd, comment):
            id_val.append(idd_v[0])
            comment_val.append(comment_v[0])
            data2.append([idd_v[0], comment_v[0]])
        
        db.close()

    data = {"id": id_val, "title":comment_val}

    return data

def get_expanse(exp_val={}, all=True):
    exp = {"title": None, "comment": None, "expanses": None, "date_exp": None}
    exp_tot =[]
    if all:
        with engine.connect() as db:
            tot = db.execute(text("SELECT title, comment, expanses, date_exp FROM public.entries")).fetchall()
            for val in tot:
                exp["title"]=val[0]
                exp["comment"]=val[1]
                exp["expanses"]=val[2]
                exp["date_exp"]=val[3]
                exp_tot.append(exp)
    else:
        if bool(exp_val):
            with engine.connect() as db:
                exp_tot = db.execute(text("""SELECT * FROM public.entries WHERE 
                                    title = :title AND comment = :comment AND expanses = :expanses AND date_exp = :date_exp  """),
                                      {"title": exp_val["title"], "comment": exp_val["comment"], "expanses": exp_val["expanses"],
                                        "date_exp": exp_val["date_exp"]}).fetchall()
                print(exp_tot)
    return exp_tot


def get_total():
    with engine.connect() as db:
        expanse_tot = db.execute(text("""SELECT SUM(expanses) FROM public.entries """)).first()[0]
    return expanse_tot











