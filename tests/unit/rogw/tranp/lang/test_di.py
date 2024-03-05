from unittest import TestCase

from rogw.tranp.lang.di import DI

class A: pass
class B(A): pass
class X: pass
class Y:
	def __init__(self, x: X) -> None:
		self.x = x


def factory_x() -> X:
	return X()


class TestDI(TestCase):
	def test_can_resolve(self) -> None:
		di = DI()
		di.bind(A, B)
		di.bind(X, X)
		self.assertEqual(di.can_resolve(A), True)
		self.assertEqual(di.can_resolve(B), False)
		self.assertEqual(di.can_resolve(X), True)
		self.assertEqual(di.can_resolve(Y), False)

	def test_bind(self) -> None:
		di = DI()
		di.bind(B, B)
		di.bind(X, factory_x)
		di.bind(Y, Y)
		self.assertEqual(di.can_resolve(A), False)
		self.assertEqual(di.can_resolve(B), True)
		self.assertEqual(di.can_resolve(X), True)
		self.assertEqual(di.can_resolve(Y), True)

	def test_unbind(self) -> None:
		di = DI()
		di.bind(A, A)
		di.bind(B, B)
		di.bind(X, X)
		di.bind(Y, Y)
		di.unbind(X)
		di.unbind(Y)
		self.assertEqual(di.can_resolve(A), True)
		self.assertEqual(di.can_resolve(B), True)
		self.assertEqual(di.can_resolve(X), False)
		self.assertEqual(di.can_resolve(Y), False)

	def test_rebind(self) -> None:
		di = DI()
		di.bind(A, A)
		di.rebind(A, B)
		self.assertEqual(di.can_resolve(A), True)
		self.assertEqual(di.can_resolve(B), False)
		self.assertNotEqual(type(di.resolve(A)), A)
		self.assertEqual(type(di.resolve(A)), B)

	def test_resolve(self) -> None:
		di = DI()
		di.bind(A, B)
		di.bind(X, factory_x)
		di.bind(Y, Y)
		self.assertEqual(type(di.resolve(A)), B)
		self.assertEqual(type(di.resolve(X)), X)
		self.assertEqual(type(di.resolve(Y)), Y)

	def test_invoke(self) -> None:
		def factory(a: A, x: X, suffix: str) -> str:
			return f'{a.__class__.__name__}.{x.__class__.__name__}.{suffix}'

		di = DI()
		di.bind(A, B)
		di.bind(X, X)
		self.assertEqual(di.invoke(factory, 'hogefuga'), 'B.X.hogefuga')

	def test_combine(self) -> None:
		di1 = DI()
		di1.bind(A, A)
		di1.bind(B, B)
		di1.bind(X, X)

		di2 = DI()
		di2.bind(A, A)
		di2.bind(X, X)
		di2.bind(Y, Y)

		# 通常利用でシンボル解決できるか確認
		combined_before = di1.combine(di2)
		self.assertEqual(type(di1.resolve(A)), A)
		self.assertEqual(type(di1.resolve(X)), X)
		self.assertEqual(type(di2.resolve(A)), A)
		self.assertEqual(type(di2.resolve(Y)), Y)
		self.assertEqual(type(combined_before.resolve(A)), A)
		self.assertEqual(type(combined_before.resolve(X)), X)
		self.assertEqual(type(combined_before.resolve(Y)), Y)

		# シンボル解決前に合成した場合、一致しないことを確認
		self.assertNotEqual(di1.resolve(A), combined_before.resolve(A))
		self.assertNotEqual(di1.resolve(X), combined_before.resolve(X))
		self.assertNotEqual(di2.resolve(A), combined_before.resolve(A))
		self.assertNotEqual(di2.resolve(Y), combined_before.resolve(Y))

		# シンボル解決後に合成した場合、合成元と一致することを確認
		# 同じシンボルはdi2で上書きされることを確認
		combined_after = di1.combine(di2)
		self.assertNotEqual(di1.resolve(A), combined_after.resolve(A))
		self.assertNotEqual(di1.resolve(X), combined_after.resolve(X))
		self.assertEqual(di2.resolve(A), combined_after.resolve(A))
		self.assertEqual(di2.resolve(X), combined_after.resolve(X))
		self.assertEqual(di2.resolve(Y), combined_after.resolve(Y))

		# rebindにより誤ってオリジナルのDIが影響を受けないか確認
		combined_after.rebind(A, B)
		self.assertEqual(type(di1.resolve(A)), A)
		self.assertEqual(type(di2.resolve(A)), A)
		self.assertNotEqual(di1.resolve(A), combined_after.resolve(A))
		self.assertNotEqual(di2.resolve(A), combined_after.resolve(A))

		# combineにより誤ってオリジナルのDIが影響を受けないか確認
		with self.assertRaises(ValueError):
			di1.resolve(Y)

		with self.assertRaises(ValueError):
			di2.resolve(B)
