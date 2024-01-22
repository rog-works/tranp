import re
from typing import cast

from py2cpp.ast.dsn import DSN
from py2cpp.lang.implementation import implements, override
from py2cpp.lang.sequence import last_index_of
from py2cpp.node.definition.common import InheritArgument
from py2cpp.node.definition.element import Decorator, Parameter, ReturnDecl
from py2cpp.node.definition.literal import String
from py2cpp.node.definition.primary import BlockDeclVar, ClassDeclVar, Declable, GenericType, ParamThis, ThisDeclVar, Type
from py2cpp.node.definition.statement_simple import AnnoAssign, MoveAssign
from py2cpp.node.definition.terminal import Empty
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.interface import IDomainName, IScope
from py2cpp.node.node import Node, T_Node
from py2cpp.node.promise import IDeclare, StatementBlock


@Meta.embed(Node, accept_tags('block'))
class Block(Node, IScope):
	@property
	@implements
	def scope_part(self) -> str:
		"""Note: XXX 親が公開名称を持つノード(クラス/ファンクション)の場合は空文字。それ以外は親の一意エントリータグを返却"""
		return '' if self.parent.public_name else self.parent._full_path.elements[-1]

	@property
	@implements
	def namespace_part(self) -> str:
		return ''

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self._children()

	def decl_vars_with(self, allow: type[T_Node]) -> list['AnnoAssign | MoveAssign | For | Catch']:
		return list(collect_decl_vars(self, allow).values())


class Flow(Node): pass


@Meta.embed(Node, accept_tags('elif_'))
class ElseIf(Flow):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('if_stmt'))
class If(Flow):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	@Meta.embed(Node, expandable)
	def else_ifs(self) -> list[ElseIf]:
		return [node.as_a(ElseIf) for node in self._by('elifs')._children()]

	@property
	@Meta.embed(Node, expandable)
	def else_statements(self) -> list[Node]:
		block = self.else_block
		return block.statements if isinstance(block, Block) else []
	
	@property
	def block(self) -> Block:
		return self._at(1).as_a(Block)

	@property
	def else_block(self) -> Block | Empty:
		return self._at(3).one_of(Block | Empty)

	@property
	def having_blocks(self) -> list[Block]:
		blocks: list[Block] = [self.block]
		for else_if in self.else_ifs:
			blocks.append(else_if.block)

		if isinstance(self.else_block, Block):
			blocks.append(self.else_block)

		return blocks


@Meta.embed(Node, accept_tags('while_stmt'))
class While(Flow):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('for_stmt'))
class For(Flow, IDeclare):
	@property
	@implements
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		return self._by('name').as_a(Declable)

	@property
	@Meta.embed(Node, expandable)
	def iterates(self) -> Node:
		return self._at(1)

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('except_clause'))
class Catch(Flow, IDeclare):
	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Type:
		# XXX Pythonの仕様では複数の型を捕捉できるが一旦単数で実装
		return self._at(0).as_a(Type)

	@property
	@implements
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		# XXX Pythonの仕様では省略出来るが実装を簡単にするため必須で実装
		return self._by('name').one_of(Declable)

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('try_stmt'))
class Try(Flow):
	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	@Meta.embed(Node, expandable)
	def catches(self) -> list[Catch]:
		return [node.as_a(Catch) for node in self._by('except_clauses')._children()]

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)

	@property
	def having_blocks(self) -> list[Block]:
		return [self.block, *[catch.block for catch in self.catches]]


