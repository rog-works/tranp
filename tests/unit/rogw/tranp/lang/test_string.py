from unittest import TestCase

from rogw.tranp.lang.string import camelize, is_quoted_literal, snakelize
from rogw.tranp.test.helper import data_provider


class TestString(TestCase):
	@data_provider([
		('hoge_fuga_piyo', 'HogeFugaPiyo'),
		('_hoge_fuga_piyo', 'HogeFugaPiyo'),
		('__hoge_fuga_piyo', 'HogeFugaPiyo'),
		('HogeFugaPiyo', 'Hogefugapiyo'),
	])
	def test_camelize(self, org: str, expected: str) -> None:
		self.assertEqual(camelize(org), expected)

	@data_provider([
		('HogeFugaPiyo', 'hoge_fuga_piyo'),
		('_HogeFugaPiyo', 'hoge_fuga_piyo'),
		('hoge_fuga_piyo', 'hoge_fuga_piyo'),
		('Hoge_Fuga_Piyo', 'hoge__fuga__piyo'),
	])
	def test_snakelize(self, org: str, expected: str) -> None:
		self.assertEqual(snakelize(org), expected)

	@data_provider([
		('"hoge"', '"', True),
		('""', '"', True),
		("''", "'", True),
		('"{\\"key\\":123}"', '"', True),
		('\"hoge\"', '"', True),
		('"a\\b"', '"', True),
		('"a", "b"', '"', False),
	])
	def test_is_quoted_literal(self, string: str, quote: str, expected: bool) -> None:
		actual = is_quoted_literal(string, quote)
		self.assertEqual(expected, actual)
