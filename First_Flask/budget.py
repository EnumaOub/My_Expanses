import os
import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import json
from sqlalchemy import create_engine, delete
from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg2 
import plotly.express as px
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd

from .sql.database import db_session, init_db, engine
from .sql.models import Budget, Categories

from datetime import datetime

def addbudget():
    bdg = {"name": None, "title": None, "value": None}
    bdg["name"] = request.form['title']
    bdg["title"] = request.form['comment']
    bdg["value"] = request.form['expanses']
    e = Budget(bdg["name"], bdg["title"], bdg["value"])
    db_session.add(e)
    db_session.commit()


def budget_id():
    data2=[]
    with engine.connect() as db:
        comment = db.execute(text("""SELECT title FROM public.budget """))
        idd = db.execute(text("""SELECT id FROM public.budget """))
        id_val=[]
        comment_val=[]
        for (idd_v , comment_v )in zip(idd, comment):
            id_val.append(idd_v[0])
            comment_val.append(comment_v[0])
            data2.append([idd_v[0], comment_v[0]])
        
        db.close()

    data = {"id": id_val, "title":comment_val}

    return data

def get_budget(bdg_val={}, all=True):
    
    bdg_tot =[]
    if all:
        with engine.connect() as db:
            tot = db.execute(text("""SELECT name, title, value FROM public.budget 
            WHERE value is not null""")).fetchall()

            for val in tot:
                bdg = {"name": None, "title": None, "value": None}
                bdg["name"] = val[0]
                bdg["title"]=val[1]
                bdg["value"]=val[2]

                bdg_tot.append(bdg)
    else:
        if bool(bdg_val):
            with engine.connect() as db:
                bdg_tot = db.execute(text("""SELECT * FROM public.budget WHERE id = :id AND
                                    title = :title AND comment = :comment AND expanses = :expanses AND date_exp = :date_exp 
                                    AND expanses is not null"""),
                                      {"id": bdg_val["id"],"title": bdg_val["title"], "comment": bdg_val["comment"], "expanses": bdg_val["expanses"],
                                        "date_exp": bdg_val["date_exp"]}).fetchall()

    return bdg_tot
