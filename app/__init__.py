import os
from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy import Model
from flask.ext.admin import Admin
from flask.ext.admin.base import BaseView, expose
from flask.ext.restful import Resource, Api

from app.recounts import CombatParser

_basedir = os.path.abspath(os.path.dirname(__file__) + '/../')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(_basedir, 'colloid.db')
db = SQLAlchemy(app)
api = Api(app)


class AdminView(BaseView):

    @expose('/')
    @expose('/admin')
    def index(self):
        return self.render('admin/index.html')


class BaseModel(Model):
    """Base class for models"""
    db = db
    def save(self, commit=True):
        self.db.session.add(self)
        if commit:
            try:
                self.db.session.commit()
            except:
                self.db.session.rollback()
                raise

        return self


class CombatEvent(Resource):
    """Api resource for combat event"""
    def get(self, event_id):
        return {event_id: event_id}

    def put(self, event_id):
        CombatParser().parse(request.form['data'])
        return True

api.add_resource(CombatEvent, '/api/<string:event_id>')

admin = Admin(app, name='My colloid')
admin.add_view(AdminView())
