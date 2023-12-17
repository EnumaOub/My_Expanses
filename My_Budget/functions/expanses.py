from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import json
from sqlalchemy import text
import plotly.express as px
import plotly
import datetime
import pandas as pd

from My_Budget.sql.database import db_session, init_db, engine
from My_Budget.sql.models import Entries, Categories, Budget


def add_expanse(grocery=[]):
    if grocery:
        if grocery[4] == "NaN":
            e = Entries(grocery[0], grocery[1], grocery[2], grocery[3])
            db_session.add(e)
            db_session.commit()
        else:
            e = Entries(grocery[0], grocery[1], grocery[2], grocery[3], budget_title = grocery[4])
            db_session.add(e)
            db_session.commit()
    else:
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
    keys = df.columns
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

def get_expanse(exp_val={}, all=True, date=""):
    
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
    elif date:
        with engine.connect() as db:
            tot = db.execute(text("""SELECT id, title, comment, expanses, "date_exp", "budget_title" FROM public.entries 
            WHERE expanses is not null
                AND "date_exp" >= '"""+str(date)+"""'""")).fetchall()

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

    
    today = datetime.date.today()
    lst_month=today.strftime("%Y-%m-"+"01")
    ajd = today.strftime("%Y-%m-%d")

    data["""date_exp"""]= pd.to_datetime(data["""date_exp"""])

    data2 = data.loc[(data["""date_exp"""] >= lst_month)
                     & (data["""date_exp"""] <= ajd)]

    expanse_tot = data2['expanses'].sum()

    return expanse_tot


def plot_exp(month=""):
    with engine.connect() as db:
        data = pd.read_sql(text("select * from public.entries"), db)

    keys = data.columns
    print(keys)
    data = data.sort_values(by="""date_exp""")

    data["""date_exp"""] = pd.to_datetime(data["""date_exp"""])
    data['expanses'] = pd.to_numeric(data['expanses'], downcast='float')
    
    data['date'] = pd.to_datetime(data["""date_exp"""]).dt.to_period('M').astype('datetime64[ns]')
    data['month'] = data.date.sort_values(ascending=False).dt.to_period('M')

    print("data['expanses']")
    print(data['expanses'])

    figs = {
    c: px.pie(data.loc[data['month']==c], values="expanses", names="title", 
             labels="title").update_layout(autosize=False, width=600, height=600)
         for c in data.month.unique()
}
    
    defaultcat = data.month.unique()[0]
    fig = figs[defaultcat].update_traces(visible=True)
    for k in figs.keys():
        print(k)
        if k != defaultcat:
            fig.add_traces(figs[k].data)

    #finally build dropdown menu
    fig.update_layout(
        updatemenus=[
            {
                "buttons": [
                    {
                        "label": k,
                        "method": "update",
                        # list comprehension for which traces are visible
                        "args": [{"visible": [kk == k for kk in data.month.astype(str).unique()]} # update
                                ],
                
                    }
                    for k in data.month.astype(str).unique()
                ],
                "direction": "down", "x": 0.07, "y": 1.15
            }
        ]
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON







