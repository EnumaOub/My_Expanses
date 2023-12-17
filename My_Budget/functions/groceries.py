from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

from sqlalchemy import text
from datetime import datetime

from My_Budget.sql.database import db_session, init_db, engine
from My_Budget.sql.models import Entries, Categories, Budget, Groceries


def add_grocery(grocery=[]):
    if grocery:
        if grocery[4] == "NaN":
            e = Groceries(grocery[0], grocery[1], grocery[2], grocery[3])
            db_session.add(e)
            db_session.commit()
        else:
            e = Groceries(grocery[0], grocery[1], grocery[2], grocery[3], budget_title = grocery[4])
            db_session.add(e)
            db_session.commit()
    if request.form.get('bdg', None) is None:
        grocery = {"title": None, "expanse": None, "comment": None, "link": None}
        grocery["title"] = request.form['title']
        grocery["expanse"] = request.form['expanses']
        grocery["comment"] = request.form['comment']
        grocery["link"] = request.form['link']
        e = Groceries(grocery["title"], grocery["comment"], grocery["expanse"], grocery["link"])
        db_session.add(e)
        db_session.commit()
    else:
        grocery = {"title": None, "expanse": None, "comment": None, "link": None, "budget_title":None}
        grocery["title"] = request.form['title']
        grocery["expanse"] = request.form['expanses']
        grocery["budget_title"] = request.form['bdg']
        grocery["comment"] = request.form['comment']
        grocery["link"] = request.form['link']
        e = Groceries(grocery["title"], grocery["comment"], grocery["expanse"], grocery["link"], budget_title = grocery["budget_title"])
        db_session.add(e)
        db_session.commit()

def id_gcr():
    data2=[]
    with engine.connect() as db:
        comment = db.execute(text("""SELECT comment FROM public.groceries """))
        idd = db.execute(text("""SELECT id FROM public.grocerie """))
        id_val=[]
        comment_val=[]
        for (idd_v , comment_v )in zip(idd, comment):
            id_val.append(idd_v[0])
            comment_val.append(comment_v[0])
            data2.append([idd_v[0], comment_v[0]])
        
        db.close()

    data = {"id": id_val, "title":comment_val}

    return data

def get_grocery():
    grc_tot = []
    with engine.connect() as db:
        tot = db.execute(text("""SELECT id, title, comment, link, expanse, "budget_title" FROM public.groceries 
        WHERE expanse is not null""")).fetchall()

        for val in tot:
            grocery = {"id": None, "title": None, "comment": None, "expanse": None, "link": None, "budget_title":None}
            grocery["id"] = val[0]
            grocery["title"]=val[1]
            grocery["comment"]=val[2]
            grocery["link"]=val[3]
            grocery["expanse"]=val[4]
            grocery["budget_title"]=val[5]
            if val[5] == None:
                grocery["budget_title"]="NaN"
            grocery.update({"date_exp": str(datetime.today().strftime("%Y-%m-%d"))})
            
            grc_tot.append(grocery)


    return grc_tot

