from unittest import TestCase

from rogw.tranp.lang.string import camelize, parse_block, parse_pair_block, snakelize
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
		('()', '()', [], ['()']),
		('[]', '[]', [], ['[]']),
		('{}', '{}', [], ['{}']),
		('<>', '<>', [], ['<>']),
		('(a)', '()', [], ['(a)']),
		('(a, (b))', '()', [], ['(a, (b))', '(b)']),
		('{a: {b: c}}', '{}', [], ['{a: {b: c}}', '{b: c}']),
		('[a], [b], [c]', '[]', [], ['[a]', '[b]', '[c]']),
		('<a, <b>, <c>>', '<>', [], ['<a, <b>, <c>>', '<b>', '<c>']),
		('()', '()', [1], []),
		('[a], [b], [c]', '[]', [0], ['[a]']),
	])
	def test_parse_block(self, text: str, brakets: str, groups: list[int], expected: list[str]) -> None:
		self.assertEqual(expected, parse_block(text, brakets, groups))

	@data_provider([
		('{}', '{}', ':', [], []),
		('{a: b}', '{}', ':', [], [['a', 'b']]),
		('{a: {b: c}}', '{}', ':', [], [['a', '{b: c}'], ['b', 'c']]),
		('{{a: b}: c}', '{}', ':', [], [['{a: b}', 'c'], ['a', 'b']]),
		('{{a: b}: {c: d}}', '{}', ':', [], [['{a: b}', '{c: d}'], ['a', 'b'], ['c', 'd']]),
		('{{a: b}: {c: d}}', '{}', ':', [0, 2], [['{a: b}', '{c: d}'], ['c', 'd']]),
		('(a, b)', '()', ',', [], [['a', 'b']]),
		('(a, b, c)', '()', ',', [], [['a', 'b', 'c']]),
	])
	def test_parse_pair_block(self, text: str, brakets: str, delimiter: str, groups: list[int], expected: list[tuple[str]]) -> None:
		self.assertEqual(expected, parse_pair_block(text, brakets, delimiter, groups))
