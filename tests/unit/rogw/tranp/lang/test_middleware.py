from unittest import TestCase

from rogw.tranp.lang.middleware import Middleware
from rogw.tranp.test.helper import data_provider


class TestMiddleware(TestCase):
	@data_provider([
		(0, 'hoge'),
		(1, 'fuga'),
		(2, 'piyo'),
	])
	def test_emit(self, v: int, s: str) -> None:
		result = {'v': 0, 'str': ''}
		def handler(v: int, s: str):
			result['v'] = v
			result['s'] = s

		instance = Middleware()
		instance.on('hoge', handler)
		instance.emit('hoge', v=v, s=s)
		self.assertEqual(result['v'], v)
		self.assertEqual(result['s'], s)

	def test_on(self) -> None:
		def handler():
			raise ValueError()

		instance = Middleware()
		instance.on('hoge', handler)
		with self.assertRaises(ValueError):
			instance.emit('hoge')

	def test_off(self) -> None:
		def handler():
			raise ValueError()

		instance = Middleware()
		instance.on('hoge', handler)
		self.assertTrue(instance.usable('hoge'))

		instance.off('hoge', handler)
		self.assertFalse(instance.usable('hoge'))

	def test_clear(self) -> None:
		def handler():
			raise ValueError()

		try:
			instance = Middleware()
			instance.on('hoge', handler)
			instance.clear()
		except Exception:
			self.fail()
