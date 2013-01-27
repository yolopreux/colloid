from app import db
from app import BaseModel

class CombatEvent(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Actor(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Ability(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    swotr_id = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80), nullable=False)

class Target(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
