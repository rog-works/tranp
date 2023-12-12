import os
from typing import Optional
from unittest import TestCase

from lark import Lark, Tree
from lark.indenter import PythonIndenter

from py2cpp.lang.annotation import override
from py2cpp.node.embed import embed_meta, expansionable
from py2cpp.node.node import Node
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.node.provider import Settings
from py2cpp.node.trait import ScopeTrait


class Empty(Node): pass


class Terminal(Node):
	@property
	def value(self) -> str:
		return ''.join([node.token for node in [self, *self.flatten()] if type(node) is Terminal])


class Block(Node, ScopeTrait): pass
class If(Node): pass


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


class Symbol(Node):
	@property
	def symbol_name(self) -> str:
		return '.'.join([node.value for node in self.flatten() if type(node) is Terminal])


class Assign(Node):
	@property
	def symbol(self) -> Symbol:
		return self._at(0).as_a(Symbol)


	@property
	def value(self) -> Terminal:
		return self._at(1).as_a(Terminal)


class Decorator(Node):
	@property
	def symbol(self) -> Symbol:
		return self._by('dotted_name').as_a(Symbol)


	@property
	@embed_meta(Node, expansionable(order=0))
	def arguments(self) -> list[Symbol]:
		return [node.as_a(Symbol) for node in self._children('arguments')]


class Function(Node):
	@property
	def function_name(self) -> Terminal:
		return self._by('function_def_raw.name').as_a(Terminal)


	@property
	@embed_meta(Node, expansionable(order=0))
	def decorators(self) -> list[Decorator]:
		return [node.as_a(Decorator) for node in self._children('decorators')] if self._exists('decorators') else []


	# @property
	# def parameters(self) -> list[Symbol]:
	# 	return [node.as_a(Symbol) for node in self._leafs('primary')]


# class Constructor(Node, ScopeTrait): pass
# class Method(Node, ScopeTrait): pass
# class ClassMethod(Node, ScopeTrait): pass


class Class(Node):
	@property
	@override
	def scope_name(self) -> str:
		return self.class_name.value


	@property
	def class_name(self) -> Terminal:
		return self._by('class_def_raw.name').as_a(Terminal)


	@property
	@embed_meta(Node, expansionable(order=0))
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


class Enum(Node):
	@property
	@override
	def scope_name(self) -> str:
		return self.enum_name.value


	@property
	def enum_name(self) -> Terminal:
		return self._by('name').as_a(Terminal)


	@property
	@embed_meta(Node, expansionable(order=0))
	def variables(self) -> list[Assign]:
		return [child.as_a(Assign) for child in self._children('block')]


class Fixture:
	__inst: Optional['Fixture'] = None


	@classmethod
	@property
	def inst(cls) -> 'Fixture':
		if cls.__inst is None:
			cls.__inst = cls()

		return cls.__inst


	def __init__(self) -> None:
		self.__tree = self.__parse_tree(self.__load_parser())


	def __load_parser(self) -> Lark:
		dir = os.path.join(os.path.dirname(__file__), '../../../../')
		with open(os.path.join(dir, 'data/grammar.lark')) as f:
			return Lark(f, start='file_input', postlex=PythonIndenter(), parser='lalr')


	def __parse_tree(self, parser: Lark) -> Tree:
		filepath, _ = __file__.split('.')
		fixture_path = f'{filepath}.fixture.py'
		with open(fixture_path) as f:
			source = '\n'.join(f.readlines())
			return parser.parse(source)


	def resolver(self) -> NodeResolver:
		return NodeResolver.load(Settings(
			symbols={
				FileInput: 'file_input',
				Class: 'class_def',
				Enum: 'enum_def',
				Function: 'function_def',
				If: 'if_stmt',
				Assign: 'assign',
				Block: 'block',
				Empty: '__empty__',
			},
			fallback=Terminal,
		))


	def nodes(self) -> Nodes:
		return Nodes(self.__tree, self.resolver())


	def dump(self) -> None:
		print(self.__tree.pretty())


class TestDefinitionEnum(TestCase):
	def test_schema(self) -> None:
		nodes = Fixture.inst.nodes()
		node = nodes.by('file_input.class_def.class_def_raw.block.enum_def').as_a(Enum)
		self.assertEqual(node.enum_name.value, 'Values')
		self.assertEqual(node.variables[0].symbol.symbol_name, 'A')
		self.assertEqual(node.variables[0].value.value, '0')
		self.assertEqual(node.variables[1].symbol.symbol_name, 'B')
		self.assertEqual(node.variables[1].value.value, '1')


class TestDefinitionClass(TestCase):
	def test_schema(self) -> None:
		nodes = Fixture.inst.nodes()
		node = nodes.by('file_input.class_def').as_a(Class)
		self.assertEqual(node.class_name.value, 'Hoge')
		self.assertEqual(node.decorators[0].symbol.symbol_name, 'deco')
		self.assertEqual(node.decorators[0].arguments[0].symbol_name, 'A')
		self.assertEqual(node.decorators[0].arguments[1].symbol_name, 'A.B')
		self.assertEqual(node.decorators[0].namespace, '__main__')


class TestDefinitionFunction(TestCase):
	def test_schema(self) -> None:
		nodes = Fixture.inst.nodes()
		node = nodes.by('file_input.function_def').as_a(Function)
		self.assertEqual(node.function_name.value, 'func3')
		self.assertEqual(node.decorators, [])
