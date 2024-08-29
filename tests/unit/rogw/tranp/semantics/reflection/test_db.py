from unittest import TestCase

from rogw.tranp.semantics.reflection.db import SymbolDB
from rogw.tranp.semantics.reflection.serialization import IReflectionSerializer
from tests.test.fixture import Fixture
from tests.unit.rogw.tranp.semantics.reflection.fixtures.test_db_expect import expected_symbols


class TestDB(TestCase):
	fixture = Fixture.make(__file__)

	def setUp(self) -> None:
		super().setUp()
		# XXX モジュールをロードすることでDBが完成するため、必ず事前に実施
		self.fixture.shared_module

	def test_make_db(self) -> None:
		db = self.fixture.get(SymbolDB)

		try:
			expected = expected_symbols()
			for expected_path, expected_org_path in expected.items():
				self.assertEqual('ok' if expected_path in db else expected_path, 'ok')
				self.assertEqual(db[expected_path].types.fullyname, expected_org_path)

			for key, _ in db.items():
				self.assertEqual('ok' if key in expected else key, 'ok')

			self.assertEqual(len(expected), len(db))
		except AssertionError:
			print('\n', '\n'.join([f"'{key}': '{raw.types.fullyname}'," for key, raw in db.items()]))
			raise

	def test_serialize(self) -> None:
		db = self.fixture.get(SymbolDB)
		data = db.to_json(self.fixture.get(IReflectionSerializer))

		keys = data.keys()
		self.assertEqual(len(db), len(keys))
		for key in db.keys():
			self.assertEqual('ok' if key in keys else key, 'ok')

	def test_deserialize(self) -> None:
		db = self.fixture.get(SymbolDB)
		data = db.to_json(self.fixture.get(IReflectionSerializer))
		new_db = SymbolDB()
		new_db.load_json(self.fixture.get(IReflectionSerializer), data)

		self.assertEqual(len(db), len(new_db))
		for key in db.keys():
			try:
				self.assertEqual('ok' if db[key] == new_db[key] else key, 'ok')
				self.assertEqual(new_db[key].node, db[key].node)
				self.assertEqual(new_db[key].decl, db[key].decl)
				self.assertEqual(new_db[key].via, db[key].via)
			except AssertionError:
				print(f'org: {str(db[key])}, new: {str(new_db[key])}, data: {data[key]}')
				raise
