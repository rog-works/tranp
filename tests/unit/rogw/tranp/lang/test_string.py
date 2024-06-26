from unittest import TestCase

from rogw.tranp.lang.string import camelize, parse_block, parse_braket_block, parse_pair_block, snakelize
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
		('()', '()', ['()']),
		('[]', '[]', ['[]']),
		('{}', '{}', ['{}']),
		('<>', '<>', ['<>']),
		('(a)', '()', ['(a)']),
		('(a, (b))', '()', ['(a, (b))', '(b)']),
		('{a: {b: c}}', '{}', ['{a: {b: c}}', '{b: c}']),
		('[a], [b], [c]', '[]', ['[a]', '[b]', '[c]']),
		('<a, <b>, <c>>', '<>', ['<a, <b>, <c>>', '<b>', '<c>']),
	])
	def test_parse_braket_block(self, text: str, brakets: str, expected: list[str]) -> None:
		self.assertEqual(expected, parse_braket_block(text, brakets))

	@data_provider([
		('', '', ':', []),
		('{}', '{}', ':', [{'name': '', 'elems': ['']}]),
		('{a: {b: c}}', '{}', ':', [{'name': '', 'elems': ['a', '{b: c}']}, {'name': '', 'elems': ['b', 'c']}]),
		('tag<a, tag[1]<b>, c>', '<>', ',', [{'name': 'tag', 'elems': ['a', 'tag[1]<b>', 'c']}, {'name': 'tag[1]', 'elems': ['b']}]),
	])
	def test_parse_block(self, text: str, brakets: str, delimiter: str, expected: list[dict[str, list[str]]]) -> None:
		self.assertEqual(expected, parse_block(text, brakets, delimiter))

	@data_provider([
		('{}', '{}', ':', []),
		('{a: b}', '{}', ':', [('a', 'b')]),
		('{a: {b: c}}', '{}', ':', [('a', '{b: c}'), ('b', 'c')]),
		('{{a: b}: c}', '{}', ':', [('{a: b}', 'c'), ('a', 'b')]),
		('{{a: b}: {c: d}}', '{}', ':', [('{a: b}', '{c: d}'), ('a', 'b'), ('c', 'd')]),
		('(a, b)', '()', ',', [('a', 'b')]),
		('(a, b, c)', '()', ',', []),
		('tag1(a, tag2(b), c)', '()', ',', []),
	])
	def test_parse_pair_block(self, text: str, brakets: str, delimiter: str, expected: list[tuple[str]]) -> None:
		self.assertEqual(expected, parse_pair_block(text, brakets, delimiter))
