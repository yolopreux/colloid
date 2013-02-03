from app import db
from app import BaseModel


def get_or_create(model, **kwargs):

    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance
    instance = model(**kwargs)
    return instance.save()


class Actor(db.Model, BaseModel):

    __tablename__ = 'colloid_actors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    is_npc = db.Column(db.Boolean)
    swotr_id = db.Column(db.String(80), unique=True)

    def __unicode__(self):
        return u'%s' % self.name

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


class StatType(db.Model, BaseModel):

    __tablename__ = 'colloid_stat_types'

    id = db.Column(db.Integer, primary_key=True)
    swotr_id = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80), nullable=False)

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return u'<%s:%s>' % (self.name, self.swotr_id)



class EventStat(db.Model, BaseModel):

    __tablename__ = 'colloid_event_stats'

    id = db.Column(db.Integer, primary_key=True)
    stat_value = db.Column(db.Integer)
    threat_value = db.Column(db.Integer)
    stat_type_id = db.Column(db.Integer, db.ForeignKey('colloid_stat_types.id'),
                             nullable=True)
    stat_type = db.relationship("StatType", backref=db.backref('event_stats'),
        primaryjoin='EventStat.stat_type_id==StatType.id', uselist=False, single_parent=False)
    is_crit = db.Column(db.Boolean)

    def __unicode__(self):
        return u'%s - %s' % (self.stat_value, self.stat_type)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return u'<%s:%s:%s>' % (self.__class__, self.stat_value, self.stat_type)


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
    stat_id = db.Column(db.Integer, db.ForeignKey('colloid_event_stats.id'), nullable=True)
    stat = db.relationship("EventStat", backref=db.backref('combat_event_stats'),
        primaryjoin='CombatEvent.stat_id==EventStat.id', uselist=False, single_parent=True)

    def __unicode__(self):
        return u'Time: %s, Actor: %s, Target: %s, Ability: %s, Stat: %s' % (self.created_at, \
        self.actor, self.target, self.ability, self.stat)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return u'<%s, Time:%s, Actor:%s, Target:%s, Ability:%s>' % (self.__class__, \
            self.created_at, self.actor, self.target, self.ability)

    def is_heal(self):
        return 'Heal' in self.effect.name

    def is_damage(self):
        return 'Damage' in self.effect.name


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


class CombatFight(object):

    _instance = None
    start_at = None
    finish_at = None
    combat_events = []
    class_fight = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CombatFight, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def set_fight_class(cls, fight_class):
        cls.class_fight = fight_class

    def save(self):
        fight = self.class_fight(start_at=self.start_at,
                                 finish_at=self.finish_at,
                                 combat_events=self.combat_events)
        return fight.save()


class Fight(db.Model, BaseModel):

    __tablename__ = 'colloid_fights'
    _in_combat = None
    _combat_fight = CombatFight

    id = db.Column(db.Integer, primary_key=True)
    start_at = db.Column(db.DateTime)
    finish_at = db.Column(db.DateTime)
    combat_events = db.relationship('CombatEvent', secondary=event_fights,
        backref=db.backref('fights', lazy='dynamic'))

    def __str__(self):
        return u'<combat_events:%s>' % self.combat_events

    def __repr__(self):
        return u'<instance:%s:%s>' % (super(Fight, self).__repr__(),
                                      self.__str__())

    @classmethod
    def reset(cls):
        cls._combat_fight._instance = None
        cls._combat_fight.combat_events = []


CombatFight.set_fight_class(Fight)
