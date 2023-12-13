import os
from typing import Any, Optional
from unittest import TestCase

from lark import Lark, Tree
from lark.indenter import PythonIndenter

from py2cpp.lang.annotation import override
from py2cpp.node.embed import accept_tags, embed_meta, expansionable
from py2cpp.node.node import Node
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.node.provider import Settings
from py2cpp.node.trait import ScopeTrait
from tests.test.helper import data_provider


class Terminal(Node): pass
class Expression(Node): pass


@embed_meta(Node, accept_tags('__empty__', 'const_none'))
class Empty(Node): pass


@embed_meta(Node, accept_tags('file_input'))
class FileInput(Node):
	@property
	@override
	def scopr_name(self) -> str:
		return '__main__'


	@property
	@override
	def namespace(self) -> str:
		return '__main__'


	@property
	@override
	def scope(self) -> str:
		return '__main__'


	@property
	@embed_meta(Node, expansionable(order=0))
	def statements(self) -> list[Node]:
		return self._children()


@embed_meta(Node, accept_tags('block'))
class Block(Node, ScopeTrait):
	@property
	@embed_meta(Node, expansionable(order=0))
	def statements(self) -> list[Node]:
		return self._children()


@embed_meta(Node, accept_tags('if_stmt'))
class If(Node): pass


@embed_meta(Node, accept_tags('getattr', 'primary', 'name', 'dotted_name'))
class Symbol(Node): pass


@embed_meta(Node, accept_tags('paramevalue'))
class Parameter(Node):
	@property
	def param_symbol(self) -> Symbol:
		return self._by('typedparam.name').as_a(Symbol)


	@property
	def param_type(self) -> Symbol | Empty:
		return self._by('typedparam')._at(1).if_not_a_to_b(Empty, Symbol)


	@property
	def default_value(self) -> Terminal | Empty:
		return self._at(1).if_not_a_to_b(Empty, Terminal)


@embed_meta(Node, accept_tags('argvalue'))
class Argument(Node):
	@property
	@embed_meta(Node, expansionable(order=0))
	def value(self) -> Expression:
		return self.as_a(Expression)


@embed_meta(Node, accept_tags('assign_stmt'))
class Assign(Node):
	@property
	def symbol(self) -> Symbol:
		return self._by('assign')._at(0).as_a(Symbol)


	@property
	def value(self) -> Terminal:  # FIXME Expression?
		return self._by('assign')._at(1).as_a(Terminal)


@embed_meta(Node, accept_tags('decorator'))
class Decorator(Node):
	@property
	def symbol(self) -> Symbol:
		return self._by('dotted_name').as_a(Symbol)


	@property
	@embed_meta(Node, expansionable(order=0))
	def arguments(self) -> list[Argument]:
		return [node.as_a(Argument) for node in self._children('arguments')]


@embed_meta(Node, accept_tags('function_def'))
class Function(Node):
	@property
	def function_name(self) -> Terminal:
		return self._by('function_def_raw.name').as_a(Terminal)


	@property
	def decorators(self) -> list[Decorator]:
		return [node.as_a(Decorator) for node in self._children('decorators')] if self._exists('decorators') else []


	@property
	def parameters(self) -> list[Parameter]:
		return [node.as_a(Parameter) for node in self._children('function_def_raw.parameters')]


	@property
	def return_type(self) -> Symbol | Empty:
		node = self._by('function_def_raw')._at(2)
		return node._by('const_none').as_a(Empty) if node._exists('const_none') else node.as_a(Symbol)


	@property
	@embed_meta(Node, expansionable(order=0))
	def block(self) -> Block:
		return self._by('function_def_raw.block').as_a(Block)


# class Constructor(Node, ScopeTrait): pass
# class Method(Node, ScopeTrait): pass
# class ClassMethod(Node, ScopeTrait): pass


