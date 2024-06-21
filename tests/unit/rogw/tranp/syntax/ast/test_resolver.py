from unittest import TestCase

from rogw.tranp.errors import LogicError
from rogw.tranp.syntax.ast.resolver import Resolver


class A: pass
class B(A): pass
class C(B): pass


class TestResolver(TestCase):
	def test_accepts(self) -> None:
		resolver = Resolver[A]()
		self.assertEqual([], resolver.accepts)
		resolver.register('a', A)
		self.assertEqual(['a'], resolver.accepts)
		resolver.register('b', B)
		self.assertEqual(['a', 'b'], resolver.accepts)
		resolver.register('c', C)
		self.assertEqual(['a', 'b', 'c'], resolver.accepts)

	def test_can_resolve(self) -> None:
		resolver = Resolver[A]()
		self.assertEqual(False, resolver.can_resolve('a'))
		resolver.register('a', A)
		self.assertEqual(True, resolver.can_resolve('a'))

	def test_register(self) -> None:
		resolver = Resolver[A]()
		self.assertEqual([], resolver.accepts)
		resolver.register('a', A)
		resolver.register('b', B)
		resolver.register('c', C)
		self.assertEqual(['a', 'b', 'c'], resolver.accepts)

		with self.assertRaises(LogicError):
			resolver.resolve('d')

	def test_unregister(self) -> None:
		resolver = Resolver[A]()
		resolver.register('a', A)
		self.assertEqual(['a'], resolver.accepts)
		resolver.unregister('a')
		self.assertEqual([], resolver.accepts)

		try:
			resolver.unregister('a')
		except Exception:
			self.fail()

	def test_resolve(self) -> None:
		resolver = Resolver[A]()
		resolver.register('a', A)
		resolver.register('b', B)
		resolver.register('c', C)
		self.assertEqual([A], resolver.resolve('a'))
		self.assertEqual([B], resolver.resolve('b'))
		self.assertEqual([C], resolver.resolve('c'))

	def test_fallback(self) -> None:
		resolver = Resolver[A]()
		resolver.register('a', A)
		resolver.fallback(B)
		self.assertEqual([A], resolver.resolve('a'))
		self.assertEqual([B], resolver.resolve('b'))

	def test_clear(self) -> None:
		resolver = Resolver[A]()
		resolver.register('a', A)
		resolver.register('b', B)
		self.assertEqual(['a', 'b'], resolver.accepts)
		resolver.clear()
		self.assertEqual([], resolver.accepts)
