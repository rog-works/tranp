from unittest import TestCase

from py2cpp.analyze.symbol import Primitives
from py2cpp.analyze.symbols import Symbols
from py2cpp.ast.dsn import DSN
import py2cpp.compatible.python.classes as classes
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


def _ast(before: str, after: str) -> str:
	aliases = {
		'__main__': 'file_input',
		'A': 'file_input.class_def[2]',
		'A.__init__.params': 'file_input.class_def[2].class_def_raw.block.function_def.function_def_raw.parameters',
		'A.__init__.return': 'file_input.class_def[2].class_def_raw.block.function_def.function_def_raw.return_type',
		'A.__init__.block': 'file_input.class_def[2].class_def_raw.block.function_def.function_def_raw.block',
		'B': 'file_input.class_def[3]',
		'B.B2': 'file_input.class_def[3].class_def_raw.block.class_def',
		'B.B2.block': 'file_input.class_def[3].class_def_raw.block.class_def.class_def_raw.block',
		'B.B2.class_func': 'file_input.class_def[3].class_def_raw.block.class_def.class_def_raw.block.function_def',
		'B.B2.class_func.params': 'file_input.class_def[3].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.parameters',
		'B.B2.class_func.return': 'file_input.class_def[3].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.return_type',
		'B.B2.class_func.block': 'file_input.class_def[3].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.block',
		'B.__init__.params': 'file_input.class_def[3].class_def_raw.block.function_def[1].function_def_raw.parameters',
		'B.__init__.return': 'file_input.class_def[3].class_def_raw.block.function_def[1].function_def_raw.return_type',
		'B.__init__.block': 'file_input.class_def[3].class_def_raw.block.function_def[1].function_def_raw.block',
		'B.func1.params': 'file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.parameters',
		'B.func1.return': 'file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.return_type',
		'B.func1.block': 'file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.block',
		'B.func2.block': 'file_input.class_def[3].class_def_raw.block.function_def[3].function_def_raw.block',
		'B.func2.closure.block': 'file_input.class_def[3].class_def_raw.block.function_def[3].function_def_raw.block.function_def.function_def_raw.block',
	}
	return DSN.join(aliases[before], after)


def _mod(before: str, after: str) -> str:
	aliases = {
		'xyz': 'tests.unit.py2cpp.analyze.fixtures.test_db_xyz',
		'classes': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes',
	}
	return DSN.join(aliases[before], after)


