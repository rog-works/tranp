from unittest import TestCase

from rogw.tranp.semantics.reflection.db import SymbolDBFinalizer
from tests.test.fixture import Fixture
from tests.unit.rogw.tranp.semantics.reflection.fixtures.test_symbol_db_expect import expected_symbols


class TestSymbolDB(TestCase):
	fixture = Fixture.make(__file__)

	def test_make_db(self) -> None:
		db = self.fixture.get(SymbolDBFinalizer)()

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
