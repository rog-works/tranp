from unittest import TestCase

from tranp.analyze.db import SymbolDB
from tests.test.fixture import Fixture
from tests.unit.tranp.analyze.fixtures.test_db_expect import expected_symbols


class TestSymbolDB(TestCase):
	fixture = Fixture.make(__file__)

	def test___init__(self) -> None:
		db = self.fixture.get(SymbolDB)

		try:
			expected = expected_symbols()
			for expected_path, expected_org_path in expected.items():
				self.assertEqual('ok' if expected_path in db.raws else expected_path, 'ok')
				self.assertEqual(db.raws[expected_path].org_path, expected_org_path)

			for key, _ in db.raws.items():
				self.assertEqual('ok' if key in expected else key, 'ok')

			self.assertEqual(len(db.raws), len(expected))
		except AssertionError as e:
			print('\n', '\n'.join([f"'{key}': '{raw.org_path}'," for key, raw in db.raws.items()]))
			raise
