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

	def test_clone(self) -> None:
		di = DI()
		di.bind(A, A)
		cloned = di.clone()
		self.assertEqual(type(di.resolve(A)), A)
		self.assertEqual(type(cloned.resolve(A)), A)
		self.assertNotEqual(di.resolve(A), cloned.resolve(A))
