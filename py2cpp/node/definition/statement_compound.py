import re

from py2cpp.lang.annotation import override
from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.element import Block, Decorator, Parameter, Var
from py2cpp.node.definition.literal import Null
from py2cpp.node.definition.primary import GenericType, This, Symbol
from py2cpp.node.definition.statement_simple import MoveAssign
from py2cpp.node.definition.terminal import Empty
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('elif_'))
class ElseIf(Node):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('if_stmt'))
class If(Node):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._at(1).as_a(Block)

	@property
	@Meta.embed(Node, expandable)
	def else_ifs(self) -> list[ElseIf]:
		return [node.as_a(ElseIf) for node in self._by('elifs')._children()]

	@property
	@Meta.embed(Node, expandable)
	def else_block(self) -> Block | Empty:
		return self._at(3).one_of(Block | Empty)


@Meta.embed(Node, accept_tags('while_stmt'))
class While(Node):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('for_stmt'))
class For(Node):
	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:
		return self._by('name').as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	def iterates(self) -> Node:
		return self._at(1)

	@property
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('except_clause'))
class Catch(Node):
	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:
		return self._by('primary').as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	def alias(self) -> Symbol | Empty:
		return self._at(1).one_of(Symbol | Empty)

	@property
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('try_stmt'))
class Try(Node):
	@property
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._by('block').as_a(Block)

	@property
	@Meta.embed(Node, expandable)
	def catches(self) -> list[Catch]:
		return [node.as_a(Catch) for node in self._by('except_clauses')._children()]


class Types(Node):
	@property
	def block(self) -> Block:
		...


@Meta.embed(Node, accept_tags('function_def'))
class Function(Types):
	@property
	def access(self) -> str:
		name = self.symbol.to_string()
		# XXX 定数化などが必要
		if re.fullmatch(r'__.+__', name):
			return 'public'
		elif name.startswith('__'):
			return 'private'
		elif name.startswith('_'):
			return 'protected'
		else:
			return 'public'

	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:
		return self._by('function_def_raw.name').as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	def decorators(self) -> list[Decorator]:
		return [node.as_a(Decorator) for node in self._children('decorators')] if self._exists('decorators') else []

	@property
	@Meta.embed(Node, expandable)
	def parameters(self) -> list[Parameter]:
		return [node.as_a(Parameter) for node in self._children('function_def_raw.parameters')]

	@property
	@Meta.embed(Node, expandable)
	def return_type(self) -> Symbol | GenericType | Null:
		return self._by('function_def_raw')._at(2).one_of(Symbol | GenericType | Null)

	@property
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._by('function_def_raw.block').as_a(Block)


@Meta.embed(Node, actualized(via=Function))
class Constructor(Function):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via.as_a(Function).symbol.to_string() == '__init__'

	@property
	def class_symbol(self) -> Symbol:
		return self.parent.as_a(Block).parent.as_a(Class).symbol  # FIXME 循環参照

	@property
	def decl_vars(self) -> list[Var]:
		return [node for node in self.block.decl_vars if node.symbol.is_a(This)]


@Meta.embed(Node, actualized(via=Function))
class ClassMethod(Function):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		decorators = via.as_a(Function).decorators
		return len(decorators) > 0 and decorators[0].symbol.to_string() == 'classmethod'

	@property
	def class_symbol(self) -> Symbol:
		return self.parent.as_a(Block).parent.as_a(Class).symbol  # FIXME 循環参照


@Meta.embed(Node, actualized(via=Function))
class Method(Function):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# XXX コンストラクターを除外
		if via.as_a(Function).symbol.to_string() == '__init__':
			return False

		parameters = via.as_a(Function).parameters
		return len(parameters) > 0 and parameters[0].symbol.is_a(This)  # XXX Thisだけの判定だと不正確かも

	@property
	def class_symbol(self) -> Symbol:
		return self.parent.as_a(Block).parent.as_a(Class).symbol  # FIXME 循環参照


@Meta.embed(Node, accept_tags('class_def'))
class Class(Types):
	@property
	@override
	def scope_name(self) -> str:
		return self.symbol.to_string()

	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:
		return self._by('class_def_raw.name').as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	def decorators(self) -> list[Decorator]:
		return [node.as_a(Decorator) for node in self._children('decorators')] if self._exists('decorators') else []

	@property
	@Meta.embed(Node, expandable)
	def parents(self) -> list[Symbol]:
		parents = self._by('class_def_raw')._at(1)
		if parents.is_a(Empty):
			return []

		return [node.as_a(Argument).value.as_a(Symbol) for node in parents._children()]

	@property
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._by('class_def_raw.block').as_a(Block)

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
	def vars(self) -> list[Var]:
		return self.constructor.decl_vars if self.constructor_exists else []


@Meta.embed(Node, accept_tags('enum_def'))
class Enum(Types):
	@property
	@override
	def scope_name(self) -> str:
		return self.symbol.to_string()

	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:
		return self._by('name').as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._by('block').as_a(Block)

	@property
	def vars(self) -> list[MoveAssign]:  # XXX 理想としてはVarだが、Enumの変数に型の定義がないため一旦MoveAssignで妥協
		return [node.as_a(MoveAssign) for node in self._children('block')]
