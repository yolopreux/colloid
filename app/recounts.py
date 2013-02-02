import os
import re
import weakref
from datetime import datetime, time
from datetime import timedelta

from app import models
from app import app


def slugify(str):
    str = str.lower()
    return re.sub(r'\W+', '_', str)


def model_id(model, **kwargs):
    model_id = slugify(str(model))
    for key, value in kwargs.iteritems():
        model_id += slugify(key) + '__' + slugify(value)
    return model_id


class Recount(object):

    _instance = None
    _data = weakref.WeakValueDictionary()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Recount, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def set(self, key, data):
        self._data[key] = data

    def get(self, key):
        try:
            return self._data[key]
        except:
            return None


def get_or_create(model, **kwargs):

    instance = Recount().get(model_id(model, **kwargs))
    if instance:
        return instance

    instance = models.get_or_create(model, **kwargs)
    Recount().set(model_id(model, **kwargs), instance)

    return instance


class InvalidDataError(Exception):
    pass


class CombatParser(object):


    ability_pattern = r"(?P<name>[a-zA-Z\s^/{^/}]{0,}) {(?P<swotr_id>[\d+]{1,})}"
    efect_pattern = r"(?P<action>[a-zA-Z'\s^/{^/}]{0,}) {(?P<action_swotr_id>[\d+]{1,})}: (?P<name>[a-zA-Z'\s^/{^/}/(/)]{0,}) {(?P<name_swotr_id>[\d+]{1,})}"

    def actor(self, logdata):

        name = re.match(r"(?P<name>[@|\w+|\s]{1,})", logdata).groupdict()['name']
        actor = get_or_create(models.Actor, name=name.strip())
        if '@' not in actor.name:
            actor.is_npc = True
        return actor

    def ability(self, logdata):
        try:
            match = re.match(self.ability_pattern, logdata)
            group = match.groupdict()
            ability = models.Ability.query.filter_by(swotr_id=group['swotr_id']).first()
            if not ability:
                ability = models.Ability(name=group['name'], swotr_id=group['swotr_id']).save()

            return ability
        except AttributeError, err:
            if re.match(r'\w+', logdata):
                ability = models.Ability.query.filter_by(swotr_id=logdata.lower()).first()
                if not ability:
                    ability = models.Ability(name=logdata, swotr_id=logdata.lower()).save()
                return ability

            raise InvalidDataError(logdata, 'ability not match', self.ability_pattern, err)

    def created_at(self, logdata):
        today = datetime.today()
        log_time = datetime.strptime(logdata, "%H:%M:%S.%f")

        return datetime.combine(today, time(log_time.hour, log_time.minute, log_time.second, log_time.microsecond))

    def run(self, file_name):
        try:
            file = open(os.path.realpath(file_name), 'r')
        except IOError, err:
            print err
            return

        for line in file.readlines():
            try:
                self.parse(line)
            except Exception, err:
                print err

    def effect(self, logdata):
        try:
            match = re.match(self.efect_pattern, logdata)
            group = match.groupdict()

            effect = get_or_create(models.Effect, name=group['name'], swotr_id=group['name_swotr_id'])
            effect_action = get_or_create(models.EffectAction, name=group['action'], swotr_id=group['action_swotr_id'])

            return effect_action, effect
        except AttributeError, err:
            raise InvalidDataError(logdata, 'effect not match', self.efect_pattern, err)

    def event_stat(self, line):

        try:
            stats = re.compile(r'(\(\d+.*\)) (\<\d+.*\>)').findall(line)[0]
            stat = stats[0][1:-1].split(' ')
            stat_value = stat[0]
            threat = stats[1][1:-1]

            try:
                stat_type = get_or_create(models.StatType, name=stat[1], swotr_id=stat[2][1:-1])
            except Exception, err:
                stat_type = None
            is_crit = False
            if '*' in stat_value:
                stat_value = stat_value[:-1]
                is_crit = True
            event_stat = models.EventStat(stat_type=stat_type, stat_value=stat_value, is_crit=is_crit, threat_value=threat)
        except Exception, err:
            event_stat = None

        return event_stat


    def parse(self, line):

#        data = re.findall(r'[\[<\(]([^\[<\(\]>\)]*)[\]>\)]', line)
        data = re.findall(r'[\[<]([^\[<\]>]*)[\]>\)]', line)

        if 'EnterCombat' in self.effect(data[4])[1].name:
            models.Fight.reset()
            models.Fight._combat_fight().start_at = self.created_at(data[0])
            app.logger.info('Enter combat: %s', self.created_at(data[0]))

        if data[3]:
            combat_event = models.CombatEvent(actor=self.actor(data[1]), target=self.actor(data[2]), \
                ability=self.ability(data[3]), created_at=self.created_at(data[0]), \
                effect_action=self.effect(data[4])[0], effect=self.effect(data[4])[1], stat=self.event_stat(line))

            models.Fight._combat_fight().combat_events.append(combat_event)
            combat_event.save()

        if 'ExitCombat' in self.effect(data[4])[1].name:
            models.Fight._combat_fight().finish_at = self.created_at(data[0])
            fight = models.Fight._combat_fight().save()
            app.logger.info('Exit combat: %s', fight.finish_at)
            self.info(fight)

            models.Fight.reset()

    def info(self, fight):
        stat = {}
        fight_time = fight.finish_at - fight.start_at
        elapsed_time = divmod(fight_time.total_seconds(), 60)
        for event in fight.combat_events:
            if event.stat:
                if not event.actor.name in stat:
                    stat[event.actor.name] = {'damage': [0], 'heal': [0]}
                if 'Damage' in event.effect.name:
                    stat[event.actor.name]['damage'].append(event.stat.stat_value)
                if 'Heal' in event.effect.name:
                    stat[event.actor.name]['heal'].append(event.stat.stat_value)
        for actor, item in stat.items():
            app.logger.info(u'Fight\n %s - %s, %s min. %s sec. \n %s did:\n %s damage, %s dps\n %s heal, %s hps', \
                fight.start_at, fight.finish_at, elapsed_time[0], elapsed_time[1], \
                actor, sum(item['damage']), sum(item['damage']) / fight_time.total_seconds(), \
                sum(item['heal']) / fight_time.total_seconds(), sum(item['heal']))
