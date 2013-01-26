#!/usr/bin/env python
# encoding: utf-8
from flask import Flask
from flask.ext.script import Manager
from flask.ext.script import prompt_bool

from app import app
from app import db
from app.models import *

manager = Manager(app)

@manager.command
def dropdb():
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()

@manager.command
def createdb():
    db.create_all()

if __name__ == '__main__':
    manager.run()
