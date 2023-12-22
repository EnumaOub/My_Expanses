from datetime import datetime

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import json
from sqlalchemy import text
import plotly.express as px
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from dateutil.relativedelta import *

from My_Budget.sql.database import db_session, init_db, engine
from My_Budget.sql.models import Entries


def add_income():
    inc = {"title": None, "comment": None, "income": None, "date_exp": None}

    inc["title"] = request.form['title']
    inc["comment"] = request.form['comment']
    inc["income"] = request.form['expanses']
    inc["date_exp"] = request.form['date_exp']

    e = Entries(title=inc["title"], comment=inc["comment"], income=inc["income"], date_exp=inc["date_exp"])
    
    db_session.add(e)
    db_session.commit()

def add_solde():
    e = Entries(date_exp=request.form['date_exp'], solde=request.form['solde'])
    db_session.add(e)
    db_session.commit()


def add_income_db(df):
    inc = {"title": None, "comment": None, "income": None, "date_exp": None}
    keys = df.columns
    for index, row in df.iterrows():
        inc["title"] = row['title']
        inc["comment"] = row['comment']
        inc["income"] = row['income']
        inc["date_exp"] = row[keys[-1]]
        e = Entries(title=inc["title"], comment=inc["comment"], income=inc["income"], date_exp=inc["date_exp"])
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

def get_income(inc_val={}, all=True, date=""):
    
    inc_tot =[]
    if all:
        with engine.connect() as db:
            tot = db.execute(text("""SELECT id, title, comment, income, "date_exp" FROM public.entries 
            WHERE income is not null""")).fetchall()

            for val in tot:
                inc = {"id": None,"title": None, "comment": None, "income": None, "date_exp": None}
                inc["id"] = val[0]
                inc["title"]=val[1]
                inc["comment"]=val[2]
                inc["income"]=val[3]
                inc["date_exp"]=val[4]
                
                inc_tot.append(inc)
    elif date:
        with engine.connect() as db:
            tot = db.execute(text("""SELECT id, title, comment, income, "date_exp" FROM public.entries 
            WHERE income is not null
                AND "date_exp" >= '"""+str(date)+"""'""")).fetchall()

            for val in tot:
                inc = {"id": None,"title": None, "comment": None, "income": None, "date_exp": None}
                inc["id"] = val[0]
                inc["title"]=val[1]
                inc["comment"]=val[2]
                inc["income"]=val[3]
                inc["date_exp"]=val[4]
                
                inc_tot.append(inc)
    
    else:
        if bool(inc_val):
            with engine.connect() as db:
                inc_tot = db.execute(text("""SELECT * FROM public.entries WHERE id = :id AND
                                    title = :title AND comment = :comment AND income = :income AND date_exp = :date_exp AND income is not null"""),
                                      {"id": inc_val["id"],"title": inc_val["title"], "comment": inc_val["comment"], "income": inc_val["income"],
                                        "date_exp": inc_val["date_exp"]}).fetchall()

    return inc_tot


def get_total():
    with engine.connect() as db:
        expanse_tot = db.execute(text("""SELECT SUM(income) FROM public.entries """)).first()[0]
    return expanse_tot

def get_all_inc(month=""):

    with engine.connect() as db:
        data = pd.read_sql(text("""select income, "date_exp" from public.entries"""), db)

    if month:
       lst_month = month
       ajd = str((datetime.strptime(month, "%Y-%m-%d") + 
                                                relativedelta(months=+1)).strftime('%Y-%m-%d'))
    else: 
        today = datetime.date.today()
        lst_month=today.strftime("%Y-%m-"+"01")
        ajd = today.strftime("%Y-%m-%d")

    data["""date_exp"""]= pd.to_datetime(data["""date_exp"""])

    data2 = data.loc[(data["""date_exp"""] >= lst_month)
                     & (data["""date_exp"""] < ajd)]

    income_tot = data2['income'].sum()

    return income_tot


def plot_inc(month=""):
    with engine.connect() as db:
        data       = pd.read_sql(text("select * from public.entries"), db)
        data_exp       = pd.read_sql(text(""" SELECT SUM(income) AS income, "date_exp"
                                            FROM public.entries WHERE income is not null
                                              GROUP BY "date_exp" """), db);



    keys = data.columns
    print(keys)
    data = data.sort_values(by="""date_exp""")
    data_exp = data_exp.sort_values(by="""date_exp""")

    today = datetime.date.today()
    lst_month=today.strftime("01"+"/%m/%Y")
    ajd = today.strftime("%d/%m/%Y")
    data2 = data.loc[(data["""date_exp"""] >= lst_month)
                     & (data["""date_exp"""] < ajd)]
    figure1 = px.bar(y=data2["income"], x=data2["title"], color=data2["title"])
    print(data2)
    # For as many traces that exist per Express figure, get the traces from each plot and store them in an array.
    # This is essentially breaking down the Express fig into it's traces
    figure1_traces = []
    
    for trace in range(len(figure1["data"])):
        figure1_traces.append(figure1["data"][trace])

    fig = make_subplots(1, 2,
                    subplot_titles=['Time', 'Incomes (' + month + ')'])
    for traces in figure1_traces:
        fig.append_trace(traces, row=1, col=2)

    
    fig.add_trace(go.Scatter(x=data_exp["""date_exp"""], y=data_exp["income"], showlegend=False),
                  1,1)
    
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin=dict(t=35, b=10, l=0, r=0), title_font_color='White',
    legend=dict(
        font=dict(
            size=18,
            color="white"
        ),
        title_text='Global Income'    )
)
    fig.update_layout(font=dict(
            size=12,  # Set the font size here
            color="white"
    ))

    for i in fig['layout']['annotations']:
        i['font'] = dict(size=20,color='white')

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON







