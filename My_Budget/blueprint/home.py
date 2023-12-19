from datetime import datetime
import calendar

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, Blueprint
from jinja2 import TemplateNotFound

from My_Budget.functions.expanses import input_id, get_total, get_expanse, plot_exp_month, plot_all
from My_Budget.functions.incomes import get_income, get_all_inc
from My_Budget.functions.groceries import get_grocery

main = Blueprint('home', __name__,
                        template_folder='templates')
    
#### Dashboard #####
@main.route('/', methods=['GET', 'POST'])
def show_entries():
    data=input_id() # data for what is to delete id and name

    ### Get actual month ###
    try:
        print(request.form['bdaymonth'])
        today_date = datetime.today().strftime("%Y-%m")
        month_year = request.form['bdaymonth'] + "-01"
        num = datetime.strptime(month_year, "%Y-%m-%d").month
        month=calendar.month_abbr[num]
    except Exception as error:
        print("An exception occurred:", error)
        today_date = datetime.today().strftime("%Y-%m")
        month_year = str(datetime.today().strftime("%Y-%m") + "-01")
        num = datetime.today().month
        month=calendar.month_abbr[num]
    #############################

    
    

    expanse_tot = round(get_total(month=month_year),2) # get the total of expanses for the month
    income_tot = round(get_all_inc(month=month_year), 2)
    
    entries = get_expanse(all = False, date=month_year)
    incomes = get_income(all = False, date=month_year)
    groceries = get_grocery()
    
    graphJSON = plot_exp_month(month_year) # get the plot
    fig_tot, fig_bar = plot_all()

    return render_template('show_entries.html', graphJSON=graphJSON, data=data,
                            expanse_tot=expanse_tot, income_tot=income_tot,
                              today_date=today_date, month=month,
                              entries=entries, incomes=incomes, groceries = groceries,
                              fig_tot=fig_tot, fig_bar=fig_bar)