class TestSymbols(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		('__main__.B.func2.a', False),
		('__main__.B.func2.closure.b', True),
		('__main__.d', False),
	])
	def test_is_list(self, fullyname: str, expected: bool) -> None:
		symbols = self.fixture.get(Symbols)
		symbol = symbols.from_fullyname(fullyname)
		self.assertEqual(symbols.is_list(symbol), expected)

	@data_provider([
		('__main__.B.func2.a', False),
		('__main__.B.func2.closure.b', False),
		('__main__.d', True),
	])
	def test_is_dict(self, fullyname: str, expected: bool) -> None:
		symbols = self.fixture.get(Symbols)
		symbol = symbols.from_fullyname(fullyname)
		self.assertEqual(symbols.is_dict(symbol), expected)

	@data_provider([
		('__main__.B.func2.a', 'int'),
		('__main__.B.func2.closure.b', 'list<int>'),
		('__main__.B.func2.if.for.i', 'T_Seq'),  # FIXME 追って修正
		('__main__.B.func2.if.for.try.e', 'Exception'),
	])
	def test_from_fullyname(self, fullyname: str, expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		symbol = symbols.from_fullyname(fullyname)
		self.assertEqual(str(symbol), expected)

	@data_provider([
		(int, _mod('classes', int.__name__)),
		(float, _mod('classes', float.__name__)),
		(str, _mod('classes', str.__name__)),
		(bool, _mod('classes', bool.__name__)),
		(tuple, _mod('classes', tuple.__name__)),
		(classes.Pair, _mod('classes', classes.Pair.__name__)),
		(list, _mod('classes', list.__name__)),
		(dict, _mod('classes', dict.__name__)),
		(classes.Unknown, _mod('classes', classes.Unknown.__name__)),
		(None, _mod('classes', 'None')),
	])
	def test_type_of_primitive(self, primitive_type: type[Primitives] | None, expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		self.assertEqual(symbols.type_of_primitive(primitive_type).types.fullyname, expected)

	@data_provider([
		(_ast('__main__', 'import_stmt.import_names.name'), _mod('xyz', 'Z'), 'Z'),
		(_ast('__main__', 'anno_assign.var'), _mod('classes', 'int'), 'int'),
		(_ast('__main__', 'anno_assign.typed_var'), _mod('classes', 'int'), 'int'),
		(_ast('__main__', 'anno_assign.number'), _mod('classes', 'int'), 'int'),
		(_ast('__main__', 'assign.var'), _mod('classes', 'dict'), 'dict<str, int>'),
		# 5
		(_ast('A', ''), '__main__.A', 'A'),
		(_ast('A', 'class_def_raw.name'), '__main__.A', 'A'),
		(_ast('A.__init__.params', 'paramvalue.typedparam.name'), '__main__.A', 'A'),
		(_ast('A.__init__.return', 'typed_none'), _mod('classes', 'None'), 'None'),
		(_ast('A.__init__.block', 'anno_assign.getattr'), _mod('classes', 'str'), 'str'),
		# 10
		(_ast('A.__init__.block', 'anno_assign.typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('A.__init__.block', 'anno_assign.string'), _mod('classes', 'str'), 'str'),
		(_ast('B', ''), '__main__.B', 'B'),
		(_ast('B', 'class_def_raw.name'), '__main__.B', 'B'),
		(_ast('B', 'class_def_raw.typed_arguments.typed_argvalue.typed_var'), '__main__.A', 'A'),
		# 15
		(_ast('B.B2', ''), '__main__.B.B2', 'B2'),
		(_ast('B.B2.block', 'anno_assign.var'), _mod('classes', 'str'), 'str'),
		(_ast('B.B2.block', 'anno_assign.typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('B.B2.block', 'anno_assign.string'), _mod('classes', 'str'), 'str'),
		(_ast('B.B2.class_func', ''), '__main__.B.B2.class_func', 'class_func<B2, dict<str, int>>'),
		# 20
		(_ast('B.B2.class_func.params', 'paramvalue.typedparam.name'), '__main__.B.B2', 'B2'),
		(_ast('B.B2.class_func.return', 'typed_getitem'), _mod('classes', 'dict'), 'dict'), # FIXME 追って修正 'dict[str, int]'
		(_ast('B.B2.class_func.block', 'return_stmt.dict'), _mod('classes', 'dict'), 'dict<str, int>'),
		(_ast('B.__init__.params', 'paramvalue.typedparam.name'), '__main__.B', 'B'),
		(_ast('B.__init__.return', 'typed_none'), _mod('classes', 'None'), 'None'),
		# 25
		(_ast('B.__init__.block', 'funccall'), '__main__.A', 'A'),
		(_ast('B.__init__.block', 'funccall.getattr.funccall.var'), _mod('classes', 'super'), 'super'),
		(_ast('B.__init__.block', 'anno_assign'), _mod('classes', 'list'), 'list<int>'),
		(_ast('B.__init__.block', 'anno_assign.getattr'), _mod('classes', 'list'), 'list<int>'),
		(_ast('B.__init__.block', 'anno_assign.typed_getitem'), _mod('classes', 'list'), 'list'), # FIXME 追って修正 'list<int>'
		# 30
		(_ast('B.__init__.block', 'anno_assign.list'), _mod('classes', 'list'), 'list<Unknown>'),
		(_ast('B.func1.params', 'paramvalue[0].typedparam.name'), '__main__.B', 'B'),
		(_ast('B.func1.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'list'), 'list<B>'),
		(_ast('B.func1.return', 'typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('B.func1.block', 'assign[0].var'), _mod('classes', 'bool'), 'bool'),
		# 35
		(_ast('B.func1.block', 'assign[0].const_false'), _mod('classes', 'bool'), 'bool'),
		(_ast('B.func1.block', 'funccall[1].arguments.argvalue.var'), _mod('classes', 'bool'), 'bool'),
		(_ast('B.func1.block', 'funccall[2].arguments.argvalue.getattr'), _mod('classes', 'list'), 'list<int>'),
		(_ast('B.func1.block', 'funccall[3].arguments.argvalue.getattr'), _mod('classes', 'list'), 'list<int>'),
		(_ast('B.func1.block', 'assign[4].getattr'), _mod('classes', 'str'), 'str'),
		# 40
		(_ast('B.func1.block', 'assign[4].string'), _mod('classes', 'str'), 'str'),
		(_ast('B.func1.block', 'assign[5].getattr'), _mod('classes', 'int'), 'int'),
		(_ast('B.func1.block', 'assign[5].number'), _mod('classes', 'int'), 'int'),
		(_ast('B.func1.block', 'assign[6]'), 'py2cpp.compatible.python.template.T_Seq', 'T_Seq'), # FIXME 追って修正 _mod('classes', 'int'), []),
		(_ast('B.func1.block', 'return_stmt.getattr'), _mod('classes', 'str'), 'str'),
		# 45
		(_ast('B.func2.block', 'if_stmt.block.assign.var'), _mod('classes', 'int'), 'int'),
		(_ast('B.func2.closure.block', 'assign.var'), _mod('classes', 'list'), 'list<int>'),
	])
	def test_type_of(self, full_path: str, expected: str, attrs_expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		node = self.fixture.shared_nodes.by(full_path)
		symbol = symbols.type_of(node)
		self.assertEqual(symbol.types.fullyname, expected)
		self.assertEqual(str(symbol), attrs_expected)
