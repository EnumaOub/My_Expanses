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
    incomes = Column(DOUBLE_PRECISION, unique=True)
    result = Column(DOUBLE_PRECISION, unique=True)


    def __init__(self, title=None, comment=None, expanses=None, date_exp=None, incomes=None, result=None):
        self.title = title
        self.comment = comment
        self.expanses = expanses
        self.date_exp = date_exp
        self.incomes = incomes
        self.result = result

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