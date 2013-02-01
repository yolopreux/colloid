import os
import re
import sys
from datetime import datetime, time

from app.models import Actor, Ability, CombatEvent
from app.models import get_or_create
from app.models import Fight
from app.models import Effect, EffectAction


class InvalidDataError(Exception):
    pass


class CombatParser(object):


    ability_pattern = r"(?P<name>[a-zA-Z\s^/{^/}]{0,}) {(?P<swotr_id>[\d+]{1,})}"
    efect_pattern = r"(?P<action>[a-zA-Z'\s^/{^/}]{0,}) {(?P<action_swotr_id>[\d+]{1,})}: (?P<name>[a-zA-Z'\s^/{^/}]{0,}) {(?P<name_swotr_id>[\d+]{1,})}"

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

    def parse(self, line):
        data = re.findall(r'[\[<\(]([^\[<\(\]>\)]*)[\]>\)]', line)

        if 'EnterCombat' in self.effect(data[4])[1].name:
            Fight.reset()
            Fight._combat_fight().start_at = self.created_at(data[0])
            print 'enter combat: %s' % self.created_at(data[0])

        if data[3]:
            combat_event = CombatEvent(actor=self.actor(data[1]), target=self.actor(data[2]), \
                        ability=self.ability(data[3]), created_at=self.created_at(data[0]), \
                        effect_action=self.effect(data[4])[0], effect=self.effect(data[4])[1])

            Fight._combat_fight().combat_events.append(combat_event)
#            combat_event.save()

        if 'ExitCombat' in self.effect(data[4])[1].name:
            Fight._combat_fight().finish_at = self.created_at(data[0])
            Fight._combat_fight().save()
            print 'exit combat: %s' % self.created_at(data[0])
            Fight.reset()
