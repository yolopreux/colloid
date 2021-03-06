"""
    colloid project
    ~~~~~~~~~~~~~~

    Combat log analizer.

    :copyright: (c) 2013 by Darek <netmik12 [AT] gmail [DOT] com>
    :license: BSD, see LICENSE for more details
"""
from flask_admin import Admin

from app.admin import views
from app.admin import models


class AppAdmin(Admin):

    def __init__(self, app=None, name=None, url=None, index_view=None,
        translations_path=None):

        super(AppAdmin, self).__init__(app, name, url, index_view,
            translations_path)
        self.init_views()

    def init_views(self):
        self.add_view(models.ActorModelView(category="Combat"))
        self.add_view(models.AbilityModelView(category="Combat"))
        self.add_view(models.CombatEventModelView(category="Combat"))
        self.add_view(models.FightModelView(category="Combat"))
