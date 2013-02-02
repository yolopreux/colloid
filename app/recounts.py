import os
import re
import sys
import weakref
from datetime import datetime, time
import logging

from app.models import Actor, Ability, CombatEvent, StatType
from app.models import get_or_create
from app.models import Fight
from app.models import Effect, EffectAction, StatType, EventStat
from app import logger


def slugify(str):
    str = str.lower()
    return re.sub(r'\W+', '_', str)


class Recount(object):

    _instance = None
    _data = weakref.WeakValueDictionary()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Recount, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def set(self, key, data):
        iod = id(key)
        self._data[iod] = data
        logger.debug('set key, iod: %s, %s', key, iod)

    def get(self, key):
        iod = id(key)
        try:
            data = self._data[iod]
            logger.debug('get key, iod: %s, %s, object: %s', key, iod, data)
            return data
        except:
            return None


class InvalidDataError(Exception):
    pass


class CombatParser(object):


    ability_pattern = r"(?P<name>[a-zA-Z\s^/{^/}]{0,}) {(?P<swotr_id>[\d+]{1,})}"
    efect_pattern = r"(?P<action>[a-zA-Z'\s^/{^/}]{0,}) {(?P<action_swotr_id>[\d+]{1,})}: (?P<name>[a-zA-Z'\s^/{^/}/(/)]{0,}) {(?P<name_swotr_id>[\d+]{1,})}"

    def actor(self, logdata):

        name = re.match(r"(?P<name>[@|\w+|\s]{1,})", logdata).groupdict()['name']
        actor = get_or_create(Actor, name=name.strip())
        if '@' not in actor.name:
            actor.is_npc = True
        return actor

    def ability(self, logdata):
        try:
            match = re.match(self.ability_pattern, logdata)
            group = match.groupdict()
            ability = Ability.query.filter_by(swotr_id=group['swotr_id']).first()
            if not ability:
                ability = Ability(name=group['name'], swotr_id=group['swotr_id']).save()

            return ability
        except AttributeError, err:
            if re.match(r'\w+', logdata):
                ability = Ability.query.filter_by(swotr_id=logdata.lower()).first()
                if not ability:
                    ability = Ability(name=logdata, swotr_id=logdata.lower()).save()
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

            effect = get_or_create(Effect, name=group['name'], swotr_id=group['name_swotr_id'])
            effect_action = get_or_create(EffectAction, name=group['action'], swotr_id=group['action_swotr_id'])

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
                stat_type = get_or_create(StatType, name=stat[1], swotr_id=stat[2][1:-1])
            except Exception, err:
                stat_type = None
            is_crit = False
            if '*' in stat_value:
                stat_value = stat_value[:-1]
                is_crit = True
            event_stat = EventStat(stat_type=stat_type, stat_value=stat_value, is_crit=is_crit, threat_value=threat)
        except Exception, err:
            event_stat = None

        return event_stat


    def parse(self, line):

#        data = re.findall(r'[\[<\(]([^\[<\(\]>\)]*)[\]>\)]', line)
        data = re.findall(r'[\[<]([^\[<\]>]*)[\]>\)]', line)

        if 'EnterCombat' in self.effect(data[4])[1].name:
            Fight.reset()
            Fight._combat_fight().start_at = self.created_at(data[0])
            print 'enter combat: %s' % self.created_at(data[0])

        if data[3]:
            combat_event = CombatEvent(actor=self.actor(data[1]), target=self.actor(data[2]), \
                ability=self.ability(data[3]), created_at=self.created_at(data[0]), \
                effect_action=self.effect(data[4])[0], effect=self.effect(data[4])[1], stat=self.event_stat(line))

            Fight._combat_fight().combat_events.append(combat_event)
            combat_event.save()

        if 'ExitCombat' in self.effect(data[4])[1].name:
            Fight._combat_fight().finish_at = self.created_at(data[0])
            Fight._combat_fight().save()
            print 'exit combat: %s' % self.created_at(data[0])
            Fight.reset()
