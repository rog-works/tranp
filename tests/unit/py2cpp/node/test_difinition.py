from unittest import TestCase

from lark import Token, Tree

from py2cpp.lang.annotation import override
from py2cpp.node.embed import embed_meta, expansionable
from py2cpp.node.node import Node
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.node.provider import Settings
from py2cpp.node.trait import ScopeTrait
from tests.test.helper import data_provider


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
		return '__main__'  # XXX ファイル名の方が良いのでは


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
		return self._at('primary[0]').as_a(Symbol)


	@property
	def value(self) -> Terminal:
		return self._at('primary[1]').as_a(Terminal)


class Decorator(Node):
	@property
	def symbol(self) -> Symbol:
		return self._at('dotted_name').as_a(Symbol)


	@property
	@embed_meta(Node, expansionable(order=0))
	def arguments(self) -> list[Symbol]:
		return [node.as_a(Symbol) for node in self._leafs('primary')]


class Function(Node):
	@property
	def function_name(self) -> Terminal:
		return self._at('function_def_raw.name').as_a(Terminal)


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
		return self._at('class_def_raw.name').as_a(Terminal)


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
		return self._at('name').as_a(Terminal)


	@property
	@embed_meta(Node, expansionable(order=0))
	def variables(self) -> list[Assign]:
		return [child.as_a(Assign) for child in self._children('block')]


class Fixture:
	@classmethod
	def tree(cls) -> Tree:
		return Tree('file_input', [
			Tree('class_def', [
				Tree('decorators', [
					Tree('decorator', [Tree('dotted_name', [Token('name', 'deco')]),
						Tree('primary', [Token('name', 'A')]),
						Tree('primary', [Tree('primary', [Token('name', 'A')]), Token('name', 'B')]),
					]),
				]),
				Tree('class_def_raw', [Token('name', 'Hoge'), Tree('block', [
					Tree('enum_def', [Token('name', 'Values'), Tree('block', [
						Tree('assign', [
							Tree('primary', [Token('name', 'A')]),
							Tree('primary', [Token('number', '0')]),
						]),
						Tree('assign', [
							Tree('primary', [Token('name', 'B')]),
							Tree('primary', [Token('number', '1')]),
						]),
					])]),
					Tree('function_def', [
						None,
						Tree('function_def_raw', [Token('name', 'func1'), Tree('block', [
							Tree('if', [Tree('block', [
								Token('term_a', ''),
							])]),
						])]),
					]),
					Tree('function_def', [
						None,
						Tree('function_def_raw', [Token('name', 'func2'), Tree('block', [
							Tree('if_stmt', [Tree('block', [
								Token('term_a', ''),
							])]),
						])]),
					]),
				]),
			])]),
			Tree('function_def', [
				None,
				Tree('function_def_raw', [Token('name', 'func3'), Tree('block', [
					Tree('if_stmt', [Tree('block', [
						Token('term_a', ''),
					])]),
				])]),
			]),
		])


	@classmethod
	def resolver(cls) -> NodeResolver:
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


	@classmethod
	def nodes(cls) -> Nodes:
		return Nodes(cls.tree(), cls.resolver())


class TestDefinitionEnum(TestCase):
	def test_schema(self) -> None:
		nodes = Fixture.nodes()
		node = nodes.at('file_input.class_def.class_def_raw.block.enum_def').as_a(Enum)
		self.assertEqual(node.enum_name.value, 'Values')
		self.assertEqual(node.variables[0].symbol.symbol_name, 'A')
		self.assertEqual(node.variables[0].value.value, '0')
		self.assertEqual(node.variables[1].symbol.symbol_name, 'B')
		self.assertEqual(node.variables[1].value.value, '1')


class TestDefinitionClass(TestCase):
	def test_schema(self) -> None:
		nodes = Fixture.nodes()
		node = nodes.at('file_input.class_def').as_a(Class)
		self.assertEqual(node.class_name.value, 'Hoge')
		self.assertEqual(node.decorators[0].symbol.symbol_name, 'deco')
		self.assertEqual(node.decorators[0].arguments[0].symbol_name, 'A')
		self.assertEqual(node.decorators[0].arguments[1].symbol_name, 'A.B')
		self.assertEqual(node.decorators[0].namespace, '__main__')


class TestDefinitionFunction(TestCase):
	def test_schema(self) -> None:
		nodes = Fixture.nodes()
		node = nodes.at('file_input.function_def').as_a(Function)
		self.assertEqual(node.function_name.value, 'func3')
		self.assertEqual(node.decorators, [])
