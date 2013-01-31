import re

from app import db
from app import BaseModel


def get_or_create(model, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance
    instance = model(**kwargs)
    return instance


class Actor(db.Model, BaseModel):

    __tablename__ = 'colloid_actors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    is_npc = db.Column(db.Boolean)
    swotr_id = db.Column(db.String(80), unique=True)

    def __unicode__(self):
        return u'%s' % self.name

    def __init__(self, *args, **kwargs):
        data = None
        if 'data' in kwargs:
            try:
                match = re.match(r"(?P<name>[@|\w+|\s]{1,})", kwargs['data'])
                self.name = match.groupdict()['name'].strip()
                if '@' not in kwargs['data']:
                    self.is_npc = True
            except AttributeError, err:
                print err
#            data = re.findall(r"@([\w+]{1,})", kwargs['data'])
            del kwargs['data']
        super(Actor, self).__init__(*args, **kwargs)

    def __repr__(self):
        return u'<%s:%s:%s>' % (self.__class__, self.id, self.name)

    def __str__(self):
        return u'<%s:%s:%s>' % (self.__class__, self.id, self.name)


class Ability(db.Model, BaseModel):

    __tablename__ = 'colloid_abilities'

    id = db.Column(db.Integer, primary_key=True)
    swotr_id = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80), nullable=False)

    def __unicode__(self):
        return u'%s' % self.name

    def __repr__(self):
        return u'<%s:%s:%s>' % (self.__class__, self.id, self.name)

    def __str__(self):
        return u'<%s:%s:%s>' % (self.__class__, self.id, self.name)


class Target(db.Model, BaseModel):

    __tablename__ = 'colloid_targets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __unicode__(self):
        return u'%s' % self.name


event_fights = db.Table('colloid_event_fights', db.Model.metadata,
    db.Column('fight_id', db.Integer, db.ForeignKey('colloid_fights.id',
        onupdate="cascade", ondelete='cascade'), primary_key=True),
    db.Column('combat_event_id', db.Integer, db.ForeignKey('colloid_combat_events.id',
        onupdate="cascade", ondelete='cascade'), primary_key=True)
)

class CombatEvent(db.Model, BaseModel):

    __tablename__ = 'colloid_combat_events'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)
    actor_id = db.Column(db.Integer, db.ForeignKey('colloid_actors.id'), nullable=False)
    actor = db.relationship("Actor", backref=db.backref('actor_events'),
        primaryjoin='CombatEvent.actor_id==Actor.id', uselist=False, single_parent=False)
    target_id = db.Column(db.Integer, db.ForeignKey('colloid_actors.id'), nullable=False)
    target = db.relationship("Actor", backref=db.backref('target_events'),
        primaryjoin='CombatEvent.target_id==Actor.id', uselist=False, single_parent=False)
    ability_id = db.Column(db.Integer, db.ForeignKey('colloid_abilities.id'), nullable=False)
    ability = db.relationship("Ability", backref=db.backref('abilitiy_events'),
        primaryjoin='CombatEvent.ability_id==Ability.id', uselist=False, single_parent=False)
    effect_action_id = db.Column(db.Integer, db.ForeignKey('colloid_effect_actions.id'), nullable=False)
    effect_action = db.relationship("EffectAction", backref=db.backref('effect_action_events'),
        primaryjoin='CombatEvent.effect_action_id==EffectAction.id', uselist=False, single_parent=False)
    effect_id = db.Column(db.Integer, db.ForeignKey('colloid_effects.id'), nullable=False)
    effect = db.relationship("Effect", backref=db.backref('effect_events'),
        primaryjoin='CombatEvent.effect_id==Effect.id', uselist=False, single_parent=False)

    def __unicode__(self):
        return u'%s' % self.name

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return u'<%s, Time:%s, Actor:%s, Target:%s, Ability:%s>' % (self.__class__, \
            self.created_at, self.actor, self.target, self.ability)


class Guild(db.Model, BaseModel):

    __tablename__ = 'colloid_guilds'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)
    name = db.Column(db.String(80), nullable=False)
    contact_username = db.Column(db.String(80), nullable=False)

    def __unicode__(self):
        return u'%s' % self.name


class Effect(db.Model, BaseModel):

    __tablename__ = 'colloid_effects'

    id = db.Column(db.Integer, primary_key=True)
    swotr_id = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80), nullable=False)

    def __unicode__(self):
        return u'%s' % self.name


class EffectAction(db.Model, BaseModel):

    __tablename__ = 'colloid_effect_actions'

    id = db.Column(db.Integer, primary_key=True)
    swotr_id = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80), nullable=False)

    def __unicode__(self):
        return u'%s' % self.name


class Fight(db.Model, BaseModel):

    _instance = None
    __tablename__ = 'colloid_fights'

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Fight, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    id = db.Column(db.Integer, primary_key=True)
    start_at = db.Column(db.DateTime)
    finish_at = db.Column(db.DateTime)
    combat_events = db.relationship('CombatEvent', secondary=event_fights,
        backref=db.backref('fights', lazy='dynamic'))

    def __str__(self):
        return u'<combat_events:%s>' % self.combat_events

    def __repr__(self):
        return u'<instance:%s:%s>' % (super(Fight, self).__repr__(), self.__str__())

    @classmethod
    def reset(cls):
        cls._instance = None
