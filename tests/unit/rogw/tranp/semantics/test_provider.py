from unittest import TestCase

from rogw.tranp.semantics.provider import SymbolDBProvider
from tests.test.fixture import Fixture
from tests.unit.rogw.tranp.semantics.fixtures.test_provider_expect import expected_symbols


class TestProvider(TestCase):
	fixture = Fixture.make(__file__)

	def test_make_db(self) -> None:
		db = self.fixture.get(SymbolDBProvider)

		try:
			expected = expected_symbols()
			for expected_path, expected_org_path in expected.items():
				self.assertEqual('ok' if expected_path in db.raws else expected_path, 'ok')
				self.assertEqual(db.raws[expected_path].org_fullyname, expected_org_path)

			for key, _ in db.raws.items():
				self.assertEqual('ok' if key in expected else key, 'ok')

			self.assertEqual(len(db.raws), len(expected))
		except AssertionError as e:
			print('\n', '\n'.join([f"'{key}': '{raw.org_fullyname}'," for key, raw in db.raws.items()]))
			raise
