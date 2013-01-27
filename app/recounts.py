import os
import re
import sys
from datetime import datetime, time

from app.models import Actor, Ability, CombatEvent

class InvalidDataError(Exception):
    pass


class CombatParser(object):


    ability_pattern = r"(?P<name>[a-zA-Z\s^/{^/}]{1,}) {(?P<swotr_id>[\d+]{1,})}"

    def actor(self, logdata):

        name = re.match(r"(?P<name>[@|\w+|\s]{1,})", logdata).groupdict()['name']
        actor = Actor.query.filter_by(name=name).first()
        if not actor:
            actor = Actor(data=name).save()

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
            self.parse(line)

    def parse(self, line):
        data = re.findall(r'[\[<\(]([^\[<\(\]>\)]*)[\]>\)]', line)
        if data[3]:
            CombatEvent(actor=self.actor(data[1]), target=self.actor(data[2]), \
                        ability=self.ability(data[3]), created_at=self.created_at(data[0])).save()


