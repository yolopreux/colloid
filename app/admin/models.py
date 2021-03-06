"""
    colloid project
    ~~~~~~~~~~~~~~

    Combat log analizer.

    :copyright: (c) 2013 by Darek <netmik12 [AT] gmail [DOT] com>
    :license: BSD, see LICENSE for more details
"""
from flask_admin.contrib.sqlamodel import ModelView
from flask_login import current_user


class DbSessionError(Exception):

    """Invalid db session"""
    pass


class AppModelView(ModelView):

    def __init__(self, model, session=None,
        name=None, category=None, endpoint=None, url=None):
        from app import BaseModel
        if issubclass(model, BaseModel):
            session = model.db.session
        if not session:
            raise DbSessionError

        super(AppModelView, self).__init__(model=model, session=session,
                                           name=name, category=category,
                                           endpoint=endpoint, url=url)

    def is_accessible(self):
        return True
#        return current_user.is_authenticated() and current_user.is_superuser


class ActorModelView(AppModelView):
    """Actor admin model view"""
    # Disable model creation
    can_create = False

    column_list = ('name', 'is_npc',)
    column_searchable_list = ('name',)
    column_sortable_list = ('name', 'is_npc',)
    column_filters = ('name', 'is_npc',)

    def __init__(self, **kwargs):
        from app.models import Actor
        super(ActorModelView, self).__init__(Actor, **kwargs)


class AbilityModelView(AppModelView):
    """Actor admin model view"""
    # Disable model creation
    can_create = False

    column_list = ('swotr_id', 'name',)
    column_searchable_list = ('swotr_id', 'name',)
    column_sortable_list = ('swotr_id', 'name',)
    column_filters = ('swotr_id', 'name',)

    def __init__(self, **kwargs):
        from app.models import Ability
        super(AbilityModelView, self).__init__(Ability, **kwargs)


class CombatEventModelView(AppModelView):
    """Actor admin model view"""
    # Disable model creation
    can_create = False
    column_filters = ('created_at', 'effect', 'ability', 'effect_action', 'actor')

    can_edit = False

    def __init__(self, **kwargs):
        from app.models import CombatEvent, Ability
        self.column_searchable_list = (Ability.name,)
        super(CombatEventModelView, self).__init__(CombatEvent, **kwargs)


class FightModelView(AppModelView):
    """Actor admin model view"""
    # Disable model creation
    can_create = False
    can_edit = False
    column_filters = ('start_at', 'finish_at')
    column_list = ('start_at', 'finish_at',)

    def __init__(self, **kwargs):
        from app.models import Fight
        super(FightModelView, self).__init__(Fight, **kwargs)


