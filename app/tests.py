import unittest
import os
import tempfile

from app import app
from app.models import Actor
from app.recounts import CombatParser
from app.models import CombatEvent, Fight



class DbTestCase(unittest.TestCase):
    """The base db test case"""

    def setUp(self):
        """Executes before each test"""

        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = '1234'
        self.client = app.test_client()
        self.app = app

    def tearDown(self):
        """Executes after each tests"""

        os.close(self.db_fd)
        os.unlink(self.app.config['DATABASE'])


class ModelTestCase(DbTestCase):

    def parse_actor_test(self):
        actor = Actor(data='@yolo').save()
        self.assertEqual(actor.name, u'@yolo')
        self.assertFalse(actor.is_npc)

        actor = Actor(data='Thrashing Larva {2960649806151680}:1566004468297').save()
        self.assertEqual(actor.name, u'Thrashing Larva')
        self.assertTrue(actor.is_npc)


class RecountTestCase(DbTestCase):
    combat_log = ['[23:03:13.572] [@Jalo] [Retching Larva {2960654101118976}:1566004468119] [Death Field {808433104191488}] [ApplyEffect {836045448945477}: Damage {836045448945501}] (3104* internal {836045448940876}) <3104>',
                  '[23:03:13.974] [@Yarpean] [@Jalo] [Revivification {808703687131136}] [ApplyEffect {836045448945477}: Heal {836045448945500}] (493)',
                  '[23:03:14.159] [@Jalo] [Thrashing Larva {2960649806151680}:1566004468038] [Deathmark {808428809224192}] [RemoveEffect {836045448945478}: Deathmark {808428809224449}] ()',
                  '[23:03:14.159] [@Jalo] [Thrashing Larva {2960649806151680}:1566004468297] [Deathmark {808428809224192}] [RemoveEffect {836045448945478}: Deathmark {808428809224449}] ()',
                  '[23:03:15.382] [@Jalo] [@Jalo] [Duplicity {949110463004672}] [RemoveEffect {836045448945478}: Exploit Weakness {949110463004928}] ()',
                  '[23:03:15.386] [@Jalo] [@Jalo] [Discharge {808235535695872}] [Event {836045448945472}: AbilityActivate {836045448945479}] ()',
                  '[23:03:15.386] [@Jalo] [@Jalo] [] [Spend {836045448945473}: Force {836045448938502}] (20)',
                  '[23:03:41.737] [@Jalo] [Thrashing Larva {2960649806151680}:1566004468297] [ {3009045497643008}] [Event {836045448945472}: ModifyThreat {836045448945483}] () <50000>',
                  '[23:03:41.949] [@Morgaina] [@Jalo] [Predation {2516812180750336}] [ApplyEffect {836045448945477}: Predation {2516812180750336}] ()',
                  '[23:03:42.717] [@Yarpean] [@Jalo] [Revivification {808703687131136}] [ApplyEffect {836045448945477}: Heal {836045448945500}] (493)',
                  '[23:03:42.792] [@Jalo] [@Jalo] [Crushing Darkness {863460225187840}] [Event {836045448945472}: AbilityActivate {836045448945479}] ()',
                  '[23:03:43.712] [@Yarpean] [@Jalo] [Revivification {808703687131136}] [ApplyEffect {836045448945477}: Heal {836045448945500}] (859*)',
                  '[23:03:43.942] [@Jalo] [@Jalo] [Duplicity {949110463004672}] [RemoveEffect {836045448945478}: Exploit Weakness {949110463004928}] ()', ]

    def parse_log_test(self):
        for combat in self.combat_log:
            CombatParser().parse(combat)
        self.assertIsNotNone(Actor.query.filter_by(name='@Jalo').first())
        self.assertIsNotNone(Actor.query.filter_by(name='@Yarpean').first())
        self.assertIsNotNone(Actor.query.filter_by(name='@Morgaina').first())
        target = Actor.query.filter_by(name='Retching Larva').first()
        self.assertIsNotNone(target, 'Target')
        self.assertTrue(target.is_npc, 'Target is npc')

