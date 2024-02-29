from unittest import TestCase

from rogw.tranp.errors import LogicError
from rogw.tranp.ast.resolver import Resolver


class A: pass
class B(A): pass
class C(B): pass


class TestResolver(TestCase):
	def test_accepts(self) -> None:
		resolver = Resolver[A]()
		self.assertEqual(resolver.accepts, [])
		resolver.register('a', A)
		self.assertEqual(resolver.accepts, ['a'])
		resolver.register('b', B)
		self.assertEqual(resolver.accepts, ['a', 'b'])
		resolver.register('c', C)
		self.assertEqual(resolver.accepts, ['a', 'b', 'c'])

	def test_can_resolve(self) -> None:
		resolver = Resolver[A]()
		self.assertEqual(resolver.can_resolve('a'), False)
		resolver.register('a', A)
		self.assertEqual(resolver.can_resolve('a'), True)

	def test_register(self) -> None:
		resolver = Resolver[A]()
		self.assertEqual(resolver.accepts, [])
		resolver.register('a', A)
		resolver.register('b', B)
		resolver.register('c', C)
		self.assertEqual(resolver.accepts, ['a', 'b', 'c'])

		with self.assertRaises(LogicError):
			resolver.resolve('d')

	def test_unregister(self) -> None:
		resolver = Resolver[A]()
		resolver.register('a', A)
		self.assertEqual(resolver.accepts, ['a'])
		resolver.unregister('a')
		self.assertEqual(resolver.accepts, [])

		try:
			resolver.unregister('a')
		except Exception:
			self.fail()

	def test_resolve(self) -> None:
		resolver = Resolver[A]()
		resolver.register('a', A)
		resolver.register('b', B)
		resolver.register('c', C)
		self.assertEqual(resolver.resolve('a'), [A])
		self.assertEqual(resolver.resolve('b'), [B])
		self.assertEqual(resolver.resolve('c'), [C])

	def test_fallback(self) -> None:
		resolver = Resolver[A]()
		resolver.register('a', A)
		resolver.fallback(B)
		self.assertEqual(resolver.resolve('a'), [A])
		self.assertEqual(resolver.resolve('b'), [B])

	def test_clear(self) -> None:
		resolver = Resolver[A]()
		resolver.register('a', A)
		resolver.register('b', B)
		self.assertEqual(resolver.accepts, ['a', 'b'])
		resolver.clear()
		self.assertEqual(resolver.accepts, [])
