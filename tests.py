#!/usr/bin/env python
import os
import sys

import nose
from configs import TESTING
from app import db


def runtests(*test_args):
    TESTING = True
    db.create_all()

    nose.main()


if __name__ == '__main__':
    runtests(*sys.argv[1:])
