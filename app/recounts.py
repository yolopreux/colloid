"""
    colloid project
    ~~~~~~~~~~~~~~

    Combat log analizer.

    :copyright: (c) 2013 by Darek <netmik12 [AT] gmail [DOT] com>
    :license: BSD, see LICENSE for more details
"""
import os
import re
import weakref
from datetime import datetime, time
import math
import glob
from sqlalchemy.orm.exc import DetachedInstanceError

from app import models
from app import app


def slugify(string):
    return re.sub(r'\W+', '_', string.lower())


def model_id(model, **kwargs):
    model_id = slugify(str(model))
    for key, value in kwargs.iteritems():
        model_id += slugify(key) + '__' + slugify(value)
    return model_id


class Recount(object):

    _instance = None
    _data = weakref.WeakValueDictionary()

    data = {}
    heal_done = {}
    damage_done = {}

    counter_start = None
    counter_end = None

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

    def add_heal(self, source, value):
        if source not in self.heal_done:
            self.heal_done[source] = []
        self.heal_done[source].append(value)

    def add_damage(self, source, value):
        if source not in self.damage_done:
            self.damage_done[source] = []
        self.damage_done[source].append(value)

    def get_heal_done(self):
        duration = self.counter_end - self.counter_start
        if not duration.seconds:
            return

        for source, heal in self.heal_done.iteritems():
            heal_done = sum(heal)
            hps = heal_done / duration.total_seconds()
            yield source, heal_done, hps

    def get_damage_done(self):
        duration = None
        try:
            duration = self.counter_end - self.counter_start
        except TypeError, err:
            print err
        if not duration or not duration.seconds:
            return
        for source, damage in self.damage_done.items():
            yield 'Damage done %s:%s %s (DPS: %s)' % (source, math.fsum(damage),
               str(duration), math.fsum(damage) / duration.seconds)

    def get_counter_time(self):
        if (self.counter_start and self.counter_end):
            return "Counter combat: %s - %s" % (datetime.strftime(
              self.counter_start, '%H:%M:%S.%f'),
            datetime.strftime(self.counter_end, '%H:%M:%S.%f'))
        return 'Invalid counter time'

    def reset(self):
        self.damage_done = {}
        self.heal_done = {}
        self.counter_start = None
        self.counter_end = None

    def stats(self):

        return self.get_damage_done(), self.get_heal_done()

    @classmethod
    def refresh(cls):
        cls._instance = None
        cls._data = weakref.WeakValueDictionary()


def get_or_create(model, **kwargs):

    instance = Recount().get(model_id(model, **kwargs))
    if instance:
        return instance

    instance = models.get_or_create(model, **kwargs)
    Recount().set(model_id(model, **kwargs), instance)

    return instance


class InvalidDataError(Exception):
    pass


class ParseLogError(InvalidDataError):
    pass


