from unittest import TestCase

from rogw.tranp.lang.parser import Entry, BlockParser, parse_block, parse_block_to_entry, parse_bracket_block, parse_pair_block
from rogw.tranp.test.helper import data_provider


class TestParser(TestCase):
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
		('{{a, b}, {c, d(e, f)}}', '{}', ['{{a, b}, {c, d(e, f)}}', '{a, b}', '{c, d(e, f)}']),
		('((a), ("b, c"))', '()', ['((a), ("b, c"))', '(a)', '("b, c")']),
	])
	def test_parse_bracket_block(self, text: str, brackets: str, expected: list[str]) -> None:
		self.assertEqual(parse_bracket_block(text, brackets), expected)

	@data_provider([
		('', '', ':', []),
		('{}', '{}', ':', [{'name': '', 'elems': ['']}]),
		('{a: {b: c}}', '{}', ':', [{'name': '', 'elems': ['a', '{b: c}']}, {'name': '', 'elems': ['b', 'c']}]),
		('tag<a, tag[1]<b>, c>', '<>', ',', [{'name': 'tag', 'elems': ['a', 'tag[1]<b>', 'c']}, {'name': 'tag[1]', 'elems': ['b']}]),
		('{{a, b}, {c, d(e, f)}}', '{}', ',', [{'name': '', 'elems': ['{a, b}', '{c, d(e, f)}']}, {'name': '', 'elems': ['a', 'b']}, {'name': '', 'elems': ['c', 'd(e, f)']}]),
		('a(b, "c, d")', '()', ',', [{'name': 'a', 'elems': ['b', '"c, d"']}]),
	])
	def test_parse_block(self, text: str, brackets: str, delimiter: str, expected: list[dict[str, list[str]]]) -> None:
		self.assertEqual(parse_block(text, brackets, delimiter), expected)

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
		('tag1(a, tag2(b))', '()', ',', [('a', 'tag2(b)')]),
		('tag1(a, tag2(b), c)', '()', ',', [('a', 'tag2(b)')]),
	])
	def test_parse_pair_block(self, text: str, brackets: str, delimiter: str, expected: list[tuple[str]]) -> None:
		self.assertEqual(parse_pair_block(text, brackets, delimiter), expected)

	@data_provider([
		('(a, b)', '()', ',', '{delimiter} ', '{name}{open}{elems}{close}', None, '(a, b)'),
		('{a: {b: c}}', '{}', ':', '{delimiter}', '{name}{open}{elems}{close}', None, '{a:{b:c}}'),
		('a<b, c<d>>', '<>', ',', '{delimiter} ', '{name}{open}{elems}{close}', lambda entry: entry.format(block_format='{elems}*') if entry.name == 'c' else None, 'a<b, d*>'),
		('std::map<CP<A>, CP<B>>', '<>', ',', '{delimiter} ', '{name}{open}{elems}{close}', lambda entry: entry.delimiter.join(entry.elems) if entry.name == 'CP' else None, 'std::map<A, B>'),
	])
	def test_parse_block_to_entry(self, text: str, brackets: str, delimiter: str, join_format: str, block_format: str, alt_formatter: Entry.AltFormatter | None, expected: str) -> None:
		entry = parse_block_to_entry(text, brackets, delimiter)
		self.assertEqual(entry.format(join_format, block_format, alt_formatter), expected)

	@data_provider([
		('{a, {b, c}, e}', '{}', ',', [
			(0, 14, 0, BlockParser.Kinds.Block),
			(1, 2, 1, BlockParser.Kinds.Element),
			(4, 10, 1, BlockParser.Kinds.Block),
			(5, 6, 2, BlockParser.Kinds.Element),
			(8, 9, 2, BlockParser.Kinds.Element),
			(12, 13, 1, BlockParser.Kinds.Element)
		]),
		('a{"b": b(1, 2), "c,d": {"e": 3}}', '{}', ':,', [
			(0, 32, 0, BlockParser.Kinds.Block),
			(2, 5, 1, BlockParser.Kinds.Element),
			(7, 14, 1, BlockParser.Kinds.Element),
			(16, 21, 1, BlockParser.Kinds.Element),
			(23, 31, 1, BlockParser.Kinds.Block),
			(24, 27, 2, BlockParser.Kinds.Element),
			(29, 30, 2, BlockParser.Kinds.Element),
		]),
	])
	def test_parse(self, text: str, brackets: str, delimiter: str, expected: list[tuple]) -> None:
		actual = BlockParser.parse(text, brackets, delimiter)
		entries = [actual, *list(actual.each())]
		for i, entry in enumerate(entries):
			self.assertEqual((entry.begin, entry.end, entry.depth, entry.kind), expected[i])
