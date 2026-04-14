from unittest import TestCase

from rogw.tranp.lang.middleware import Middleware
from rogw.tranp.test.helper import data_provider


class TestMiddleware(TestCase):
	@data_provider([
		(0, 'hoge'),
		(1, 'fuga'),
		(2, 'piyo'),
	])
	def test_emit(self, n: int, s: str) -> None:
		instance = Middleware[tuple[int, str]]()
		instance.on('hoge', lambda n, s: (n, s))
		actual = instance.emit('hoge', n=n, s=s)
		self.assertEqual((n, s), actual)

	def test_on(self) -> None:
		instance = Middleware[str]()
		instance.on('hoge', lambda: 'ok')
		actual = instance.emit('hoge')
		self.assertEqual('ok', actual)

	def test_off(self) -> None:
		def handler() -> int: ...

		instance = Middleware[int]()
		instance.on('hoge', handler)
		self.assertTrue(instance.usable('hoge'))

		instance.off('hoge', handler)
		self.assertFalse(instance.usable('hoge'))

	def test_clear(self) -> None:
		instance = Middleware[int]()
		instance.on('hoge', lambda: 0)
		self.assertTrue(instance.usable('hoge'))

		instance.clear()
		self.assertFalse(instance.usable('hoge'))
