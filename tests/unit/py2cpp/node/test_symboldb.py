from unittest import TestCase

from py2cpp.node.symboldb import SymbolDB
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestSymbolDB(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		({
			# implicit module types
			'tests.unit.py2cpp.node.test_symboldb_fixture_classes.int': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.int',
			'tests.unit.py2cpp.node.test_symboldb_fixture_classes.float': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.float',
			'tests.unit.py2cpp.node.test_symboldb_fixture_classes.str': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.str',
			'tests.unit.py2cpp.node.test_symboldb_fixture_classes.bool': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.bool',
			'tests.unit.py2cpp.node.test_symboldb_fixture_classes.tuple': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.tuple',
			'tests.unit.py2cpp.node.test_symboldb_fixture_classes.list': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.list',
			'tests.unit.py2cpp.node.test_symboldb_fixture_classes.dict': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.dict',
			'tests.unit.py2cpp.node.test_symboldb_fixture_classes.None': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.None',
			'tests.unit.py2cpp.node.test_symboldb_fixture_classes.Unknown': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.Unknown',
			# explicit module types
			'tests.unit.py2cpp.node.test_symboldb_fixture2.int': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.int',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.float': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.float',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.str': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.str',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.bool': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.bool',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.tuple': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.tuple',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.list': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.list',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.dict': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.dict',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.None': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.None',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.Unknown': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.Unknown',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.X': 'tests.unit.py2cpp.node.test_symboldb_fixture2.X',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.Y': 'tests.unit.py2cpp.node.test_symboldb_fixture2.Y',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.Z': 'tests.unit.py2cpp.node.test_symboldb_fixture2.Z',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.X.nx': 'tests.unit.py2cpp.node.test_symboldb_fixture2.int',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.Y.ny': 'tests.unit.py2cpp.node.test_symboldb_fixture2.int',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.Y.x': 'tests.unit.py2cpp.node.test_symboldb_fixture2.X',
			'tests.unit.py2cpp.node.test_symboldb_fixture2.Z.nz': 'tests.unit.py2cpp.node.test_symboldb_fixture2.int',
			# implicit import types
			'__main__.int': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.int',
			'__main__.float': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.float',
			'__main__.str': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.str',
			'__main__.bool': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.bool',
			'__main__.tuple': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.tuple',
			'__main__.list': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.list',
			'__main__.dict': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.dict',
			'__main__.None': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.None',
			'__main__.Unknown': 'tests.unit.py2cpp.node.test_symboldb_fixture_classes.Unknown',
			# explicit import types
			'__min__.Z': 'tests.unit.py2cpp.node.test_symboldb_fixture2.Z',
			# entrypoint types
			'__main__.A': '__main__.A',
			'__main__.A.__init__': '__main__.A.__init__',
			'__main__.B': '__main__.B',
			'__main__.B.B2': '__main__.B.B2',
			'__main__.B.__init__': '__main__.B.__init__',
			'__main__.B.func1': '__main__.B.func1',
			# entrypoint symbols
			'__main__.v': '__main__.int',
			'__main__.A.s': '__main__.str',
			'__main__.B.v': '__main__.bool',
			'__main__.B.func1.b': '__main__.list',
			'__main__.B.func1.v': '__main__.bool',
			'__main__.B.B2.v': '__main__.str',
		},),
	])
	def test_make_db(self, expected: dict[str, str]) -> None:
		db = self.fixture.get(SymbolDB)
		print('\n'.join([f"'{key}': '{row.ref_path}'," for key, row in db.items()]))
		for path, row in db.items():
			self.assertEqual('ok' if path in expected else path, 'ok')
			self.assertEqual(f'{row.ref_path}', expected[path])
