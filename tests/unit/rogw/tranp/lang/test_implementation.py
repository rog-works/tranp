from unittest import TestCase

from rogw.tranp.lang.annotation import implements, override

class A:
	@property
	def prop_number(self) -> int:
		return 0

	def number_to_str(self, n: int) -> str:
		return str(n)


class TestImplementation(TestCase):
	def test_override(self) -> None:
		class B(A):
			@property
			@override
			def prop_number(self) -> int:
				return 1

			@override
			def number_to_str(self, n: int) -> str:
				return super().number_to_str(n)


		b = B()
		self.assertEqual(1, b.prop_number)
		self.assertEqual('1', b.number_to_str(1))
		self.assertEqual(int, b.number_to_str.__annotations__['n'])
		self.assertEqual(str, b.number_to_str.__annotations__['return'])

	def test_implements(self) -> None:
		class B(A):
			@property
			@implements
			def prop_number(self) -> int:
				return 1

			@implements
			def number_to_str(self, n: int) -> str:
				return super().number_to_str(n)


		b = B()
		self.assertEqual(1, b.prop_number)
		self.assertEqual('1', b.number_to_str(1))
		self.assertEqual(int, b.number_to_str.__annotations__['n'])
		self.assertEqual(str, b.number_to_str.__annotations__['return'])
