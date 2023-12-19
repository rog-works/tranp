import os
from typing import Any, Optional
from unittest import TestCase

from lark import Lark, Tree
from lark.indenter import PythonIndenter

import py2cpp.node.definition as defs
from py2cpp.node.definitions import make_settings
from py2cpp.node.nodes import NodeResolver, Nodes
from tests.test.helper import data_provider


class Fixture:
	__inst: Optional['Fixture'] = None
	__prebuild = True

	@classmethod
	@property
	def inst(cls) -> 'Fixture':
		if cls.__inst is None:
			cls.__inst = cls()

		return cls.__inst

	def __init__(self) -> None:
		tree = self.__load_prebuild_tree() if self.__prebuild else self.__parse_tree(self.__load_parser())
		self.nodes = self.__make_nodes(tree)

	def __load_parser(self) -> Lark:
		dir = os.path.join(os.path.dirname(__file__), '../../../../')
		with open(os.path.join(dir, 'data/grammar.lark')) as f:
			return Lark(f, start='file_input', postlex=PythonIndenter(), parser='lalr')

	def __parse_tree(self, parser: Lark) -> Tree:
		filepath, _ = __file__.split('.')
		fixture_path = f'{filepath}_fixture.org.py'
		with open(fixture_path) as f:
			source = '\n'.join(f.readlines())
			return parser.parse(source)

	def __load_prebuild_tree(self) -> Tree:
		from tests.unit.py2cpp.node.test_definition_fixture import fixture

		return fixture()

	def __make_resolver(self) -> NodeResolver:
		return NodeResolver.load(make_settings())

	def __make_nodes(self, tree: Tree) -> Nodes:
		return Nodes(tree, self.__make_resolver())


