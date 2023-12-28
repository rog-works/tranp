import re

from py2cpp.ast.dns import domainize
from py2cpp.lang.annotation import override
from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.element import Block, Decorator, Parameter, ReturnType
from py2cpp.node.definition.primary import Symbol, This, ThisVar, Var
from py2cpp.node.definition.statement_simple import AnnoAssign, MoveAssign
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
	def domain_id(self) -> str:
		return domainize(self.scope, self.symbol.tokens)

	@property
	def domain_name(self) -> str:
		return domainize(self.module.path, self.symbol.tokens)

	@property
	def symbol(self) -> Symbol:
		raise NotImplementedError()

	@property
	def block(self) -> Block:
		raise NotImplementedError()


@Meta.embed(Node, accept_tags('function_def'))
class Function(Types):
	@property
	def access(self) -> str:
		name = self.symbol.tokens
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
	@override
	def name(self) -> str:
		return self.symbol.tokens

	@property
	@override
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
		if not self._exists('function_def_raw.parameters'):
			return []

		return [node.as_a(Parameter) for node in self._children('function_def_raw.parameters')]

	@property
	@Meta.embed(Node, expandable)
	def return_type(self) -> ReturnType:
		return self._by('function_def_raw.return_type').as_a(ReturnType)

	@property
	@override
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._by('function_def_raw.block').as_a(Block)

	@property
	def decl_vars(self) -> list[Parameter | AnnoAssign | MoveAssign]:
		return [*self.parameters, *self.block.decl_vars_with(Var)]


@Meta.embed(Node, actualized(via=Function))
class ClassMethod(Function):
	@classmethod
	@override
	def match_feature(cls, via: Function) -> bool:
		decorators = via.decorators
		return len(decorators) > 0 and decorators[0].symbol.tokens == 'classmethod'

	@property
	def class_symbol(self) -> Symbol:
		return self.parent.as_a(Block).parent.as_a(Types).symbol


@Meta.embed(Node, actualized(via=Function))
class Constructor(Function):
	@classmethod
	@override
	def match_feature(cls, via: Function) -> bool:
		return via.symbol.tokens == '__init__'

	@property
	def class_symbol(self) -> Symbol:
		return self.parent.as_a(Block).parent.as_a(Types).symbol

	@property
	def this_vars(self) -> list[AnnoAssign | MoveAssign]:
		return self.block.decl_vars_with(ThisVar)


@Meta.embed(Node, actualized(via=Function))
class Method(Function):
	@classmethod
	@override
	def match_feature(cls, via: Function) -> bool:
		# XXX コンストラクターを除外
		if via.symbol.tokens == '__init__':
			return False

		# XXX Thisのみの判定だと不正確かもしれない
		parameters = via.parameters
		return len(parameters) > 0 and parameters[0].symbol.is_a(This)

	@property
	def class_symbol(self) -> Symbol:
		return self.parent.as_a(Block).parent.as_a(Types).symbol


@Meta.embed(Node, accept_tags('class_def'))
class Class(Types):
	@property
	@override
	def name(self) -> str:
		return self.symbol.tokens

	@property
	@override
	def scope_name(self) -> str:
		return self.name

	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:
		return self.__alias_symbol or self._by('class_def_raw.name').as_a(Symbol)

	@property
	def __alias_symbol(self) -> Symbol | None:
		"""Symbol: 特定の書式のデコレーターで設定した別名をクラス名のシンボルとして取り込む @node: 書式: `@__alias__.${alias_symbol}`。標準ライブラリの実装にのみ使う想定"""
		decorators = self.decorators
		if len(decorators) == 0:
			return None

		decorator = decorators[0]
		if not decorator.symbol.tokens.startswith('__alias__'):
			return None

		return decorator.symbol._by('name[1]').as_a(Symbol)

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
	@override
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
	def vars(self) -> list[AnnoAssign | MoveAssign]:
		return [*self.class_vars, *self.instance_vars]

	@property
	def class_vars(self) -> list[AnnoAssign | MoveAssign]:
		return self.block.decl_vars_with(Var)

	@property
	def instance_vars(self) -> list[AnnoAssign | MoveAssign]:
		return self.constructor.this_vars if self.constructor_exists else []


@Meta.embed(Node, accept_tags('enum_def'))
class Enum(Types):
	@property
	@override
	def name(self) -> str:
		return self.symbol.tokens

	@property
	@override
	def scope_name(self) -> str:
		return self.name

	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:
		return self._by('name').as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	@override
	def block(self) -> Block:
		return self._by('block').as_a(Block)

	@property
	def vars(self) -> list[AnnoAssign | MoveAssign]:
		return [node.one_of(AnnoAssign | MoveAssign) for node in self.block._children() if node.is_a(AnnoAssign, MoveAssign)]
