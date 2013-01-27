import os
from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy import Model
from flask.ext.admin.base import BaseView, expose
from flask.ext.restful import Resource, Api

from app.admin import init_admin


app = Flask(__name__)
app.config.from_object('configs')

db = SQLAlchemy(app)
api = Api(app)


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

    def __rep__(self):
        return u'<%s:%s>' % (self.__class__, self.id)


class CombatEvent(Resource):
    """Api resource for combat event"""
    def get(self, event_id):
        return {event_id: event_id}

    def put(self, event_id):
        from app.recounts import CombatParser
        CombatParser().parse(request.form['data'])
        return True

api.add_resource(CombatEvent, '/api/<string:event_id>')

init_admin(app)
