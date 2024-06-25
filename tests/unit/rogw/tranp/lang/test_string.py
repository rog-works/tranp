from unittest import TestCase

from rogw.tranp.lang.string import camelize, parse_brakets, snakelize
from rogw.tranp.test.helper import data_provider


class TestString(TestCase):
	@data_provider([
		('hoge_fuga_piyo', 'HogeFugaPiyo'),
		('_hoge_fuga_piyo', 'HogeFugaPiyo'),
		('__hoge_fuga_piyo', 'HogeFugaPiyo'),
		('HogeFugaPiyo', 'Hogefugapiyo'),
	])
	def test_camelize(self, org: str, expected: str) -> None:
		self.assertEqual(expected, camelize(org))

	@data_provider([
		('HogeFugaPiyo', 'hoge_fuga_piyo'),
		('_HogeFugaPiyo', 'hoge_fuga_piyo'),
		('hoge_fuga_piyo', 'hoge_fuga_piyo'),
		('Hoge_Fuga_Piyo', 'hoge__fuga__piyo'),
	])
	def test_snakelize(self, org: str, expected: str) -> None:
		self.assertEqual(expected, snakelize(org))

	@data_provider([
		('()', '()', -1, ['()']),
		('[]', '[]', -1, ['[]']),
		('{}', '{}', -1, ['{}']),
		('<>', '<>', -1, ['<>']),
		('(a)', '()', -1, ['(a)']),
		('(a, (b))', '()', -1, ['(a, (b))', '(b)']),
		('{a: {b: c}}', '{}', -1, ['{a: {b: c}}', '{b: c}']),
		('[a], [b], [c]', '[]', -1, ['[a]', '[b]', '[c]']),
		('<a, <b>, <c>>', '<>', -1, ['<a, <b>, <c>>', '<b>', '<c>']),
		('()', '()', 0, []),
		('[a], [b], [c]', '[]', 1, ['[a]']),
	])
	def test_parse_brakets(self, text: str, brakets: str, limit: int, expected: list[str]) -> None:
		self.assertEqual(expected, parse_brakets(text, brakets, limit))
