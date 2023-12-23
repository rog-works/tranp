from unittest import TestCase

from lark import Tree, Token

from py2cpp.node.classify import make_db
import py2cpp.node.definition as defs
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestClassify(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		('file_input', [
			'__main__.pragma',
			'__main__.v',
			'__main__.A',
			'__main__.A.B',
			'__main__.A.B.__init__',
			'__main__.A.B.func1',
			'__main__.A.B.v',
		]),
	])
	def test_make_db(self, full_path: str, symbols: list[str]) -> None:
		root = self.fixture.shared.by(full_path).as_a(defs.Module)
		db = make_db(root)
		for index, path in enumerate(db.keys()):
			self.assertEqual(path, symbols[index])
