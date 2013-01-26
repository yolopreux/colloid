from app import db
from app import BaseModel

class CombatEvent(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

class Actor(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

class Ability(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

