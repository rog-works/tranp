from unittest import TestCase

from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestPy2Cpp(TestCase):
	fixture = Fixture.make(__file__)

	def test_exec(self) -> None:
		...