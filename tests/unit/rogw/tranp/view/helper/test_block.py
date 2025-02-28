from unittest import TestCase

from rogw.tranp.test.helper import data_provider
from rogw.tranp.view.helper.block import AltFormatter, BlockParser, Kinds


class TestBlockParser(TestCase):
	@data_provider([
		('{a, {b, c}, e}', '{}', ',', [
			(0, 14, 0, Kinds.Block),
			(1, 2, 1, Kinds.Element),
			(4, 10, 1, Kinds.Block),
			(5, 6, 2, Kinds.Element),
			(8, 9, 2, Kinds.Element),
			(12, 13, 1, Kinds.Element)
		]),
		('a{"b": b(1, 2), "c,d": {"e": 3}}', '{}', ':,', [
			(0, 32, 0, Kinds.Block),
			(2, 5, 1, Kinds.Element),
			(7, 14, 1, Kinds.Element),
			(16, 21, 1, Kinds.Element),
			(23, 31, 1, Kinds.Block),
			(24, 27, 2, Kinds.Element),
			(29, 30, 2, Kinds.Element),
		]),
	])
	def test_parse(self, text: str, brackets: str, delimiter: str, expected: list[tuple]) -> None:
		actual = BlockParser.parse(text, brackets, delimiter)
		entries = [actual, *actual.unders()]
		for i, entry in enumerate(entries):
			self.assertEqual((entry.begin, entry.end, entry.depth, entry.kind), expected[i])

	@data_provider([
		('()', '()', ['()']),
		('[]', '[]', ['[]']),
		('{}', '{}', ['{}']),
		('<>', '<>', ['<>']),
		('(a)', '()', ['(a)']),
		('(a, (b))', '()', ['(a, (b))', '(b)']),
		('{a: {b: c}}', '{}', ['{a: {b: c}}', '{b: c}']),
		('<a, <b>, <c>>', '<>', ['<a, <b>, <c>>', '<b>', '<c>']),
		('{{a, b}, {c, d(e, f)}}', '{}', ['{{a, b}, {c, d(e, f)}}', '{a, b}', '{c, d(e, f)}']),
		('((a), ("b, c"))', '()', ['((a), ("b, c"))', '(a)', '("b, c")']),
	])
	def test_parse_bracket(self, text: str, brackets: str, expected: list[str]) -> None:
		self.assertEqual(BlockParser.parse_bracket(text, brackets), expected)

	@data_provider([
		('{}', '{}', ':', []),
		('{a: b}', '{}', ':', [('a', 'b')]),
		('{a: {b: c}}', '{}', ':', [('a', '{b: c}'), ('b', 'c')]),
		('{{a: b}: c}', '{}', ':', [('{a: b}', 'c'), ('a', 'b')]),
		('{{a: b}: {c: d}}', '{}', ':', [('{a: b}', '{c: d}'), ('a', 'b'), ('c', 'd')]),
		('{{a, b}, {c, d(e, f)}}', '{}', ',', [('{a, b}', '{c, d(e, f)}'), ('a', 'b'), ('c', 'd(e, f)')]),
		('a(b, "c, d")', '()', ',', [('b', '"c, d"')]),
		('(a, b)', '()', ',', [('a', 'b')]),
		('(a, b, c)', '()', ',', [('a', 'b')]),
		('tag(a, tag[A, B](b))', '()', ',', [('a', 'tag[A, B](b)')]),
		('tag(a, tag[A, B](b), c)', '()', ',', [('a', 'tag[A, B](b)')]),
	])
	def test_parse_pair(self, text: str, brackets: str, delimiter: str, expected: list[tuple[str]]) -> None:
		self.assertEqual(BlockParser.parse_pair(text, brackets, delimiter), expected)

	@data_provider([
		('(a, b)', '()', ',', '{delimiter} ', '{name}{open}{elems}{close}', None, '(a, b)'),
		('{a: {b: c}}', '{}', ':', '{delimiter}', '{name}{open}{elems}{close}', None, '{a:{b:c}}'),
		('a<b, c<d>>', '<>', ',', '{delimiter} ', '{name}{open}{elems}{close}', lambda entry: entry.format(block_format='{elems}*') if entry.name == 'c' else None, 'a<b, d*>'),
		('std::map<CP<A>, CP<B>>', '<>', ',', '{delimiter} ', '{name}{open}{elems}{close}', lambda entry: entry.delimiter.join(entry.elems) if entry.name == 'CP' else None, 'std::map<A, B>'),
	])
	def test_parse_to_formatter(self, text: str, brackets: str, delimiter: str, join_format: str, block_format: str, alt_formatter: AltFormatter | None, expected: str) -> None:
		formatter = BlockParser.parse_to_formatter(text, brackets, delimiter)
		self.assertEqual(formatter.format(join_format, block_format, alt_formatter), expected)

	@data_provider([
		('[]', '[]', ('', '')),
		('a[0].b[1][2]', '[]', ('a[0].b[1]', '2')),
		('a[0].b[c[1]]', '[]', ('a[0].b', 'c[1]')),
		('a[b(c, d)[0]].e[1, 2]', '[]', ('a[b(c, d)[0]].e', '1, 2')),
		('a().b(1, 2[3]).c({});', '()', ('a().b(1, 2[3]).c', '{}')),
	])
	def test_break_block(self, text: str, delimiter: str, expected: tuple[str, str]) -> None:
		actual = BlockParser.break_last_block(text, delimiter)
		self.assertEqual(actual, expected)

	@data_provider([
		('', ',', []),
		('a', ',', ['a']),
		('1, 2', ',', ['1', '2']),
		('abc->def', '->', ['abc', 'def']),
		('1, f(2, b=3), l[0]', ',', ['1', 'f(2, b=3)', 'l[0]']),
		('a->b[c], d->e(f)', ',', ['a->b[c]', 'd->e(f)']),
		('std::map<std::string, int> dsn', ' ', ['std::map<std::string, int>', 'dsn']),
		('std::map<std::string, int> dsn = {}', '=', ['std::map<std::string, int> dsn', '{}']),
		('f(a->b().c()), d', ',', ['f(a->b().c())', 'd']),
	])
	def test_break_separator(self, text: str, delimiter: str, expected: list[str]) -> None:
		actual = BlockParser.break_separator(text, delimiter)
		self.assertEqual(actual, expected)