class ClassKind(Node, IDomainName, IScope, IDeclare):
	@property
	@override
	def public_name(self) -> str:
		return self.symbol.tokens

	@property
	@implements
	def scope_part(self) -> str:
		return self.public_name

	@property
	@implements
	def namespace_part(self) -> str:
		return ''

	@property
	@implements
	def domain_name(self) -> str:
		"""Note: XXX スコープ内に自身の名前が含まれるので空文字を返却"""
		return ''

	@property
	@implements
	def fullyname(self) -> str:
		return DSN.join(self.scope, self.domain_name)

	@property
	@implements
	def symbol(self) -> Declable:
		"""Note: XXX 宣言し直しているため、念のためインターフェイスを継承していることを明示"""
		raise NotImplementedError()

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
	def decorators(self) -> list[Decorator]:
		raise NotImplementedError()

	@property
	def statements(self) -> list[Node]:
		raise NotImplementedError()

	@property
	def block(self) -> Block:
		raise NotImplementedError()

	@property
	def generic_types(self) -> list[Type]:
		"""Note: XXX 未使用"""
		return []

	def _alias_symbol(self) -> str | None:
		"""デコレーターで設定した別名をシンボル名として取り込む

		Returns:
			str | None: 別名
		Examples:
			```python
			@__alias__('int')
			class Integer: ...
			```
		"""
		decorators = self.decorators
		if len(decorators) == 0:
			return None

		decorator = decorators[0]
		if not decorator.path.tokens.startswith('__alias__'):
			return None

		return decorator.arguments[0].value.as_a(String).plain


@Meta.embed(Node, accept_tags('function_def'))
class Function(ClassKind):
	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		symbol = self._by('function_def_raw.name').as_a(Declable)
		alias = self._alias_symbol()
		return symbol if not alias else symbol.dirty_proxify(tokens=alias).as_a(Declable)

	@property
	@override
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
	def return_decl(self) -> ReturnDecl:
		return self._by('function_def_raw.return_type').as_a(ReturnDecl)

	@property
	@override
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	@override
	def block(self) -> Block:
		return self._by('function_def_raw.block').as_a(Block)

	@property
	def decl_vars(self) -> list[Parameter | AnnoAssign | MoveAssign | For | Catch]:
		return [*self.parameters, *self.block.decl_vars_with(BlockDeclVar)]


@Meta.embed(Node, actualized(via=Function))
class ClassMethod(Function):
	@classmethod
	@override
	def match_feature(cls, via: Function) -> bool:
		decorators = via.decorators
		return len(decorators) > 0 and decorators[0].path.tokens == 'classmethod'

	@property
	def class_symbol(self) -> Declable:
		return self.parent.as_a(Block).parent.as_a(ClassKind).symbol


@Meta.embed(Node, actualized(via=Function))
class Constructor(Function):
	@classmethod
	@override
	def match_feature(cls, via: Function) -> bool:
		return via.symbol.tokens == '__init__'

	@property
	def class_symbol(self) -> Declable:
		return self.parent.as_a(Block).parent.as_a(ClassKind).symbol

	@property
	def this_vars(self) -> list[AnnoAssign]:
		return [node.as_a(AnnoAssign) for node in self.block.decl_vars_with(ThisDeclVar)]


@Meta.embed(Node, actualized(via=Function))
class Method(Function):
	@classmethod
	@override
	def match_feature(cls, via: Function) -> bool:
		if via.symbol.tokens == '__init__':
			return False

		parameters = via.parameters
		return len(parameters) > 0 and parameters[0].symbol.is_a(ParamThis)

	@property
	def class_symbol(self) -> Declable:
		return self.parent.as_a(Block).parent.as_a(ClassKind).symbol


@Meta.embed(Node, actualized(via=Function))
class Closure(Function):
	@classmethod
	@override
	def match_feature(cls, via: Function) -> bool:
		elems = via._full_path.de_identify().elements
		actual_function_def_at = last_index_of(elems, 'function_def_raw')
		expect_function_def_at = max(0, len(elems) - 3)
		in_decl_function = actual_function_def_at == expect_function_def_at
		return in_decl_function

	@property
	def binded_this(self) -> bool:
		found_own_class = 'class_def' in self._full_path.de_identify().elements
		if not found_own_class:
			return False

		types = self._ancestor('class_def').as_a(Class)
		own_method_at = len(types.block._full_path.elements) + 1
		own_method = self
		while own_method_at < len(own_method._full_path.elements):
			own_method = own_method.parent

		return own_method.is_a(Method)


