import re
from unittest import TestCase

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.semantics.errors import UnresolvedSymbolError
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


class TestReflectionsError(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__)

	@data_provider([
		(ModuleDSN.full_joined(fixture_module_path, 'InvalidOps.tenary_to_union_types.n_or_s'), UnresolvedSymbolError, r'Only Nullable.'),
		(ModuleDSN.full_joined(fixture_module_path, 'InvalidOps.tuple_expand.a'), IndexError, r'list index out of range'),
	])
	def test_from_fullyname_error(self, fullyname: str, expected_error: type[Exception], expected: re.Pattern[str]) -> None:
		reflections = self.fixture.get(Reflections)
		with self.assertRaisesRegex(expected_error, expected):
			str(reflections.from_fullyname(fullyname))
