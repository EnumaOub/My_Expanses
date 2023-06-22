# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 20:14:41 2023

@author: rayan
"""

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
try:
    from .database import Base
except:
    from database import Base

class Entries(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True)
    comment = Column(String(120), unique=True)
    expanses = Column(DOUBLE_PRECISION, unique=True)
    date_exp = Column(Date, unique=True)
    income = Column(DOUBLE_PRECISION, unique=True)
    result = Column(DOUBLE_PRECISION, unique=True)
    budget_title = Column(String(50), unique=True)


    def __init__(self, title=None, comment=None, expanses=None, date_exp=None, income=None, result=None, budget_title=None):
        self.title = title
        self.comment = comment
        self.expanses = expanses
        self.date_exp = date_exp
        self.income = income
        self.result = result
        self.budget_title = budget_title

    def __repr__(self):
        return '<Title %r>' % (self.title)

class Budget(Base):
    __tablename__ = 'budget'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    title = Column(String(120), unique=True)
    value = Column(DOUBLE_PRECISION, unique=True)


    def __init__(self, name=None, title=None, value=None):
        self.name = name
        self.title = title
        self.value = value

    def __repr__(self):
        return '<Title %r>' % (self.title) 

class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    

    def __init__(self, name=None):
        self.name = name


    def __repr__(self):
        return '<Name %r>' % (self.name)