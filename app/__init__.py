import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

_basedir = os.path.abspath(os.path.dirname(__file__) + '/../')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(_basedir, 'colloid.db')
db = SQLAlchemy(app)
