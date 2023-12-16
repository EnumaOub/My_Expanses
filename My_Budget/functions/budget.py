from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

from sqlalchemy import text

from My_Budget.sql.database import db_session, init_db, engine
from My_Budget.sql.models import Entries, Categories, Budget



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







