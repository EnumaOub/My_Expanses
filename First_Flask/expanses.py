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
from .sql.models import Entries, Categories

from datetime import datetime

def add_expanse():
    if request.form.get('bdg', None) is None:
        exp = {"title": None, "comment": None, "expanses": None, "date_exp": None}
        exp["title"] = request.form['title']
        exp["comment"] = request.form['comment']
        exp["expanses"] = request.form['expanses']
        exp["date_exp"] = request.form['date_exp']
        e = Entries(exp["title"], exp["comment"], exp["expanses"], exp["date_exp"])
        db_session.add(e)
        db_session.commit()
    else:
        exp = {"title": None, "comment": None, "expanses": None, "date_exp": None, "budget_title":None}
        exp["title"] = request.form['title']
        exp["comment"] = request.form['comment']
        exp["expanses"] = request.form['expanses']
        exp["date_exp"] = request.form['date_exp']
        exp["budget_title"] = request.form['bdg']
        e = Entries(exp["title"], exp["comment"], exp["expanses"], exp["date_exp"], budget_title = exp["budget_title"])
        db_session.add(e)
        db_session.commit()

def add_expanse_db(df):
    exp = {"title": None, "comment": None, "expanses": None, "date_exp": None}
    keys = sql_df.columns
    for index, row in df.iterrows():
        exp["title"] = row['title']
        exp["comment"] = row['comment']
        exp["expanses"] = row['expanses']
        exp["date_exp"] = row[keys[-1]]
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
    
    exp_tot =[]
    if all:
        with engine.connect() as db:
            tot = db.execute(text("""SELECT id, title, comment, expanses, "date_exp", "budget_title" FROM public.entries 
            WHERE expanses is not null""")).fetchall()

            for val in tot:
                exp = {"id": None,"title": None, "comment": None, "expanses": None, "date_exp": None, "budget_title":None}
                exp["id"] = val[0]
                exp["title"]=val[1]
                exp["comment"]=val[2]
                exp["expanses"]=val[3]
                exp["date_exp"]=val[4]
                exp["budget_title"]=val[5]
                
                exp_tot.append(exp)
    else:
        if bool(exp_val):
            with engine.connect() as db:
                exp_tot = db.execute(text("""SELECT * FROM public.entries WHERE id = :id AND
                                    title = :title AND comment = :comment AND expanses = :expanses AND date_exp = :date_exp AND budget_title =:budget_title
                                    AND expanses is not null"""),
                                      {"id": exp_val["id"],"title": exp_val["title"], "comment": exp_val["comment"], "expanses": exp_val["expanses"],
                                        "date_exp": exp_val["date_exp"], "budget_title": exp_val["budget_title"]}).fetchall()

    return exp_tot


def get_total():

    with engine.connect() as db:
        data       = pd.read_sql(text("select * from public.entries"), db)

    import datetime
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    lst_month=today.strftime("%Y-%m-"+"01")
    ajd = today.strftime("%Y-%m-%d")

    data["""date_exp"""]= pd.to_datetime(data["""date_exp"""])

    data2 = data.loc[(data["""date_exp"""] >= lst_month)
                     & (data["""date_exp"""] < ajd)]

    expanse_tot = data2['expanses'].sum()

    return expanse_tot


def plot_exp(month=""):
    with engine.connect() as db:
        data       = pd.read_sql(text("select * from public.entries"), db)
        data_exp       = pd.read_sql(text(""" SELECT SUM(expanses) AS expanses, "date_exp"
                                            FROM public.entries WHERE expanses is not null
                                              GROUP BY "date_exp" """), db);



    keys = data.columns
    print(keys)
    data.sort_values(by="""date_exp""", inplace = True)
    data_exp.sort_values(by="""date_exp""", inplace = True)

    import datetime
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    lst_month=today.strftime("%Y-%m-"+"01")
    ajd = today.strftime("%Y-%m-%d")

    data["""date_exp"""]= pd.to_datetime(data["""date_exp"""])
    data_exp["""date_exp"""]= pd.to_datetime(data_exp["""date_exp"""])

    data2 = data.loc[(data["""date_exp"""] >= lst_month)
                     & (data["""date_exp"""] < ajd)]

    try:
        figure1 = px.bar(y=data2["expanses"], x=data2["title"], color=data2["title"])
    except:
        figure1 = px.bar(y=data["expanses"], x=data["title"], color=data["title"])

    # For as many traces that exist per Express figure, get the traces from each plot and store them in an array.
    # This is essentially breaking down the Express fig into it's traces
    figure1_traces = []
    
    for trace in range(len(figure1["data"])):
        figure1_traces.append(figure1["data"][trace])

    fig = make_subplots(1, 2,
                    subplot_titles=['Time', 'Expanses (' + month + ')'])
    for traces in figure1_traces:
        fig.append_trace(traces, row=1, col=2)

    
    fig.add_trace(go.Scatter(x=data_exp["""date_exp"""], y=data_exp["expanses"], showlegend=False),
                  1,1)
    
    fig.update_layout(margin=dict(t=35, b=10, l=0, r=0),
    legend=dict(
        font=dict(
            size=18
        ),
        title_text='Global Expanses'    )
)
    fig.update_layout(font=dict(
            size=12
    ))

    for i in fig['layout']['annotations']:
        i['font'] = dict(size=20)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON







