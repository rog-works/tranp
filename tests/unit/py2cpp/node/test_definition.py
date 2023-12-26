from typing import Any
from unittest import TestCase

from lark import Tree, Token

from py2cpp.ast.entry import Entry
import py2cpp.node.definition as defs
from py2cpp.tp_lark.entry import EntryOfLark
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestDefinition(TestCase):
	fixture = Fixture.make(__file__)

	# Statement compound

	@data_provider([
		(
			EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'if_stmt'), [Tree('const_true', []), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'pass_stmt'), [])]), Tree(Token('RULE', 'elifs'), []), None])])),
			'file_input.if_stmt', {
			'condition': defs.Truthy,
			'statements': [defs.Pass],
		}),
	])
	def test_if(self, tree: Entry, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(tree).by(full_path).as_a(defs.If)
		self.assertEqual(type(node.condition), expected['condition'])
		for index, statement in enumerate(node.block.statements):
			in_expected = expected['statements'][index]
			self.assertEqual(type(statement), in_expected)

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[1]', {
			'name': 'func1',
			'access': 'public',
			'decorators': [],
			'parameters': [
				{'name': 'self', 'type': 'Empty', 'default': 'Empty'},
				{'name': 'value', 'type': 'int', 'default': 'Empty'},
			],
			'return': defs.Symbol,
		}),
		('file_input.class_def[4].class_def_raw.block.function_def[2]', {
			'name': '_func2',
			'access': 'protected',
			'decorators': [
				{'symbol': 'deco_func', 'arguments': [{'value': "'hoge'"}]},
			],
			'parameters': [
				{'name': 'self', 'type': 'Empty', 'default': 'Empty'},
				{'name': 'text', 'type': 'str', 'default': 'Empty'},
			],
			'return': defs.ListType,
		}),
		('file_input.function_def', {
			'name': 'func3',
			'access': 'public',
			'decorators': [],
			'parameters': [
				{'name': 'ok', 'type': 'bool', 'default': 'Empty'},
			],
			'return': defs.Null,
		}),
	])
	def test_function(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Function)
		self.assertEqual(node.symbol.tokens, expected['name'])
		self.assertEqual(node.access, expected['access'])
		self.assertEqual(len(node.decorators), len(expected['decorators']))
		for index, decorator in enumerate(node.decorators):
			in_expected = expected['decorators'][index]
			self.assertEqual(decorator.symbol.tokens, in_expected['symbol'])
			self.assertEqual(len(decorator.arguments), len(in_expected['arguments']))
			for index_arg, argument in enumerate(decorator.arguments):
				in_arg_expected = in_expected['arguments'][index_arg]
				self.assertEqual(argument.value.tokens, in_arg_expected['value'])

		self.assertEqual(len(node.parameters), len(expected['parameters']))
		for index, parameter in enumerate(node.parameters):
			in_expected = expected['parameters'][index]
			self.assertEqual(parameter.symbol.tokens, in_expected['name'])
			self.assertEqual(parameter.var_type.tokens if parameter.var_type.is_a(defs.Symbol) else 'Empty', in_expected['type'])
			self.assertEqual(parameter.default_value.tokens if parameter.default_value.is_a(defs.Terminal) else 'Empty', in_expected['default'])

		self.assertEqual(type(node.return_type), expected['return'])
		self.assertEqual(type(node.block), defs.Block)

	@data_provider([
		('file_input.class_def[3]', {
			'name': 'Base',
			'decorators': [],
			'parents': [],
			'constructor': {},
			'methods': [],
			'vars': [],
		}),
		('file_input.class_def[4]', {
			'name': 'Hoge',
			'decorators': [
				{'symbol': 'deco', 'arguments': [{'value': 'A'}, {'value': 'A.B'}]},
			],
			'parents': [
				{'symbol': 'Base'},
			],
			'constructor': {
				'decl_vars': [
					{'symbol': 'self', 'type': 'Empty'},
					{'symbol': 'v', 'type': 'int'},
					{'symbol': 's', 'type': 'str'},
				],
			},
			'methods': [
				{'name': 'func1'},
				{'name': '_func2'},
			],
			'vars': [
				{'symbol': 'self.v', 'type': defs.AnnoAssign},
				{'symbol': 'self.s', 'type': defs.AnnoAssign},
			],
		}),
	])
	def test_class(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Class)
		self.assertEqual(node.symbol.tokens, expected['name'])
		self.assertEqual(len(node.decorators), len(expected['decorators']))
		for index, decorator in enumerate(node.decorators):
			in_expected = expected['decorators'][index]
			self.assertEqual(decorator.symbol.tokens, in_expected['symbol'])
			for index_arg, argument in enumerate(decorator.arguments):
				in_arg_expected = in_expected['arguments'][index_arg]
				self.assertEqual(argument.value.tokens, in_arg_expected['value'])

		self.assertEqual(len(node.parents), len(expected['parents']))
		for index, parent in enumerate(node.parents):
			in_expected = expected['parents'][index]
			self.assertEqual(parent.tokens, in_expected['symbol'])

		self.assertEqual(node.constructor_exists, len(expected['constructor'].keys()) > 0)
		if node.constructor_exists:
			in_expected = expected['constructor']
			constructor = node.constructor
			self.assertEqual(type(constructor), defs.Constructor)
			self.assertEqual(len(constructor.decl_vars), len(in_expected['decl_vars']))
			for index, var in enumerate(constructor.decl_vars):
				in_var_expected = in_expected['decl_vars'][index]
				self.assertEqual(var.symbol.tokens, in_var_expected['symbol'])
				if isinstance(var, defs.AnnoAssign):
					self.assertEqual(var.var_type.tokens, in_var_expected['type'])
				elif isinstance(var, defs.MoveAssign):
					self.assertEqual('Empty', in_var_expected['type'])
				elif isinstance(var, defs.Parameter):
					self.assertEqual(var.var_type.tokens if var.var_type.is_a(defs.Symbol) else 'Empty', in_var_expected['type'])

		self.assertEqual(len(node.methods), len(expected['methods']))
		for index, method in enumerate(node.methods):
			in_expected = expected['methods'][index]
			self.assertEqual(type(method), defs.Method)
			self.assertEqual(method.symbol.tokens, in_expected['name'])

		self.assertEqual(len(node.vars), len(expected['vars']))
		for index, var in enumerate(node.vars):
			in_expected = expected['vars'][index]
			self.assertEqual(type(var), in_expected['type'])
			self.assertEqual(var.symbol.tokens, in_expected['symbol'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.enum_def', {
			'name': 'Values',
			'vars': [
				{'symbol': 'A', 'value': '0'},
				{'symbol': 'B', 'value': '1'},
			],
		}),
	])
	def test_enum(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Enum)
		self.assertEqual(node.symbol.tokens, expected['name'])
		self.assertEqual(len(node.vars), len(expected['vars']))
		for index, var in enumerate(node.vars):
			in_expected = expected['vars'][index]
			self.assertEqual(var.symbol.tokens, in_expected['symbol'])
			self.assertEqual(var.value.tokens, in_expected['value'])

	# Statement simple

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[0]', {
			'symbol': 'map',
			'var_type': defs.DictType,
			'value': defs.Dict,
		}),
	])
	def test_anno_assign(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.AnnoAssign)
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(type(node.var_type), expected['var_type'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[5]', {
			'symbol': defs.Indexer,
			'operator': '+=',
			'value': defs.Indexer,
		}),
	])
	def test_aug_assign(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.AugAssign)
		self.assertEqual(type(node.symbol), expected['symbol'])
		self.assertEqual(node.operator.tokens, expected['operator'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('file_input.import_stmt[1]', {
			'module_path': 'py2cpp.cpp.enum',
			'import_symbols': [
				{'symbol': 'CEnum'},
				{'symbol': 'A'},
			],
		}),
	])
	def test_import(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Import)
		self.assertEqual(node.module_path.tokens, expected['module_path'])
		self.assertEqual(len(node.import_symbols), len(expected['import_symbols']))
		for index, symbol in enumerate(node.import_symbols):
			in_expected = expected['import_symbols'][index]
			self.assertEqual(symbol.tokens, in_expected['symbol'])

	# Primary

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[2].anno_assign.typed_getitem', {
			'value_type': 'int',
		}),
	])
	def test_list_type(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.ListType)
		self.assertEqual(node.value_type.tokens, expected['value_type'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[0].anno_assign.typed_getitem', {
			'key_type': 'Hoge.Values',
			'value_type': 'int',
		}),
	])
	def test_dict_type(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.DictType)
		self.assertEqual(node.key_type.tokens, expected['key_type'])
		self.assertEqual(node.value_type.tokens, expected['value_type'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.getitem', {
			'symbol': 'arr',
			'key': '0',
		}),
	])
	def test_indexer(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Indexer)
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(node.key.tokens, expected['key'])

	@data_provider([
		('file_input.funccall', {
			'caller': 'pragma',
			'arguments': [
				{'value': "'once'"},
			],
			'calculated': [
				'<Var: file_input.funccall.var>',
				'<String: file_input.funccall.arguments.argvalue.string>',
				'<Argument: file_input.funccall.arguments.argvalue>',
			],
		}),
	])
	def test_funccall(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.FuncCall)
		self.assertEqual(node.calls.tokens, expected['caller'])
		self.assertEqual(len(node.arguments), len(expected['arguments']))
		for index, argument in enumerate(node.arguments):
			in_expected = expected['arguments'][index]
			self.assertEqual(argument.value.tokens, in_expected['value'])

		self.assertEqual([str(node) for node in node.calculated()], expected['calculated'])

	# Operator

	@data_provider([
		(
			EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])),
			'file_input.factor', {'type': defs.Factor, 'value': '-1'},
		),
		(
			EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'factor'), [Token('PLUS', '+'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])),
			'file_input.factor', {'type': defs.Factor, 'value': '+1'},
		),
		(
			EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'factor'), [Token('TILDE', '~'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])),
			'file_input.factor', {'type': defs.Factor, 'value': '~1'},
		),
	])
	def test_unary_operator(self, tree: Entry, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(tree).by(full_path).as_a(defs.UnaryOperator)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.tokens, expected['value'])

	@data_provider([
		(
			EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'or_expr'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')]), Token('VBAR', '|'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])])])),
			'file_input.or_expr', {'type': defs.OrBitwise, 'left': '1', 'operator': '|', 'right': '2'},
		),
		(
			EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'xor_expr'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')]), Token('CIRCUMFLEX', '^'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])])])),
			'file_input.xor_expr', {'type': defs.XorBitwise, 'left': '1', 'operator': '^', 'right': '2'},
		),
		(
			EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'and_expr'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')]), Token('AMPERSAND', '&'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])])])),
			'file_input.and_expr', {'type': defs.AndBitwise, 'left': '1', 'operator': '&', 'right': '2'},
		),
		(
			EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'shift_expr'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')]), Token('__ANON_19', '<<'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])])])),
			'file_input.shift_expr', {'type': defs.ShiftBitwise, 'left': '1', 'operator': '<<', 'right': '2'},
		),
		(
			EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'shift_expr'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')]), Token('__ANON_20', '>>'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])])])),
			'file_input.shift_expr', {'type': defs.ShiftBitwise, 'left': '1', 'operator': '>>', 'right': '2'},
		),
	])
	def test_binary_operator(self, tree: Entry, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(tree).by(full_path).as_a(defs.BinaryOperator)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.left.tokens, expected['left'])
		self.assertEqual(node.operator.tokens, expected['operator'])
		self.assertEqual(node.right.tokens, expected['right'])

	# Literal

	@data_provider([
		(EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])), 'file_input.number', {'type': defs.Integer, 'value': '1'}),
		(EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'number'), [Token('HEX_NUMBER', '0x1')])])), 'file_input.number', {'type': defs.Integer, 'value': '0x1'}),
		(EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'number'), [Token('FLOAT_NUMBER', '0.1')])])), 'file_input.number', {'type': defs.Float, 'value': '0.1'}),
	])
	def test_number(self, tree: Entry, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(tree).by(full_path).as_a(defs.Number)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.tokens, expected['value'])

	@data_provider([
		(EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'string'), [Token('STRING', "'abcd'")])])), 'file_input.string', {'type': defs.String, 'value': "'abcd'"}),
		(EntryOfLark(Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'string'), [Token('LONG_STRING', '"""abcd\nefgh"""')])])), 'file_input.string', {'type': defs.String, 'value': '"""abcd\nefgh"""'}),
	])
	def test_string(self, tree: Entry, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(tree).by(full_path).as_a(defs.String)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.tokens, expected['value'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[2].anno_assign.list', {
			'values': [
				{'value': '0', 'value_type': defs.Integer},
				{'value': '1', 'value_type': defs.Integer},
				{'value': '2', 'value_type': defs.Integer},
			],
		}),
	])
	def test_list(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.List)
		self.assertEqual(len(node.values), len(expected['values']))
		for index, value in enumerate(node.values):
			in_expected = expected['values'][index]
			self.assertEqual(value.tokens, in_expected['value'])
			self.assertEqual(type(value), in_expected['value_type'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[0].anno_assign.dict', {
			'items': [
				{'key': 'Hoge.Values.A', 'value': '0', 'value_type': defs.Integer},
				{'key': 'Hoge.Values.B', 'value': '1', 'value_type': defs.Integer},
			],
		}),
	])
	def test_dict(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Dict)
		self.assertEqual(len(node.items), len(expected['items']))
		for index, item in enumerate(node.items):
			in_expected = expected['items'][index]
			self.assertEqual(item.key.tokens, in_expected['key'])
			self.assertEqual(item.value.tokens, in_expected['value'])
			self.assertEqual(type(item.value), in_expected['value_type'])
