# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 20:14:41 2023

@author: rayan
"""

from sqlalchemy import Column, Integer, String
from .database import Base

class Entries(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True)
    text = Column(String(120), unique=True)

    def __init__(self, title=None, text=None):
        self.title = title
        self.text = text

    def __repr__(self):
        return '<Title %r>' % (self.title)