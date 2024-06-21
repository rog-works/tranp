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
		self.assertEqual(True, di.can_resolve(A))
		self.assertEqual(False, di.can_resolve(B))
		self.assertEqual(True, di.can_resolve(X))
		self.assertEqual(False, di.can_resolve(Y))

	def test_bind(self) -> None:
		di = DI()
		di.bind(B, B)
		di.bind(X, factory_x)
		di.bind(Y, Y)
		self.assertEqual(False, di.can_resolve(A))
		self.assertEqual(True, di.can_resolve(B))
		self.assertEqual(True, di.can_resolve(X))
		self.assertEqual(True, di.can_resolve(Y))

	def test_unbind(self) -> None:
		di = DI()
		di.bind(A, A)
		di.bind(B, B)
		di.bind(X, X)
		di.bind(Y, Y)
		di.unbind(X)
		di.unbind(Y)
		self.assertEqual(True, di.can_resolve(A))
		self.assertEqual(True, di.can_resolve(B))
		self.assertEqual(False, di.can_resolve(X))
		self.assertEqual(False, di.can_resolve(Y))

	def test_rebind(self) -> None:
		di = DI()
		di.bind(A, A)
		di.rebind(A, B)
		self.assertEqual(True, di.can_resolve(A))
		self.assertEqual(False, di.can_resolve(B))
		self.assertNotEqual(A, type(di.resolve(A)))
		self.assertEqual(B, type(di.resolve(A)))

	def test_resolve(self) -> None:
		di = DI()
		di.bind(A, B)
		di.bind(X, factory_x)
		di.bind(Y, Y)
		self.assertEqual(B, type(di.resolve(A)))
		self.assertEqual(X, type(di.resolve(X)))
		self.assertEqual(Y, type(di.resolve(Y)))

	def test_invoke(self) -> None:
		def factory(a: A, x: X, suffix: str) -> str:
			return f'{a.__class__.__name__}.{x.__class__.__name__}.{suffix}'

		di = DI()
		di.bind(A, B)
		di.bind(X, X)
		self.assertEqual('B.X.hogefuga', di.invoke(factory, 'hogefuga'))

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
		self.assertEqual(A, type(di1.resolve(A)))
		self.assertEqual(X, type(di1.resolve(X)))
		self.assertEqual(A, type(di2.resolve(A)))
		self.assertEqual(Y, type(di2.resolve(Y)))
		self.assertEqual(A, type(combined_before.resolve(A)))
		self.assertEqual(X, type(combined_before.resolve(X)))
		self.assertEqual(Y, type(combined_before.resolve(Y)))

		# シンボル解決前に合成した場合、一致しないことを確認
		self.assertNotEqual(combined_before.resolve(A), di1.resolve(A))
		self.assertNotEqual(combined_before.resolve(X), di1.resolve(X))
		self.assertNotEqual(combined_before.resolve(A), di2.resolve(A))
		self.assertNotEqual(combined_before.resolve(Y), di2.resolve(Y))

		# シンボル解決後に合成した場合、合成元と一致することを確認
		# 同じシンボルはdi2で上書きされることを確認
		combined_after = di1.combine(di2)
		self.assertNotEqual(combined_after.resolve(A), di1.resolve(A))
		self.assertNotEqual(combined_after.resolve(X), di1.resolve(X))
		self.assertEqual(combined_after.resolve(A), di2.resolve(A))
		self.assertEqual(combined_after.resolve(X), di2.resolve(X))
		self.assertEqual(combined_after.resolve(Y), di2.resolve(Y))

		# rebindにより誤ってオリジナルのDIが影響を受けないか確認
		combined_after.rebind(A, B)
		self.assertEqual(A, type(di1.resolve(A)))
		self.assertEqual(A, type(di2.resolve(A)))
		self.assertNotEqual(combined_after.resolve(A), di1.resolve(A))
		self.assertNotEqual(combined_after.resolve(A), di2.resolve(A))

		# combineにより誤ってオリジナルのDIが影響を受けないか確認
		with self.assertRaises(ValueError):
			di1.resolve(Y)

		with self.assertRaises(ValueError):
			di2.resolve(B)
