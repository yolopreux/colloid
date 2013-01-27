import os
import re
import sys

from app.models import Actor, Ability

class CombatParser(object):

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
        actor = Actor.query.filter_by(name=data[1]).first()
        if not actor:
            actor = Actor(name=data[1])

        match = re.match(r"(?P<name>[a-zA-Z\s^/{^/}]{1,}) {(?P<swotr_id>[\d+]{1,})}", data[3])
        if match:
            group = match.groupdict()
            ability = Ability.query.filter_by(swotr_id=group['swotr_id']).first()
            if not ability:
                ability = Ability(name=group['name'], swotr_id=group['swotr_id'])
