import os
from typing import Any, Optional
from unittest import TestCase

from lark import Lark, Tree
from lark.indenter import PythonIndenter

from py2cpp.node.definition import (
	Argument,
	Assign,
	Block,
	Class,
	Constructor,
	Decorator,
	Empty,
	Enum,
	FileInput,
	Function,
	If,
	Method,
	Parameter,
	Symbol,
	Terminal,
)
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.node.provider import Settings
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
		if self.__prebuild:
			self.__tree = self.__load_prebuild_tree()
		else:
			self.__tree = self.__parse_tree(self.__load_parser())


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
		from tests.unit.py2cpp.node.test_difinition_fixture import fixture

		return fixture()


	def resolver(self) -> NodeResolver:
		return NodeResolver.load(Settings(
			symbols={
				'argvalue': Argument,
				'assign_stmt': Assign,
				'block': Block,
				'class_def': Class,
				'decorator': Decorator,
				'enum_def': Enum,
				'file_input': FileInput,
				'function_def': Function,
				'if_stmt': If,
				'paramvalue': Parameter,
				'getattr': Symbol,
				'__empty__': Empty,
			},
			fallback=Terminal,
		))


	def nodes(self) -> Nodes:
		return Nodes(self.__tree, self.resolver())


class TestDefinition(TestCase):
	@data_provider([
		('file_input.class_def.class_def_raw.block.enum_def', {
			'name': 'Values',
			'variables': [
				{'symbol': 'A', 'value': '0'},
				{'symbol': 'B', 'value': '1'},
			],
		}),
	])
	def test_enum(self, full_path: str, expected: dict[str, Any]) -> None:
		nodes = Fixture.inst.nodes()
		node = nodes.by(full_path).as_a(Enum)
		self.assertEqual(node.enum_name.to_string(), expected['name'])
		for index, variable in enumerate(node.variables):
			in_expected = expected['variables'][index]
			self.assertEqual(variable.symbol.to_string(), in_expected['symbol'])
			self.assertEqual(variable.value.to_string(), in_expected['value'])


	@data_provider([
		('file_input.class_def', {
			'name': 'Hoge',
			'decorators': [
				{'symbol': 'deco', 'arguments': [{'value': 'A'}, {'value': 'A.B'}]},
			],
			'constructor': {
				'decl_variables': [
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
		nodes = Fixture.inst.nodes()
		node = nodes.by(full_path).as_a(Class)
		self.assertEqual(node.class_name.to_string(), expected['name'])
		self.assertEqual(len(node.decorators), len(expected['decorators']))
		for index, decorator in enumerate(node.decorators):
			in_expected = expected['decorators'][index]
			self.assertEqual(decorator.symbol.to_string(), in_expected['symbol'])
			for index_arg, argument in enumerate(decorator.arguments):
				in_arg_expected = in_expected['arguments'][index_arg]
				self.assertEqual(argument.value.to_string(), in_arg_expected['value'])

		if node.constructor_exists:
			in_expected = expected['constructor']
			constructor = node.constructor
			self.assertEqual(type(constructor), Constructor)
			self.assertEqual(len(constructor.decl_variables), len(in_expected['decl_variables']))
			for index, variable in enumerate(constructor.decl_variables):
				in_var_expected = in_expected['decl_variables'][index]
				self.assertEqual(variable.symbol.to_string(), in_var_expected['symbol'])
				self.assertEqual(variable.variable_type.to_string(), in_var_expected['type'])

		self.assertEqual(len(node.methods), len(expected['methods']))
		for index, constructor in enumerate(node.methods):
			in_expected = expected['methods'][index]
			self.assertEqual(type(constructor), Method)
			self.assertEqual(constructor.function_name.to_string(), in_expected['name'])


	@data_provider([
		('file_input.class_def.class_def_raw.block.function_def[1]', {
			'name': 'func1',
			'access': 'public',
			'decorators': [],
			'parameters': [
				{'name': 'self', 'type': 'Empty', 'default': 'Empty'},
				{'name': 'value', 'type': 'int', 'default': 'Empty'},
			],
			'return': 'Values',
		}),
		('file_input.class_def.class_def_raw.block.function_def[2]', {
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
		nodes = Fixture.inst.nodes()
		node = nodes.by(full_path).as_a(Function)
		self.assertEqual(node.function_name.to_string(), expected['name'])
		self.assertEqual(node.access, expected['access'])
		self.assertEqual(len(node.decorators), len(expected['decorators']))
		for index, decorator in enumerate(node.decorators):
			in_expected = expected['decorators'][index]
			self.assertEqual(decorator.symbol.to_string(), in_expected['symbol'])
			for index_arg, argument in enumerate(decorator.arguments):
				in_arg_expected = in_expected['arguments'][index_arg]
				self.assertEqual(argument.value.to_string(), in_arg_expected['value'])

		for index, parameter in enumerate(node.parameters):
			in_expected = expected['parameters'][index]
			self.assertEqual(parameter.param_symbol.to_string(), in_expected['name'])
			self.assertEqual(parameter.param_type.to_string() if type(parameter.param_type) is Symbol else 'Empty', in_expected['type'])
			self.assertEqual(parameter.default_value.to_string() if type(parameter.default_value) is Terminal else 'Empty', in_expected['default'])

		self.assertEqual(node.return_type.to_string() if type(node.return_type) is Symbol else 'Empty', expected['return'])
		self.assertEqual(type(node.block), Block)
