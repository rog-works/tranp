from typing import Generic, TypeVar, override

from rogw.tranp.compatible.python.embed import Embed, __actual__
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.lang.annotation import duck_typed, implements
from rogw.tranp.lang.sequence import flatten, last_index_of
from rogw.tranp.syntax.node.accessible import ClassOperations
from rogw.tranp.syntax.node.behavior import IDomain, INamespace, IScope
from rogw.tranp.syntax.node.definition.accessible import PythonClassOperations, to_accessor
from rogw.tranp.syntax.node.definition.element import Decorator, Parameter
from rogw.tranp.syntax.node.definition.literal import Boolean, DocString, String
from rogw.tranp.syntax.node.definition.primary import DeclClassVar, DeclLocalVar, DeclThisVarForward, Declable, ForIn, GenericType, InheritArgument, DeclThisParam, DeclThisVar, Type, TypesName, VarOfType
from rogw.tranp.syntax.node.definition.statement_simple import AnnoAssign, MoveAssign
from rogw.tranp.syntax.node.definition.terminal import Empty
from rogw.tranp.syntax.node.embed import Meta, accept_tags, expandable
from rogw.tranp.syntax.node.interface import IDeclaration, ISymbol, StatementBlock
from rogw.tranp.syntax.node.node import Node

T_Declable = TypeVar('T_Declable', bound=Declable)


@Meta.embed(Node, accept_tags('block'))
class Block(Node):
	@property
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self._children()


class Flow(Node, IDomain, IScope):
	@property
	@override
	def domain_name(self) -> str:
		# XXX 一意な名称を持たないためIDで代用
		return ModuleDSN.identify(self.classification, self.id)


class FlowEnter(Flow): pass
class FlowPart(Flow): pass


@Meta.embed(Node, accept_tags('if_clause'))
class IfClause(FlowPart):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(0)

	@property
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('elif_clause'))
class ElseIf(IfClause): pass


@Meta.embed(Node, accept_tags('else_clause'))
class Else(FlowPart):
	@property
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('if_stmt'))
class If(FlowEnter):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self.if_clause.condition

	@property
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	@Meta.embed(Node, expandable)
	def else_ifs(self) -> list[ElseIf]:
		return [node.as_a(ElseIf) for node in self._by('elif_clauses')._children()]

	@property
	@Meta.embed(Node, expandable)
	def else_clause(self) -> Else | Empty:
		return self._at(2).one_of(Else, Empty)

	@property
	def if_clause(self) -> IfClause:
		return self._by('if_clause').as_a(IfClause)
	
	@property
	def block(self) -> Block:
		return self.if_clause.block

	@property
	def having_blocks(self) -> list[Block]:
		blocks: list[Block] = [self.block]
		for else_if in self.else_ifs:
			blocks.append(else_if.block)

		if isinstance(self.else_clause, Else):
			blocks.append(self.else_clause.block)

		return blocks


@Meta.embed(Node, accept_tags('while_stmt'))
class While(FlowEnter):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(0)

	@property
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('for_stmt'))
class For(FlowEnter, IDeclaration):
	@property
	@implements
	@Meta.embed(Node, expandable)
	def symbols(self) -> list[Declable]:
		return [node.as_a(Declable) for node in self._children('for_namelist')]

	@property
	@Meta.embed(Node, expandable)
	def for_in(self) -> ForIn:
		return self._by('for_in').as_a(ForIn)

	@property
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def iterates(self) -> Node:
		return self.for_in.iterates

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('except_clause'))
class Catch(FlowPart, IDeclaration):
	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Type:
		"""Note: XXX Pythonの仕様では複数の型を捕捉できるが一旦単数で実装"""
		return self._at(0).as_a(Type)

	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> DeclLocalVar:
		"""Note: XXX Pythonの仕様では省略出来るが実装を簡単にするため必須で実装"""
		return self._by('name').as_a(DeclLocalVar)

	@property
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	@implements
	def symbols(self) -> list[Declable]:
		return [self.symbol]

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('try_clause'))
class TryClause(FlowPart):
	@property
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('try_stmt'))
class Try(FlowEnter):
	@property
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	@Meta.embed(Node, expandable)
	def catches(self) -> list[Catch]:
		return [node.as_a(Catch) for node in self._by('except_clauses')._children()]

	@property
	def try_clause(self) -> TryClause:
		return self._by('try_clause').as_a(TryClause)

	@property
	def block(self) -> Block:
		return self.try_clause.block

	@property
	def having_blocks(self) -> list[Block]:
		return [self.block, *[catch.block for catch in self.catches]]


