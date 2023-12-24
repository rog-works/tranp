from typing import Callable
from unittest import TestCase

from py2cpp.lang.di import DI

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
		di.register(A, B)
		di.register(X, X)
		self.assertEqual(di.can_resolve(A), True)
		self.assertEqual(di.can_resolve(B), False)
		self.assertEqual(di.can_resolve(X), True)
		self.assertEqual(di.can_resolve(Y), False)

	def test_register(self) -> None:
		di = DI()
		di.register(B, B)
		di.register(X, factory_x)
		di.register(Y, Y)
		self.assertEqual(di.can_resolve(A), False)
		self.assertEqual(di.can_resolve(B), True)
		self.assertEqual(di.can_resolve(X), True)
		self.assertEqual(di.can_resolve(Y), True)

	def test_unregister(self) -> None:
		di = DI()
		di.register(A, A)
		di.register(B, B)
		di.register(X, X)
		di.register(Y, Y)
		di.unregister(X)
		di.unregister(Y)
		self.assertEqual(di.can_resolve(A), True)
		self.assertEqual(di.can_resolve(B), True)
		self.assertEqual(di.can_resolve(X), False)
		self.assertEqual(di.can_resolve(Y), False)

	def test_resolve(self) -> None:
		di = DI()
		di.register(A, B)
		di.register(X, factory_x)
		di.register(Y, Y)
		self.assertEqual(type(di.resolve(A)), B)
		self.assertEqual(type(di.resolve(X)), X)
		self.assertEqual(type(di.resolve(Y)), Y)

	def test_curry(self) -> None:
		def factory(a: A, x: X, suffix: str) -> str:
			return f'{a.__class__.__name__}.{x.__class__.__name__}.{suffix}'

		di = DI()
		di.register(A, B)
		di.register(X, X)
		curried = di.curry(factory, Callable[[str], str])
		self.assertEqual(curried('hogefuga'), 'B.X.hogefuga')
