import re
from collections.abc import Callable
from unittest import TestCase

from rogw.tranp.test.helper import data_provider
from rogw.tranp.view.error_render import ErrorRender


def hoge() -> None:
	raise Exception('hoge')


class TestErrorRender(TestCase):
	@data_provider([
		(hoge, [
			r'Stacktrace:',
			r'  [^:]+:\d+ test_usage',
			r'  [^:]+:\d+ hoge',
			r'    >>> raise Exception\(\'hoge\'\)',
			r'builtins.Exception: \("hoge"\)',
		]),
	])
	def test_usage(self, fail: Callable[[], None], expected: list[re.Pattern]) -> None:
		try:
			fail()
			self.fail()
		except AssertionError:
			pass
		except Exception as e:
			actual = str(ErrorRender(e))
			for index, line in enumerate(actual.split('\n')):
				self.assertRegex(line, expected[index])

	@data_provider([
		(__file__, (2, 5, 2, 13), [
			r'via Node:',
			r'.+:3',
			r'    >>> from unittest import TestCase',
			r'             ^^^^^^^^',
		]),
	])
	def test_quatation(self, filepath: str, source_map: tuple[int, int, int, int], expected: list[re.Pattern]) -> None:
		actual = ErrorRender.Quotation(filepath, source_map).build()
		self.assertEqual(actual[0], expected[0])
		self.assertRegex(actual[1], expected[1])
		self.assertEqual(actual[2], expected[2])
		self.assertEqual(actual[3], expected[3])
