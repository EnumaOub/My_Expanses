# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 20:14:41 2023

@author: rayan
"""

from sqlalchemy import Column, Integer, String, Date
from .. import Base

class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    

    def __init__(self, name=None):
        self.name = name


    def __repr__(self):
        return '<Name %r>' % (self.name)