@embed_meta(Node, accept_tags('class_def'))
class Class(Node):
	@property
	@override
	def scope_name(self) -> str:
		return self.class_name.to_string()


	@property
	def class_name(self) -> Terminal:
		return self._by('class_def_raw.name').as_a(Terminal)


	@property
	def decorators(self) -> list[Decorator]:
		return [node.as_a(Decorator) for node in self._children('decorators')] if self._exists('decorators') else []


	# @property
	# def constructor_exists(self) -> bool:
	# 	candidates = [node.as_a(Constructor) for node in self._leafs('class_raw.block.function') if node.is_a(Constructor)]
	# 	return len(candidates) == 1


	# @property
	# def constructor(self) -> Constructor:
	# 	return [node.as_a(Constructor) for node in self._leafs('class_raw.block.function') if node.is_a(Constructor)].pop()


	# @property
	# def methods(self) -> list[Method]:
	# 	return [node.as_a(Method) for node in self._leafs('class_raw.block.function') if node.is_a(Method)]


	@property
	@embed_meta(Node, expansionable(order=0))
	def block(self) -> Block:
		return self._by('class_def_raw.block').as_a(Block)


@embed_meta(Node, accept_tags('enum_def'))
class Enum(Node):
	@property
	@override
	def scope_name(self) -> str:
		return self.enum_name.to_string()


	@property
	def enum_name(self) -> Terminal:
		return self._by('name').as_a(Terminal)


	@property
	@embed_meta(Node, expansionable(order=0))
	def variables(self) -> list[Assign]:
		return [child.as_a(Assign) for child in self._leafs('assign_stmt')]


class Fixture:
	__inst: Optional['Fixture'] = None


	@classmethod
	@property
	def inst(cls) -> 'Fixture':
		if cls.__inst is None:
			cls.__inst = cls()

		return cls.__inst


	def __init__(self) -> None:
		# self.__tree = self.__parse_tree(self.__load_parser())
		self.__tree = self.__load_prebuild_tree()


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
				FileInput: 'file_input',
				Class: 'class_def',
				Enum: 'enum_def',
				Function: 'function_def',
				If: 'if_stmt',
				Assign: 'assign_stmt',
				Block: 'block',
				Parameter: 'paramvalue',
				Empty: '__empty__',
			},
			fallback=Terminal,
		))


	def nodes(self) -> Nodes:
		return Nodes(self.__tree, self.resolver())


class TestDefinition(TestCase):
	def test_enum(self) -> None:
		nodes = Fixture.inst.nodes()
		node = nodes.by('file_input').as_a(FileInput) \
			.statements[1].as_a(Class).block \
			.statements[0].as_a(Enum)
		self.assertEqual(node.enum_name.to_string(), 'Values')
		self.assertEqual(node.variables[0].symbol.to_string(), 'A')
		self.assertEqual(node.variables[0].value.to_string(), '0')
		self.assertEqual(node.variables[1].symbol.to_string(), 'B')
		self.assertEqual(node.variables[1].value.to_string(), '1')


	def test_class(self) -> None:
		nodes = Fixture.inst.nodes()
		node = nodes.by('file_input').as_a(FileInput) \
			.statements[1].as_a(Class)
		self.assertEqual(node.class_name.to_string(), 'Hoge')
		self.assertEqual(node.decorators[0].symbol.to_string(), 'deco')
		self.assertEqual(node.decorators[0].arguments[0].value.is_a(Expression), True)
		self.assertEqual(node.decorators[0].arguments[1].value.is_a(Expression), True)
		self.assertEqual(node.decorators[0].namespace, '__main__')


	@data_provider([
		('file_input.class_def.class_def_raw.block.function_def[1]', {
			'name': 'func1',
			'decorators': [],
			'parameters': [
				{'name': 'self', 'type': 'Empty', 'default': 'Empty'},
				{'name': 'value', 'type': 'int', 'default': 'Empty'},
			],
			'return': 'Values',
		}),
		('file_input.function_def', {
			'name': 'func3',
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
		self.assertEqual(len(node.decorators), len(expected['decorators']))
		for index, decorator in enumerate(node.decorators):
			in_expected = expected['decorators'][index]
			self.assertEqual(decorator.symbol.to_string(), in_expected['name'])
			for argument in decorator.arguments:
				self.assertEqual(argument.value.is_a(Expression), True)

		for index, parameter in enumerate(node.parameters):
			in_expected = expected['parameters'][index]
			self.assertEqual(parameter.param_symbol.to_string(), in_expected['name'])
			self.assertEqual(parameter.param_type.to_string() if type(parameter.param_type) is Symbol else 'Empty', in_expected['type'])
			self.assertEqual(parameter.default_value.to_string() if type(parameter.default_value) is Terminal else 'Empty', in_expected['default'])

		self.assertEqual(node.return_type.to_string() if type(node.return_type) is Symbol else 'Empty', expected['return'])
		self.assertEqual(type(node.block), Block)
