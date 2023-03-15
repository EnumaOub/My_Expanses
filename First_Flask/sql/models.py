# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 20:14:41 2023

@author: rayan
"""

from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class Entries(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True)
    comment = Column(String(120), unique=True)
    expanses = Column(Integer, unique=True)
    date = Column(DateTime(timezone=True), unique=True)

    def __init__(self, title=None, comment=None, expanses=None, date=None):
        self.title = title
        self.comment = comment
        self.expanses = expanses
        self.date = date

    def __repr__(self):
        return '<Title %r>' % (self.title)