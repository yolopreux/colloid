"""
    colloid project
    ~~~~~~~~~~~~~~

    Combat log analizer.

    :copyright: (c) 2013 by Darek <netmik12 [AT] gmail [DOT] com>
    :license: BSD, see LICENSE for more details
"""
from .base import AppAdmin


def init_admin(app):
    AppAdmin(app)
