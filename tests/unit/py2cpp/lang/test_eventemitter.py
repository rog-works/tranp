from unittest import TestCase

from py2cpp.lang.eventemitter import EventEmitter
from tests.test.helper import data_provider


class TestEventEmitter(TestCase):
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

		emitter = EventEmitter()
		emitter.on('hoge', handler)
		emitter.emit('hoge', v=v, s=s)
		self.assertEqual(result['v'], v)
		self.assertEqual(result['s'], s)


	def test_on(self) -> None:
		def handler():
			raise ValueError()

		emitter = EventEmitter()
		emitter.on('hoge', handler)
		with self.assertRaises(ValueError):
			emitter.emit('hoge')


	def test_off(self) -> None:
		def handler():
			raise ValueError()

		try:
			emitter = EventEmitter()
			emitter.on('hoge', handler)
			emitter.off('hoge', handler)
			emitter.emit('hoge')
		except Exception:
			self.fail()


	def test_clear(self) -> None:
		def handler():
			raise ValueError()

		try:
			emitter = EventEmitter()
			emitter.on('hoge', handler)
			emitter.clear()
		except Exception:
			self.fail()
