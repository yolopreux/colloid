import os
import json
import sys
import logging
from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy import Model
from flask.ext.admin.base import BaseView, expose
from flask.ext.restful import Resource, Api
from flask.ext.cache import Cache

from app.admin import init_admin

app = Flask(__name__)
app.config.from_object('configs')

if not app.debug:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.CRITICAL)

db = SQLAlchemy(app)
api = Api(app)
cache = Cache()
cache.init_app(app, config={'CACHE_TYPE': 'simple'})

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

    def __repr__(self):
        return u'<%s:id:%s>' % (super(BaseModel, self).__repr__(), self.id)

    def __str__(self):
        return u'<%s:id:%s>' % (super(BaseModel, self).__repr__(), self.id)


class CombatEvent(Resource):
    """Api resource for combat event"""
    def get(self, event_id):
        return {event_id: event_id}

    def put(self, event_id):
        from app.recounts import CombatParser
        lines = json.loads(request.form['data'])
        for line in lines:
            CombatParser().parse(line)
        return True

api.add_resource(CombatEvent, '/api/<string:event_id>')

init_admin(app)
