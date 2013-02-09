"""
    colloid project
    ~~~~~~~~~~~~~~

    Combat log analizer.

    :copyright: (c) 2013 by Darek <netmik12 [AT] gmail [DOT] com>
    :license: BSD, see LICENSE for more details
"""
from flask_admin.base import BaseView
from flask_admin.base import expose
from flask_login import current_user


class AdminView(BaseView):

    def is_accessible(self):
        return True
#        return current_user.is_authenticated()

    @expose('/')
    def index(self):
        return self.render('admin/index.html')
