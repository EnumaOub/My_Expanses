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
from .sql.models import Entries, Categories

from datetime import datetime



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
        db_session.add(e)
        db_session.commit()

def get_all_cat():
    categ = {"name": None}
    cat_tot =[]

    with engine.connect() as db:
        tot = db.execute(text("SELECT name FROM public.categories")).fetchall()
        for val in tot:
            categ["name"]=val[0]
            cat_tot.append(val[0])
    
    return cat_tot
   





