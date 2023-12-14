import os
from typing import Any, Optional
from unittest import TestCase

from lark import Lark, Tree
from lark.indenter import PythonIndenter

from py2cpp.ast.travarsal import EntryPath
from py2cpp.lang.annotation import override
from py2cpp.node.embed import accept_tags, actualized, expansionable, Meta
from py2cpp.node.node import Node
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.node.provider import Settings
from py2cpp.node.trait import ScopeTrait
from tests.test.helper import data_provider


class Terminal(Node): pass


@Meta.embed(Node, accept_tags('__empty__', 'const_none'))
class Empty(Node): pass


@Meta.embed(Node, accept_tags('file_input'))
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
	@Meta.embed(Node, expansionable(order=0))
	def statements(self) -> list[Node]:
		return self._children()


@Meta.embed(Node, accept_tags('block'))
class Block(Node, ScopeTrait):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def statements(self) -> list[Node]:
		return self._children()


@Meta.embed(Node, accept_tags('if_stmt'))
class If(Node): pass


@Meta.embed(Node, accept_tags('dotted_name', 'getattr', 'primary', 'var', 'name', 'argvalue'))
class Symbol(Node):
	@override
	def to_string(self) -> str:
		return '.'.join([node.to_string() for node in self._flatten()])


@Meta.embed(Node, accept_tags('getattr'), actualized(via=Symbol))
class SelfSymbol(Symbol):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via.to_string() == 'self'


@Meta.embed(Node, accept_tags('paramvalue'))
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


class Expression(Node):
	@override
	def actualize(self) -> Node:
		if self.__feature_symbol():
			return self.as_a(Symbol)

		return super().actualize()


	def __feature_symbol(self) -> bool:
		if len(self._children()) != 1:
			return False

		rel_paths = [EntryPath(node.full_path).relativefy(self.full_path) for node in self._flatten()]
		for rel_path in rel_paths:
			if not rel_path.consists_of_only('getattr', 'primary', 'var', 'name', 'NAME'):
				return False

		return True


@Meta.embed(Node, accept_tags('argvalue'))
class Argument(Node):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def value(self) -> Node:
		return self.as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('assign_stmt'))
class Assign(Node):
	@property
	def _elements(self) -> list[Node]:
		return self._at(0)._children()


@Meta.embed(Node, accept_tags('assign_stmt'), actualized(via=Assign))
class MoveAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('assign')


	@property
	def symbol(self) -> Symbol:
		return self._elements[0].as_a(Symbol)


	@property
	def value(self) -> Node:
		return self._elements[1].as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('assign_stmt'), actualized(via=Assign))
class AnnoAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('anno_assign')


	@property
	def symbol(self) -> Symbol:
		return self._elements[0].as_a(Symbol)


	@property
	def variable_type(self) -> Symbol:
		return self._elements[1].as_a(Symbol)


	@property
	def value(self) -> Node:
		return self._elements[2].as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('assign_stmt'), actualized(via=Assign))
class AugAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('aug_assign')


	@property
	def symbol(self) -> Symbol:
		return self._elements[0].as_a(Symbol)


	@property
	def operator(self) -> Terminal:
		return self._elements[1].as_a(Terminal)


	@property
	def value(self) -> Node:
		return self._elements[2].as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('assign_stmt'))
class Variable(Node):
	@property
	def symbol(self) -> Symbol:
		return self._by('anno_assign')._at(0).as_a(Symbol)


	@property
	def variable_type(self) -> Symbol:
		return self._by('anno_assign')._at(1).as_a(Symbol)


@Meta.embed(Node, accept_tags('decorator'))
class Decorator(Node):
	@property
	def symbol(self) -> Symbol:
		return self._by('dotted_name').as_a(Symbol)


	@property
	@Meta.embed(Node, expansionable(order=0))
	def arguments(self) -> list[Argument]:
		return [node.as_a(Argument) for node in self._children('arguments')]


@Meta.embed(Node, accept_tags('function_def'))
class Function(Node):
	@property
	def access(self) -> str:
		name = self.function_name.to_string()
		if name.startswith('__'):
			return 'private'
		elif name.startswith('_'):
			return 'protected'
		else:
			return 'public'


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
	@Meta.embed(Node, expansionable(order=0))
	def block(self) -> Block:
		return self._by('function_def_raw.block').as_a(Block)


class Constructor(Function):
	@property
	def decl_variables(self) -> list[Variable]:
		assigns = [node.as_a(AnnoAssign) for node in self.block._children() if node.is_a(AnnoAssign)]
		variables = [node.as_a(Variable) for node in assigns if node.variable_type.is_a(SelfSymbol)]
		return list(set(variables))


class ClassMethod(Function): pass
class Method(Function): pass


@Meta.embed(Node, accept_tags('class_def'))
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


	@property
	def parents(self) -> list[Symbol]:
		parents = self._by('class_def_raw')._at(1)
		if parents.is_a(Empty):
			return []

		return [node.as_a(Symbol) for node in parents if node.is_a(Symbol)]  # FIXME


	@property
	def constructor_exists(self) -> bool:
		candidates = [node.as_a(Constructor) for node in self.block._children() if node.is_a(Constructor)]
		return len(candidates) == 1


	@property
	def constructor(self) -> Constructor:
		return [node.as_a(Constructor) for node in self.block._children() if node.is_a(Constructor)].pop()


	@property
	def class_methods(self) -> list[ClassMethod]:
		return [node.as_a(ClassMethod) for node in self.block._children() if node.is_a(ClassMethod)]


	@property
	def methods(self) -> list[Method]:
		return [node.as_a(Method) for node in self.block._children() if node.is_a(Method)]


	@property
	@Meta.embed(Node, expansionable(order=0))
	def block(self) -> Block:
		return self._by('class_def_raw.block').as_a(Block)


	@property
	def variables(self) -> list[Variable]:
		return self.constructor.decl_variables if self.constructor_exists else []


@Meta.embed(Node, accept_tags('enum_def'))
class Enum(Node):
	@property
	@override
	def scope_name(self) -> str:
		return self.enum_name.to_string()


	@property
	def enum_name(self) -> Terminal:
		return self._by('name').as_a(Terminal)


	@property
	@Meta.embed(Node, expansionable(order=0))
	def variables(self) -> list[MoveAssign]:
		return [child.as_a(MoveAssign) for child in self._leafs('assign_stmt')]


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
				'file_input': FileInput,
				'class_def': Class,
				'enum_def': Enum,
				'function_def': Function,
				'if_stmt': If,
				'assign_stmt': Assign,
				'block': Block,
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
		}),
	])
	def test_class(self, full_path: str, expected: dict[str, Any]) -> None:
		nodes = Fixture.inst.nodes()
		node = nodes.by(full_path).as_a(Class)
		self.assertEqual(node.class_name.to_string(), expected['name'])
		for index, decorator in enumerate(node.decorators):
			in_expected = expected['decorators'][index]
			self.assertEqual(decorator.symbol.to_string(), in_expected['symbol'])
			for index_arg, argument in enumerate(decorator.arguments):
				in_arg_expected = in_expected['arguments'][index_arg]
				self.assertEqual(argument.value.to_string(), in_arg_expected['value'])


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
