#!/usr/bin/env python
# encoding: utf-8
"""
    colloid project
    ~~~~~~~~~~~~~~

    Combat log analizer.

    :copyright: (c) 2013 by Darek <netmik12 [AT] gmail [DOT] com>
    :license: MIT, see LICENSE for more details
"""
import logging
import sys
from flask import Flask
from flask.ext.script import Manager
from flask.ext.script import prompt_bool

from app import app
from app import db
from app.models import *
from app.recounts import CombatParser

manager = Manager(app)

@manager.command
def dropdb():
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()

@manager.command
def createdb():
    dropdb()
    db.create_all()


def setLogLevel(verbose):
    logging.basicConfig(stream=sys.stdout)
    if not verbose:
        verbose = 0
    if int(verbose) < 2:
        app.logger.setLevel(logging.ERROR)
    if int(verbose) >= 3:
        app.logger.setLevel(logging.DEBUG)
    elif int(verbose) >= 2:
        app.logger.setLevel(logging.INFO)


@manager.option('-p', '--file', help='File path')
@manager.option('-d', '--dir', dest='directory', help='Directory path')
@manager.option('-v', '--verbosity', dest='verbose', help='Set verbose')
def parse(file=None, directory=None, verbose=None):
    """
    Parse combat logs by file or directory path
    """
    setLogLevel(verbose)
    CombatParser().run(file_name=file, directory=directory)

if __name__ == '__main__':
    manager.run()
