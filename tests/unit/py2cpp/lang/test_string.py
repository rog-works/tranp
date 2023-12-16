from unittest import TestCase

from py2cpp.lang.string import camelize, snakelize
from tests.test.helper import data_provider


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