@Meta.embed(Node, accept_tags('class_def'))
class Class(ClassKind):
	@property
	@override
	def namespace_part(self) -> str:
		return self.public_name

	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		symbol = self._by('class_def_raw.name').as_a(Declable)
		alias = self._alias_symbol()
		return symbol if not alias else symbol.dirty_proxify(tokens=alias).as_a(Declable)

	@property
	@override
	@Meta.embed(Node, expandable)
	def decorators(self) -> list[Decorator]:
		return [node.as_a(Decorator) for node in self._children('decorators')] if self._exists('decorators') else []

	@property
	@Meta.embed(Node, expandable)
	def parents(self) -> list[Type]:
		parents = self._by('class_def_raw')._at(1)
		if parents.is_a(Empty):
			return []

		return [node.as_a(InheritArgument).class_type.as_a(Type) for node in parents._children()]  # XXX as_a(Type)を消す

	@property
	@override
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	@override
	def block(self) -> Block:
		return self._by('class_def_raw.block').as_a(Block)

	@property
	@override
	def generic_types(self) -> list[Type]:
		"""Note: XXX 未使用"""
		generic_parent = [parent for parent in self.parents if isinstance(parent, GenericType)]
		return generic_parent[0].template_types if len(generic_parent) > 0 else []

	@property
	def constructor_exists(self) -> bool:
		candidates = [node.as_a(Constructor) for node in self.statements if node.is_a(Constructor)]
		return len(candidates) == 1

	@property
	def constructor(self) -> Constructor:
		return [node.as_a(Constructor) for node in self.statements if node.is_a(Constructor)].pop()

	@property
	def class_methods(self) -> list[ClassMethod]:
		return [node.as_a(ClassMethod) for node in self.statements if node.is_a(ClassMethod)]

	@property
	def methods(self) -> list[Method]:
		return [node.as_a(Method) for node in self.statements if node.is_a(Method)]

	@property
	def vars(self) -> list[AnnoAssign]:
		return [*self.class_vars, *self.instance_vars]

	@property
	def class_vars(self) -> list[AnnoAssign]:
		return [node.as_a(AnnoAssign) for node in self.block.decl_vars_with(ClassDeclVar)]

	@property
	def instance_vars(self) -> list[AnnoAssign]:
		return self.constructor.this_vars if self.constructor_exists else []


@Meta.embed(Node, accept_tags('enum_def'))
class Enum(ClassKind):
	@property
	@override
	def namespace_part(self) -> str:
		return self.public_name

	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		return self._by('name').as_a(Declable)

	@property
	@override
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	@override
	def block(self) -> Block:
		return self._by('block').as_a(Block)

	@property
	def vars(self) -> list[MoveAssign]:
		return [node.as_a(MoveAssign) for node in self.statements if node.is_a(MoveAssign)]


def collect_decl_vars(block: StatementBlock, allow: type[T_Node]) -> dict[str, AnnoAssign | MoveAssign | For | Catch]:
	decl_vars: dict[str, AnnoAssign | MoveAssign | For | Catch] = {}
	for node in block.statements:
		if isinstance(node, (AnnoAssign, MoveAssign)) and node.receiver.is_a(allow):
			var_name = node.receiver.tokens
			if var_name not in decl_vars:
				decl_vars[var_name] = node
		if isinstance(node, For) and node.symbol.is_a(allow):
			var_name = node.symbol.tokens
			if var_name not in decl_vars:
				decl_vars[var_name] = node
		elif isinstance(node, Try):
			for catch in node.catches:
				var_name = cast(Declable, catch.symbol).tokens
				if var_name not in decl_vars:
					decl_vars[var_name] = catch

		if isinstance(node, (If, Try)):
			for in_block in node.having_blocks:
				decl_vars = {**collect_decl_vars(in_block, allow), **decl_vars}
		elif isinstance(node, (While, For)):
			decl_vars = {**collect_decl_vars(node.block, allow), **decl_vars}

	return decl_vars
