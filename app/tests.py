import unittest
import os
import tempfile
import glob
from flask.ext.cache import Cache

from app import app
from app.models import Actor, Effect
from app.recounts import CombatParser
from app.models import CombatEvent
from app.models import Fight
from app.recounts import Recount


class DbTestCase(unittest.TestCase):
    """The base db test case"""

    def setUp(self):
        """Executes before each test"""

        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = '1234'
        app.config['CACHE_TYPE'] = 'simple'
        self.client = app.test_client()
        self.cache = Cache(app)
        self.app = app

    def tearDown(self):
        """Executes after each tests"""

        os.close(self.db_fd)
        os.unlink(self.app.config['DATABASE'])


class ModelTestCase(DbTestCase):
    pass


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
        '[23:03:43.942] [@Jalo] [@Jalo] [Duplicity {949110463004672}] [RemoveEffect {836045448945478}: Exploit Weakness {949110463004928}] ()',
        '[19:58:56.071] [@Jalo] [@Jalo] [Sprint {810670782152704}] [ApplyEffect {836045448945477}: Sprint {810670782152704}] ()',
        '[20:02:45.589] [@Jalo] [@Jalo] [] [Event {836045448945472}: EnterCombat {836045448945489}] ()',
        '[20:02:45.622] [@Jalo] [@Jalo] [Force Lightning {808252715565056}] [Event {836045448945472}: AbilityActivate {836045448945479}] ()',
        '[20:02:45.622] [@Jalo] [@Jalo] [] [Spend {836045448945473}: Force {836045448938502}] (30)',
        '[20:02:45.622] [@Jalo] [@Jalo] [Sprint {810670782152704}] [RemoveEffect {836045448945478}: Sprint {810670782152704}] ()',
        '[20:02:45.623] [@Jalo] [@Jalo] [Duplicity {949110463004672}] [ApplyEffect {836045448945477}: Exploit Weakness {949110463004928}] ()',
        '[20:02:45.625] [@Jalo] [Operations Training Target MK-5 {2816265890562048}:1179000006870] [Lightning Charge {808205470924800}] [ApplyEffect {836045448945477}: Damage {836045448945501}] (106 energy {836045448940874}) <106>',
        '[20:02:45.625] [@Jalo] [Operations Training Target MK-5 {2816265890562048}:1179000006870] [Shocked {808252715565342}] [ApplyEffect {836045448945477}: Damage {836045448945501}] (406 energy {836045448940874}) <406>',
        '[20:02:46.622] [@Jalo] [Operations Training Target MK-5 {2816265890562048}:1179000006870] [Shocked {808252715565342}] [ApplyEffect {836045448945477}: Damage {836045448945501}] (406 energy {836045448940874}) <406>',
        '[20:02:47.630] [@Jalo] [Operations Training Target MK-5 {2816265890562048}:1179000006870] [Shocked {808252715565342}] [ApplyEffect {836045448945477}: Damage {836045448945501}] (406 energy {836045448940874}) <406>',
        '[20:02:48.685] [@Jalo] [Operations Training Target MK-5 {2816265890562048}:1179000006870] [Lightning Charge {808205470924800}] [ApplyEffect {836045448945477}: Damage {836045448945501}] (106 energy {836045448940874}) <106>',
        '[20:02:48.686] [@Jalo] [Operations Training Target MK-5 {2816265890562048}:1179000006870] [Shocked {808252715565342}] [ApplyEffect {836045448945477}: Damage {836045448945501}] (406 energy {836045448940874}) <406>',
        '[20:02:49.167] [@Jalo] [@Jalo] [Death Field {808433104191488}] [Event {836045448945472}: AbilityActivate {836045448945479}] ()',
        '[20:02:49.167] [@Jalo] [@Jalo] [] [Spend {836045448945473}: Force {836045448938502}] (25)',
        '[20:02:49.165] [@Jalo] [@Jalo] [] [Event {836045448945472}: ExitCombat {836045448945490}] ()'
        '[20:02:49.169] [@Jalo] [@Jalo] [Death Field {808433104191488}] [ApplyEffect {836045448945477}: Heal {836045448945500}] (354)',
        '[20:02:49.170] [@Jalo] [@Jalo] [Exploitive Strikes {808441694126080}] [ApplyEffect {836045448945477}: Exploitive Strikes {808441694126080}] ()',
        '[20:02:49.170] [@Jalo] [@Jalo] [] [Event {836045448945472}: EnterCombat {836045448945489}] ()',
        '[20:02:49.170] [@Jalo] [Operations Training Target MK-5 {2816265890562048}:1179000006870] [Deathmark {808428809224192}] [ApplyEffect {836045448945477}: Deathmark {808428809224449}] ()',
        '[20:02:49.171] [@Jalo] [Operations Training Target MK-5 {2816265890562048}:1179000006870] [Death Field {808433104191488}] [ApplyEffect {836045448945477}: Damage {836045448945501}] (2839* internal {836045448940876}) <2839>',
        '[20:02:54.766] [@Jalo] [@Jalo] [] [Event {836045448945472}: ExitCombat {836045448945490}] ()',
        '[20:04:19.552] [@Jalo] [Operations Training Target MK-5 {2816265890562048}:1179000006870] [Discharge {808235535695872}] [RemoveEffect {836045448945478}: Shocked (Force) {808235535696133}] ()', ]

    def parse_log_test(self):
        for combat in self.combat_log:
            CombatParser().parse(combat)
        self.assertIsNotNone(Actor.query.filter_by(name='@Jalo').first())
        self.assertIsNotNone(Actor.query.filter_by(name='@Yarpean').first())
        self.assertIsNotNone(Actor.query.filter_by(name='@Morgaina').first())
        target = Actor.query.filter_by(name='Retching Larva').first()
        self.assertIsNotNone(target, 'Target')
        self.assertTrue(target.is_npc, 'Target is npc')

        self.assertEqual(2, len(Fight.query.all()))
        fights = Fight.query.all()
        self.assertEqual(10, len(fights[0].combat_events))
        self.assertEqual(fights[0].start_at.second, 45)
        self.assertEqual(fights[0].finish_at.second, 49)
        self.assertEqual(2, len(fights[1].combat_events))
        self.assertEqual(fights[1].start_at.second, 49)
        self.assertEqual(fights[1].finish_at.second, 54)

    def parse_file_test(self):
        """
        Load and parse logs inside app/combat directory
        """
        instance_id = id(Recount())
        path = os.path.realpath('app/combat')
        files = glob.glob(path + '/combat_*.txt')
        if not len(files):
            self.fail('Pending')
        for file_path in files:
            for line in open(file_path).readlines():
                CombatParser().parse(line)

        self.assertEqual(Recount(), instance_id)