class TestDefinition(TestCase):
	# Statement compound

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[1]', {
			'name': 'func1',
			'access': 'public',
			'decorators': [],
			'parameters': [
				{'name': 'self', 'type': 'Empty', 'default': 'Empty'},
				{'name': 'value', 'type': 'int', 'default': 'Empty'},
			],
			'return': 'Values',
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
			'return': 'Empty',
		}),
		('file_input.function_def', {
			'name': 'func3',
			'access': 'public',
			'decorators': [],
			'parameters': [
				{'name': 'ok', 'type': 'bool', 'default': 'Empty'},
			],
			'return': 'Empty',
		}),
	])
	def test_function(self, full_path: str, expected: dict[str, Any]) -> None:
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.Function)
		self.assertEqual(node.function_name.to_string(), expected['name'])
		self.assertEqual(node.access, expected['access'])
		self.assertEqual(len(node.decorators), len(expected['decorators']))
		for index, decorator in enumerate(node.decorators):
			in_expected = expected['decorators'][index]
			self.assertEqual(decorator.symbol.to_string(), in_expected['symbol'])
			self.assertEqual(len(decorator.arguments), len(in_expected['arguments']))
			for index_arg, argument in enumerate(decorator.arguments):
				in_arg_expected = in_expected['arguments'][index_arg]
				self.assertEqual(argument.value.to_string(), in_arg_expected['value'])

		self.assertEqual(len(node.parameters), len(expected['parameters']))
		for index, parameter in enumerate(node.parameters):
			in_expected = expected['parameters'][index]
			self.assertEqual(parameter.symbol.to_string(), in_expected['name'])
			self.assertEqual(parameter.var_type.to_string() if type(parameter.var_type) is defs.Symbol else 'Empty', in_expected['type'])
			self.assertEqual(parameter.default_value.to_string() if type(parameter.default_value) is defs.Terminal else 'Empty', in_expected['default'])

		self.assertEqual(node.return_type.to_string() if type(node.return_type) is defs.Symbol else 'Empty', expected['return'])
		self.assertEqual(type(node.block), defs.Block)

	@data_provider([
		('file_input.class_def[3]', {
			'name': 'Base',
			'decorators': [],
			'parents': [],
			'constructor': {},
			'methods': [],
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
					{'symbol': 'self.v', 'type': 'int'},
					{'symbol': 'self.s', 'type': 'str'},
				],
			},
			'methods': [
				{'name': 'func1'},
				{'name': '_func2'},
			],
		}),
	])
	def test_class(self, full_path: str, expected: dict[str, Any]) -> None:
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.Class)
		self.assertEqual(node.class_name.to_string(), expected['name'])
		self.assertEqual(len(node.decorators), len(expected['decorators']))
		for index, decorator in enumerate(node.decorators):
			in_expected = expected['decorators'][index]
			self.assertEqual(decorator.symbol.to_string(), in_expected['symbol'])
			for index_arg, argument in enumerate(decorator.arguments):
				in_arg_expected = in_expected['arguments'][index_arg]
				self.assertEqual(argument.value.to_string(), in_arg_expected['value'])

		self.assertEqual(len(node.parents), len(expected['parents']))
		for index, parent in enumerate(node.parents):
			in_expected = expected['parents'][index]
			self.assertEqual(parent.to_string(), in_expected['symbol'])

		self.assertEqual(node.constructor_exists, len(expected['constructor'].keys()) > 0)
		if node.constructor_exists:
			in_expected = expected['constructor']
			constructor = node.constructor
			self.assertEqual(type(constructor), defs.Constructor)
			self.assertEqual(len(constructor.decl_vars), len(in_expected['decl_vars']))
			for index, var in enumerate(constructor.decl_vars):
				in_var_expected = in_expected['decl_vars'][index]
				self.assertEqual(var.symbol.to_string(), in_var_expected['symbol'])
				self.assertEqual(var.var_type.to_string(), in_var_expected['type'])

		self.assertEqual(len(node.methods), len(expected['methods']))
		for index, constructor in enumerate(node.methods):
			in_expected = expected['methods'][index]
			self.assertEqual(type(constructor), defs.Method)
			self.assertEqual(constructor.function_name.to_string(), in_expected['name'])

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
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.Enum)
		self.assertEqual(node.enum_name.to_string(), expected['name'])
		self.assertEqual(len(node.vars), len(expected['vars']))
		for index, var in enumerate(node.vars):
			in_expected = expected['vars'][index]
			self.assertEqual(var.symbol.to_string(), in_expected['symbol'])
			self.assertEqual(var.value.to_string(), in_expected['value'])

	# Statement simple

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[0]', {
			'symbol': 'map',
			'var_type': defs.DictType,
			'value': defs.Expression,
		}),
	])
	def test_anno_assign(self, full_path: str, expected: dict[str, Any]) -> None:
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.AnnoAssign)
		self.assertEqual(node.symbol.to_string(), expected['symbol'])
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
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.AugAssign)
		self.assertEqual(type(node.symbol), expected['symbol'])
		self.assertEqual(node.operator.to_string(), expected['operator'])
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
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.Import)
		self.assertEqual(node.module_path.to_string(), expected['module_path'])
		self.assertEqual(len(node.import_symbols), len(expected['import_symbols']))
		for index, symbol in enumerate(node.import_symbols):
			in_expected = expected['import_symbols'][index]
			self.assertEqual(symbol.to_string(), in_expected['symbol'])

	# Primary

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[2].anno_assign.getitem', {
			'value_type': 'int',
		}),
	])
	def test_list_type(self, full_path: str, expected: dict[str, Any]) -> None:
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.ListType)
		self.assertEqual(node.value_type.to_string(), expected['value_type'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[0].anno_assign.getitem', {
			'key_type': 'Hoge.Values',
			'value_type': 'int',
		}),
	])
	def test_dict_type(self, full_path: str, expected: dict[str, Any]) -> None:
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.DictType)
		self.assertEqual(node.key_type.to_string(), expected['key_type'])
		self.assertEqual(node.value_type.to_string(), expected['value_type'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.getitem', {
			'symbol': 'arr',
			'key': '0',
		}),
	])
	def test_indexer(self, full_path: str, expected: dict[str, Any]) -> None:
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.Indexer)
		self.assertEqual(node.symbol.to_string(), expected['symbol'])
		self.assertEqual(node.key.to_string(), expected['key'])

	@data_provider([
		('file_input.funccall', {
			'caller': 'pragma',
			'arguments': [
				{'value': "'once'"},
			],
			'calculated': [
				'<Symbol: file_input.funccall.primary>',
				'<String: file_input.funccall.arguments.argvalue.primary>',
				'<Argument: file_input.funccall.arguments.argvalue>',
			],
		}),
	])
	def test_funccall(self, full_path: str, expected: dict[str, Any]) -> None:
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.FuncCall)
		self.assertEqual(node.calls.to_string(), expected['caller'])
		self.assertEqual(len(node.arguments), len(expected['arguments']))
		for index, argument in enumerate(node.arguments):
			in_expected = expected['arguments'][index]
			self.assertEqual(argument.value.to_string(), in_expected['value'])

		self.assertEqual([str(node) for node in node.calculated()], expected['calculated'])

	# Literal

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[2].anno_assign.primary[2].list', {
			'values': [
				{'value': '0', 'value_type': defs.Integer},
				{'value': '1', 'value_type': defs.Integer},
				{'value': '2', 'value_type': defs.Integer},
			],
		}),
	])
	def test_list(self, full_path: str, expected: dict[str, Any]) -> None:
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.List)
		self.assertEqual(len(node.values), len(expected['values']))
		for index, value in enumerate(node.values):
			in_expected = expected['values'][index]
			self.assertEqual(value.to_string(), in_expected['value'])
			self.assertEqual(type(value), in_expected['value_type'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[0].anno_assign.primary[2].dict', {
			'items': [
				{'key': 'Hoge.Values.A', 'value': '0', 'value_type': defs.Integer},
				{'key': 'Hoge.Values.B', 'value': '1', 'value_type': defs.Integer},
			],
		}),
	])
	def test_dict(self, full_path: str, expected: dict[str, Any]) -> None:
		nodes = Fixture.inst.nodes
		node = nodes.by(full_path).as_a(defs.Dict)
		self.assertEqual(len(node.items), len(expected['items']))
		for index, item in enumerate(node.items):
			in_expected = expected['items'][index]
			self.assertEqual(item.key.to_string(), in_expected['key'])
			self.assertEqual(item.value.to_string(), in_expected['value'])
			self.assertEqual(type(item.value), in_expected['value_type'])
