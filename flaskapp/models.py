# -*- coding: utf-8 -*-
#!/usr/bin/env python

from sqlalchemy import Table, Column, Integer, String, Float
from sqlalchemy.orm import mapper
from database import metadata, db_session

class User(object):
    query = db_session.query_property()

    def __init__(self, name=None, email=None, progress=None):
        self.name = name
        self.email = email
        self.progress = progress

    def __repr__(self):
        return '<User %r>' % (self.name)

users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50), unique=True),
    Column('email', String(120), unique=False),
    Column('progress', Float)

)
mapper(User, users)
