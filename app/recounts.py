import os
import re
import sys

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
        pass
