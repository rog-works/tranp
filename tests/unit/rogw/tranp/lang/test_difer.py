from unittest import TestCase

from rogw.tranp.lang.defer import Difer


class TestDifer(TestCase):
	def test_usage(self) -> None:
		class A:
			def func(self) -> int:
				return 1

		actual = Difer.new(lambda: A())
		self.assertEqual(actual.func(), 1)
