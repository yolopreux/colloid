import re

from app import db
from app import BaseModel


def get_or_create(model, **kwargs):
    instance = model.db.session.query(model).filter_by(**kwargs).first()
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

    def __rep__(self):
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

    def __rep__(self):
        return u'<%s:%s:%s>' % (self.__class__, self.id, self.name)

    def __str__(self):
        return u'<%s:%s:%s>' % (self.__class__, self.id, self.name)


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

    def __rep__(self):
        return self.__str__()

    def __str__(self):
        return u'<%s, Time:%s, Actor:%s, Target:%s, Ability:%s>' % (self.__class__, \
            self.created_at, self.actor, self.target, self.ability)
