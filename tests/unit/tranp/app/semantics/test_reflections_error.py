import re
from unittest import TestCase

from tests.test.fixture import Fixture
from tranp.app.dsn.module import ModuleDSN
from tranp.app.errors import Errors
from tranp.app.semantics.reflections import Reflections
from tranp.app.test.helper import data_provider


class TestReflectionsError(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__)

	@data_provider([
		(ModuleDSN.full_joined(fixture_module_path, 'InvalidOps.tuple_expand.a'), Errors.Fatal, 'Unhandled error'),
	])
	def test_from_fullyname(self, fullyname: str, expected_error: type[Exception], expected: re.Pattern[str]) -> None:
		with self.assertRaisesRegex(expected_error, expected):
			self.fixture.shared_module
			reflections = self.fixture.get(Reflections)
			str(reflections.from_fullyname(fullyname))
