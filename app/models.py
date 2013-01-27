from app import db
from app import BaseModel


class Actor(db.Model, BaseModel):

    __tablename__ = 'colloid_actors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    is_npc = db.Column(db.Boolean)

    def __unicode__(self):
        return u'%s' % self.name


class Ability(db.Model, BaseModel):

    __tablename__ = 'colloid_abilities'

    id = db.Column(db.Integer, primary_key=True)
    swotr_id = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80), nullable=False)

    def __unicode__(self):
        return u'%s' % self.name


class Target(db.Model, BaseModel):

    __tablename__ = 'colloid_targets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __unicode__(self):
        return u'%s' % self.name


class CombatEvent(db.Model, BaseModel):

    __tablename__ = 'colloid_combat_events'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)
    actor_id = db.Column(db.Integer, db.ForeignKey('colloid_actors.id'), nullable=False)
    actor = db.relationship("Actor", backref=db.backref('actors'),
        primaryjoin='CombatEvent.actor_id==Actor.id', uselist=False, single_parent=True)
    target_id = db.Column(db.Integer, db.ForeignKey('colloid_actors.id'), nullable=False)
    target = db.relationship("Actor", backref=db.backref('targets'),
        primaryjoin='CombatEvent.target_id==Actor.id', uselist=False, single_parent=True)
    ability_id = db.Column(db.Integer, db.ForeignKey('colloid_abilities.id'), nullable=False)
    ability = db.relationship("Ability", backref=db.backref('abilities'),
        primaryjoin='CombatEvent.ability_id==Ability.id', uselist=False, single_parent=True)

    def __unicode__(self):
        return u'%s' % self.name