@Meta.embed(Node, accept_tags('with_item'))
class WithEntry(Node, IDeclaration):
	@property
	@Meta.embed(Node, expandable)
	def enter(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> DeclLocalVar:
		"""Note: XXX Pythonの仕様では省略出来るが実装を簡単にするため必須で実装"""
		return self._by('name').as_a(DeclLocalVar)

	@property
	@implements
	def symbols(self) -> list[Declable]:
		return [self.symbol]


@Meta.embed(Node, accept_tags('with_stmt'))
class With(FlowEnter):
	@property
	@Meta.embed(Node, expandable)
	def entries(self) -> list[WithEntry]:
		return [node.as_a(WithEntry) for node in self._by('with_items')._children()]

	@property
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


class ClassDef(Node, IDomain, IScope, INamespace, IDeclaration, ISymbol):
	@property
	@override
	def domain_name(self) -> str:
		return self.symbol.tokens

	@property
	@implements
	def symbols(self) -> list[Declable]:
		return [self.symbol]

	@property
	@implements
	def symbol(self) -> TypesName:
		raise NotImplementedError()

	@property
	@implements
	def declare(self) -> 'ClassDef':
		return self

	@property
	def accessor(self) -> str:
		return to_accessor(self.symbol.tokens)

	@property
	def operations(self) -> ClassOperations:
		return PythonClassOperations()

	@property
	def decorators(self) -> list[Decorator]:
		return [node.as_a(Decorator) for node in self._children('decorators')] if self._exists('decorators') else []

	@property
	def comment(self) -> DocString | Empty:
		found_comment = [statement for statement in self._org_statements if isinstance(statement, DocString)]
		if len(found_comment):
			return found_comment.pop()

		return self.dirty_child(Empty, '__empty__', tokens='')

	@property
	@duck_typed(StatementBlock)
	def statements(self) -> list[Node]:
		return [statement for statement in self._org_statements if not statement.is_a(DocString)]

	@property
	def _org_statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		raise NotImplementedError()

	@property
	def template_types(self) -> list[Type]:
		"""Note: @see Class.template_types"""
		return []

	@property
	def actual_symbol(self) -> str | None:
		embedder = self._dig_embedder(__actual__.__name__)
		return embedder.arguments[0].value.as_a(String).as_string if embedder else None

	@property
	def alias_or_domain_name(self) -> str:
		"""Note: トランスパイル時のみ使用すること。それ以外の使用はNG"""
		embedder = self._dig_embedder(Embed.alias.__qualname__)
		if not embedder:
			return self.domain_name

		alias = embedder.arguments[0].value.as_a(String).as_string
		return f'{alias}{self.domain_name}' if len(embedder.arguments) == 2 else alias

	def _decl_vars_with(self, allow: type[T_Declable]) -> list[T_Declable]:
		return VarsCollector.collect(self, allow)

	def _dig_embedder(self, identifier: str) -> Decorator | None:
		"""埋め込みデコレーターを取得

		Args:
			identifier (str): 識別名
		Returns:
			Decorator | None: デコレーター
		Examples:
			```python
			@__actual__('int')
			class Integer: ...
			```
		"""
		embeders = [decorator for decorator in self.decorators if decorator.path.tokens == identifier]
		return embeders[0] if len(embeders) > 0 else None


@Meta.embed(Node, accept_tags('function_def'))
class Function(ClassDef):
	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> TypesName:
		symbol = self._by('function_def_raw.name').as_a(TypesName)
		alias = self.actual_symbol
		return symbol if not alias else symbol.dirty_proxify(tokens=alias)

	@property
	@override
	@Meta.embed(Node, expandable)
	def decorators(self) -> list[Decorator]:
		return super().decorators

	@property
	@Meta.embed(Node, expandable)
	def parameters(self) -> list[Parameter]:
		if not self._exists('function_def_raw.parameters'):
			return []

		return [node.as_a(Parameter) for node in self._children('function_def_raw.parameters') if not node.is_a(Empty)]

	@property
	@Meta.embed(Node, expandable)
	def return_type(self) -> Type:
		return self._children('function_def_raw')[2].as_a(Type)

	@property
	@override
	@Meta.embed(Node, expandable)
	def comment(self) -> DocString | Empty:
		return super().comment

	@property
	@override
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return super().statements

	@property
	@override
	def block(self) -> Block:
		return self._by('function_def_raw.block').as_a(Block)

	@property
	def decl_vars(self) -> list[Parameter | DeclLocalVar]:
		parameters = self.parameters
		parameter_names = [parameter.symbol.domain_name for parameter in parameters]
		# 仮引数と変数宣言をマージ(仮引数と同じドメイン名の変数は除外)
		local_vars = [var for var in self._decl_vars_with(DeclLocalVar) if var.symbol.domain_name not in parameter_names]
		return [*parameters, *local_vars]

	@property
	def is_pure(self) -> bool:
		return self._has_annotation(Embed.pure.__qualname__)

	def _has_annotation(self, *names: str) -> bool:
		return len([True for decorator in self.decorators if decorator.path.tokens in names]) > 0


@Meta.embed(Node)
class ClassMethod(Function):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# @see ClassDef.decorators
		decorators = via._children('decorators') if via._exists('decorators') else []
		return len(decorators) > 0 and decorators[0].as_a(Decorator).path.tokens == 'classmethod'

	@property
	def is_abstract(self) -> bool:
		return self._has_annotation('abstractmethod')

	@property
	def is_override(self) -> bool:
		return self._has_annotation(implements.__name__, override.__name__)

	@property
	def class_types(self) -> ClassDef:
		return self.parent.as_a(Block).parent.as_a(ClassDef)


@Meta.embed(Node)
class Constructor(Function):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# @see Function.symbol
		return via._by('function_def_raw.name').tokens == '__init__'

	@property
	def is_abstract(self) -> bool:
		return self._has_annotation('abstractmethod')

	@property
	def is_override(self) -> bool:
		return self._has_annotation(implements.__name__, override.__name__)

	@property
	def class_types(self) -> ClassDef:
		return self.parent.as_a(Block).parent.as_a(ClassDef)


@Meta.embed(Node)
class Method(Function):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# @see Function.symbol
		if via._by('function_def_raw.name').tokens == '__init__':
			return False

		# @see Function.parameters
		if not via._exists('function_def_raw.parameters'):
			return False

		parameters = via._children('function_def_raw.parameters')
		return len(parameters) > 0 and parameters[0].as_a(Parameter).symbol.is_a(DeclThisParam)

	@property
	def is_abstract(self) -> bool:
		return self._has_annotation('abstractmethod')

	@property
	def is_override(self) -> bool:
		return self._has_annotation(implements.__name__, override.__name__)

	@property
	def is_property(self) -> bool:
		return self._has_annotation('property')

	@property
	def class_types(self) -> ClassDef:
		return self.parent.as_a(Block).parent.as_a(ClassDef)


@Meta.embed(Node)
class Closure(Function):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		elems = via._full_path.de_identify().elements
		actual_function_def_at = last_index_of(elems, 'function_def_raw')
		expect_function_def_at = max(0, len(elems) - 3)
		in_decl_function = actual_function_def_at == expect_function_def_at
		return in_decl_function


@Meta.embed(Node, accept_tags('class_def'))
class Class(ClassDef):
	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> TypesName:
		symbol = self._by('class_def_raw.name').as_a(TypesName)
		alias = self.actual_symbol
		return symbol if not alias else symbol.dirty_proxify(tokens=alias)

	@property
	@override
	@Meta.embed(Node, expandable)
	def decorators(self) -> list[Decorator]:
		return super().decorators

	@property
	@Meta.embed(Node, expandable)
	def inherits(self) -> list[Type]:
		"""Note: XXX Genericは継承チェーンを考慮する必要がないため除外する"""
		return [inherit for inherit in self.__org_inherits if inherit.type_name.tokens != Generic.__name__]

	@property
	@override
	@Meta.embed(Node, expandable)
	def template_types(self) -> list[Type]:
		"""Note: 厳密に言うとこのメソッドでテンプレートタイプを取得することはできず、候補のタイプノードである点に注意"""
		def fetch_template_types(t_type: GenericType) -> list[Type]:
			t_types: list[Type] = []
			for in_t_type in t_type.template_types:
				if isinstance(in_t_type, GenericType):
					t_types.extend(fetch_template_types(in_t_type))
				elif isinstance(in_t_type, VarOfType):
					t_types.append(in_t_type)

			return t_types

		candidate_types: list[Type] = []
		for inherit in self.__org_inherits:
			if isinstance(inherit, GenericType):
				candidate_types.extend(fetch_template_types(inherit))

		return candidate_types

	@property
	@override
	@Meta.embed(Node, expandable)
	def comment(self) -> DocString | Empty:
		return super().comment

	@property
	@override
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return super().statements

	@property
	@override
	def block(self) -> Block:
		return self._by('class_def_raw.block').as_a(Block)

	@property
	def __org_inherits(self) -> list[Type]:
		if not self._exists('class_def_raw.inherit_arguments'):
			return []

		return [node.class_type for node in self._children('class_def_raw.inherit_arguments') if isinstance(node, InheritArgument)]

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
	def class_vars(self) -> list[DeclClassVar]:
		return self._decl_vars_with(DeclClassVar)

	@property
	def this_vars(self) -> list[DeclThisVar]:
		"""コンストラクター内の変数宣言を取得"""
		if not self.constructor_exists:
			return []

		this_var_names = self.decl_this_vars.keys()
		if len(this_var_names) == 0:
			return []

		return [this_var for this_var in self.constructor._decl_vars_with(DeclThisVar) if this_var.tokens_without_this in this_var_names]

	@property
	def decl_this_vars(self) -> dict[str, AnnoAssign]:
		"""前方宣言内の型/アノテーションを取得"""
		return {node.receiver.domain_name: node for node in self.statements if isinstance(node, AnnoAssign) and isinstance(node.receiver, DeclThisVarForward)}


@Meta.embed(Node)
class Enum(Class):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# @see Class.__org_inherits
		if not via._exists('class_def_raw.inherit_arguments'):
			return False

		inherits = via._children('class_def_raw.inherit_arguments')
		# XXX Enumと言うシンボル名に依存しない方法を検討
		return 'Enum' in [inherit.class_type.tokens for inherit in inherits if isinstance(inherit, InheritArgument)]

	@property
	def vars(self) -> list[DeclLocalVar]:
		"""Note: XXX MoveAssignはメンバー変数宣言にならない設計であるため、返却型はlist[DeclLocalVar]になる"""
		# XXX collect_decl_varsだと不要な変数宣言まで拾う可能性があるため、ステートメントから直接収集
		vars = flatten([node.symbols for node in self.statements if isinstance(node, MoveAssign)])
		return [var.as_a(DeclLocalVar) for var in vars]


@Meta.embed(Node, accept_tags('class_assign'))
class AltClass(ClassDef):
	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> TypesName:
		return self._by('assign_namelist.var').as_a(TypesName)

	@property
	@override
	def block(self) -> Block:
		return self.dirty_child(Block, 'block', statements=[])

	@property
	@Meta.embed(Node, expandable)
	def actual_type(self) -> Type:
		return self._at(1).as_a(Type)


@Meta.embed(Node, accept_tags('template_assign'))
class TemplateClass(ClassDef):
	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> TypesName:
		return self._by('assign_namelist.var').as_a(TypesName)

	@property
	@override
	def block(self) -> Block:
		return self.dirty_child(Block, 'block', statements=[])

	@property
	def definition_type(self) -> Type:
		return self._at(1).as_a(Type)

	@property
	def boundary(self) -> Type | Empty:
		if not self._exists('template_assign_boundary'):
			return self.dirty_child(Empty, '__empty__', tokens='')

		return self._by('template_assign_boundary')._at(0).as_a(Type)

	@property
	def covariant(self) -> Boolean | Empty:
		if not self._exists('template_assign_covariant'):
			return self.dirty_child(Empty, '__empty__', tokens='')

		return self._by('template_assign_covariant')._at(0).as_a(Boolean)


class VarsCollector:
	"""変数宣言コレクター"""

	@classmethod
	def collect(cls, block: StatementBlock, allow: type[T_Declable]) -> list[T_Declable]:
		"""対象のブロック内で宣言した変数を収集する

		Args:
			block (StatementBlock): ブロック
			allow (type[T_Declable]): 収集対象の変数宣言ノード
		Returns:
			list[T_Declable]: 宣言ノードリスト
		"""
		return list(cls._collect_impl(block, allow).values())

	@classmethod
	def _collect_impl(cls, block: StatementBlock, allow: type[T_Declable]) -> dict[str, T_Declable]:
		"""対象のブロック内で宣言した変数を収集する

		Args:
			block (StatementBlock): ブロック
			allow (type[T_Declable]): 収集対象の変数宣言ノード
		Returns:
			dict[str, T_Declable]: 完全参照名と変数宣言ノードのマップ表
		"""
		decl_vars: dict[str, T_Declable] = {}
		for node in block.statements:
			if isinstance(node, (AnnoAssign, MoveAssign)):
				decl_vars = cls._merged_by(decl_vars, node, allow)
			elif isinstance(node, For):
				decl_vars = cls._merged_by(decl_vars, node, allow)
			elif isinstance(node, Try):
				for catch in node.catches:
					decl_vars = cls._merged_by(decl_vars, catch, allow)
			elif isinstance(node, With):
				for entry in node.entries:
					decl_vars = cls._merged_by(decl_vars, entry, allow)

			if isinstance(node, (If, Try)):
				for in_block in node.having_blocks:
					decl_vars = cls._merged(decl_vars, cls._collect_impl(in_block, allow))
			elif isinstance(node, (While, For, With)):
				decl_vars = cls._merged(decl_vars, cls._collect_impl(node.block, allow))

		return decl_vars

	@classmethod
	def _merged_by(cls, decl_vars: dict[str, T_Declable], add_declare: IDeclaration, allow: type[T_Declable]) -> dict[str, T_Declable]:
		"""シンボル宣言ノード内の変数を収集済みデータに合成する

		Args:
			decl_vars (dict[str, T_Declable]): 収集済みの変数宣言ノード
			add_declare (IDeclaration: 追加対象のシンボル宣言ノード
			allow (type[T_Declable]): 収集対象の変数宣言ノード
		Returns:
			dict[str, T_Declable]: 完全参照名と変数宣言ノードのマップ表
		"""
		add_vars = {symbol.fullyname: symbol for symbol in add_declare.symbols if isinstance(symbol, allow)}
		return cls._merged(decl_vars, add_vars)

	@classmethod
	def _merged(cls, decl_vars: dict[str, T_Declable], add_vers: dict[str, T_Declable]) -> dict[str, T_Declable]:
		"""追加対象の変数を収集済みデータに合成する

		Args:
			decl_vars (dict[str, T_Declable]): 収集済みの変数宣言ノード
			add_vars (dict[str, T_Declable]): 追加の変数宣言ノード
		Returns:
			dict[str, T_Declable]: 完全参照名と変数宣言ノードのマップ表
		Note:
			# 追加条件
			1. 新規の完全参照名
			2. 追加対象のスコープと既存データのスコープに相関性が無い
		"""
		merged = decl_vars
		for add_fullyname, add_var in add_vers.items():
			if add_fullyname in decl_vars:
				continue

			relationed = False
			for decl_var in decl_vars.values():
				if decl_var.domain_name != add_var.domain_name:
					continue

				if add_var.scope.startswith(decl_var.scope):
					relationed = True
					break

			if not relationed:
				merged[add_fullyname] = add_var

		return merged
