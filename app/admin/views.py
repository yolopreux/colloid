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
