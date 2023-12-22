from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

from sqlalchemy import text
import datetime
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from My_Budget.sql.database import db_session, init_db, engine
from My_Budget.sql.models import Budget

from My_Budget.functions.expanses import get_exp_month


def addbudget():
    bdg = {"name": None, "title": None, "value": None, "monthly": False}
    bdg["title"] = request.form['title']
    bdg["value"] = request.form['expanses']
    try:
        bdg["monthly"] = bool(request.form['monthly'])
    except:
        bdg["monthly"] = False
    e = Budget(title=bdg["title"], value=bdg["value"], monthly=bdg["monthly"])
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
    
    bdg_tot = []
    if all:
        with engine.connect() as db:
            tot = db.execute(text("""SELECT id, title, value, monthly FROM public.budget 
            WHERE value is not null""")).fetchall()
            for val in tot:
                bdg = {"id": None, "title": None, "value": None, "monthly": False}
                bdg["id"] = val[0]
                bdg["title"] = val[1]
                bdg["value"] = val[2]
                bdg["monthly"] = val[3]
                bdg_tot.append(bdg)
    else:
        if bool(bdg_val):
            with engine.connect() as db:
                bdg_tot = db.execute(text("""SELECT * FROM public.budget WHERE id = :id AND
                                    title = :title AND value = :value AND monthly = :monthly AND value is not null"""),
                                      {"id": bdg_val["id"],"title": bdg_val["title"], "value": bdg_val["value"],
                                        "monthly": bdg_val["monthly"]}).fetchall()
    return bdg_tot


def get_all_bdg(lst = True):
    
    cat_tot = []
    cat_comp = []
    with engine.connect() as db:
        tot = db.execute(text("SELECT id, title FROM public.budget")).fetchall()
        for val in tot:
            categ = {"id": None, "name": None}
            categ["id"]=val[0]
            categ["name"]=val[1]
            cat_comp.append(categ)
            cat_tot.append(val[1])
    if lst:
        return cat_tot
    else:
        return cat_comp



def plot_bdg_month(date):
    bdg_data = get_budget()

    expanses = get_exp_month(date)
    expanses = expanses.sort_values(by="""date_exp""")
    expanses["""date_exp"""] = pd.to_datetime(expanses["""date_exp"""])
    expanses['expanses'] = expanses['expanses'].astype(float).round(2)

    fig = go.Figure()

    for bdg in bdg_data:
        name = bdg["title"]
        val_bdg = bdg["value"]
        val_exp = expanses[expanses['title']==name]["expanses"].sum()
        percent = round((val_exp/val_bdg)*100, 2)
        fig.add_trace(go.Bar(x=[name], y=[percent], 
                   name=str(name)))

    fig.update_layout(autosize=False, width=600, height=600)
    fig.update_layout(xaxis_title="Budget",
                    yaxis_title="Budget percent [%]")
    fig.update_yaxes(range=[-1, 101])
    

    fig_bdg = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return fig_bdg