class CombatParser(object):

    date = None
    UNDEFINED = 'undefinded'

    ability_pattern = r"(?P<name>[a-zA-Z\s^/{^/}]{0,}) {(?P<swotr_id>[\d+]{1,})}"
    efect_pattern = r"(?P<action>[a-zA-Z'\s^/{^/}]{0,}) {(?P<action_swotr_id>[\d+]{1,})}: (?P<name>[a-zA-Z'\s^/{^/}/(/)]{0,}) {(?P<name_swotr_id>[\d+]{1,})}"
    actor_pattern = r'(?P<name>[@|\w+|\s|/:]{1,})'

    def actor(self, logdata=None):
        """Match actor in logdata"""
        if not logdata:
            name = self.UNDEFINED
        else:
            match = re.match(self.actor_pattern, logdata)
            if not match:
                raise InvalidDataError(logdata, 'invalid actor or target', self.actor_pattern)
            name = match.groupdict()['name']

        actor = get_or_create(models.Actor, name=name.strip())
        if '@' not in actor.name:
            actor.is_npc = True

        return actor

    def ability(self, logdata=None):
        """Match ability in logdata"""
        try:
            match = re.match(self.ability_pattern, logdata)
            group = match.groupdict()
            ability = get_or_create(models.Ability, name=group['name'], swotr_id=group['swotr_id'])

            return ability
        except AttributeError:
            app.logger.debug('ability not match logdata[%s]: pattern[%s]', logdata, self.ability_pattern)
        ability = get_or_create(models.Ability, name='undefined')
        return ability

    def created_at(self, logdata):
        created_date = datetime.today()
        if self.date:
            created_date = self.date
        today = datetime.today()
        log_time = datetime.strptime(logdata, "%H:%M:%S.%f")

        return datetime.combine(created_date, time(log_time.hour, log_time.minute,
                                            log_time.second,
                                            log_time.microsecond))

    def run(self, file_name=None, directory=None):
        """
        Open log file
        Start parse combat log
        :param file_name: - combat log filename
        :param directory: combat log directory path
        """
        if not file_name and not directory:
            directory = 'app/combat'
        try:
            if file_name:
                self.date = self.created_date(filename=file_name)
                file_log = open(os.path.realpath(file_name), 'r')
                for line in file_log.readlines():
                    try:
                        self.parse(line)
                    except Exception, err:
                        app.logger.warn(err)
                return

            path = os.path.realpath(directory)
            files = glob.glob(path + '/combat_*.txt')
            if not len(files):
                app.logger.warn("No combats were found in path %s", path)
            for file_path in files:
                self.date = self.created_date(filename=file_path)
                for line in open(file_path).readlines():
                    try:
                        self.parse(line)
                    except Exception, err:
                        app.logger.warn(err)

        except IOError, err:
            print err
            return

    def created_date(self, filename):
        time = os.path.getctime(filename)
        return datetime.fromtimestamp(time)

    def effect(self, logdata):
        try:
            match = re.match(self.efect_pattern, logdata)
            group = match.groupdict()
            effect = get_or_create(models.Effect, name=group['name'],
                                   swotr_id=group['name_swotr_id'])
            effect_action = get_or_create(models.EffectAction,
                                          name=group['action'],
                                          swotr_id=group['action_swotr_id'])

            return effect_action, effect
        except AttributeError, err:
            raise InvalidDataError(logdata, 'effect not match',
                                   self.efect_pattern, err)

    def event_stat(self, line):

        try:
            compiled = re.compile(r'(\(\d+.*\)) (\<\d+.*\>)').findall(line)
            try:
                stats = compiled[0]
            except IndexError:
                stats = re.compile(r'(\(\d+.*\))').findall(line)

            stat = stats[0][1:-1].split(' ')
            stat_value = stat[0]
            try:
                threat = stats[1][1:-1]
            except IndexError:
                threat = None

            try:
                stat_type = get_or_create(models.StatType, name=stat[1],
                                          swotr_id=stat[2][1:-1])
            except IndexError:
                stat_type = None
            is_crit = False
            if '*' in stat_value:
                stat_value = stat_value[:-1]
                is_crit = True
            event_stat = models.EventStat(stat_type=stat_type,
                                          stat_value=stat_value,
                                          is_crit=is_crit, threat_value=threat)
        except Exception, err:
            event_stat = None

        return event_stat

    def parse(self, line):
        try:
            self.recount(line)
        except InvalidDataError, err:
            raise ParseLogError(err, line)
        except DetachedInstanceError, err:
            app.logger.warn(err)
            Recount.refresh()

    def recount(self, line):
#        data = re.findall(r'[\[<\(]([^\[<\(\]>\)]*)[\]>\)]', line)
        data = re.findall(r'[\[<]([^\[<\]>]*)[\]>\)]', line)
        event = None
        try:
            actor = self.actor(data[1])
        except IndexError:
            actor = self.actor()
        try:
            target = self.actor(data[2])
        except IndexError:
            target = actor
        try:
            event = models.CombatEvent(actor=actor, target=target,
                                       ability=self.ability(data[3]),
                                       created_at=self.created_at(data[0]),
                                       effect_action=self.effect(data[4])[0],
                                       effect=self.effect(data[4])[1],
                                       stat=self.event_stat(line))

            models.Fight._combat_fight().combat_events.append(event)
        except IndexError:
            pass
        try:
            effect_name = self.effect(data[4])[1].name
        except IndexError:
            effect_name = 'undefined'

        if 'EnterCombat' in effect_name:
            models.Fight.reset()
            models.Fight._combat_fight().start_at = self.created_at(data[0])
            app.logger.info('Enter combat: %s', self.created_at(data[0]))
            Recount().reset()
            Recount().counter_start = models.Fight._combat_fight().start_at
            models.Fight._combat_fight().combat_events.append(event)

        if event and event.stat:
            if event.is_damage():
                Recount().add_damage(event.actor.name, event.stat.stat_value)
                app.logger.debug('Damage: %s:%s %s', event.actor.name, event.ability.name, event.stat.stat_value)
            if event.is_heal():
                Recount().add_heal(event.actor.name, event.stat.stat_value)
                app.logger.debug('Heal: %s:%s %s', event.actor.name, event.ability.name, event.stat.stat_value)

        if 'ExitCombat' in effect_name:
            models.Fight._combat_fight().finish_at = self.created_at(data[0])
            fight = models.Fight._combat_fight().save()
            app.logger.info('Exit combat: %s', fight.finish_at)
            self.info(fight)
            Recount().get_heal_done()
            Recount().reset()
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
                            fight.start_at, fight.finish_at, elapsed_time[0],
                            elapsed_time[1], actor, sum(item['damage']),
                            sum(item['damage']) / fight_time.total_seconds(),
                            sum(item['heal']), sum(item['heal']) / fight_time.total_seconds())
