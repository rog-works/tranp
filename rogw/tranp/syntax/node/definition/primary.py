import re
from typing import Union

from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.lang.convertion import as_a
from rogw.tranp.lang.sequence import flatten, last_index_of
from rogw.tranp.syntax.ast.path import EntryPath
from rogw.tranp.syntax.errors import InvalidRelationError
from rogw.tranp.syntax.node.behavior import IDomain, INamespace, IScope, ITerminal
from rogw.tranp.syntax.node.definition.literal import Literal
from rogw.tranp.syntax.node.definition.terminal import Empty
from rogw.tranp.syntax.node.embed import Meta, accept_tags, expandable
from rogw.tranp.syntax.node.interface import IDeclaration, ISymbol
from rogw.tranp.syntax.node.node import Node


@Meta.embed(Node, accept_tags('argvalue'))
class Argument(Node):
	""" Note: * FIXME starargs/kwargsを受け入れるが、現状は通常の引数と同様に扱う"""

	@property
	@Meta.embed(Node, expandable)
	def label(self) -> 'ArgumentLabel | Empty':
		children = self._children()
		if len(children) == 2:
			return children[0].as_a(ArgumentLabel)

		return self.dirty_child(Empty, '__empty__', tokens='')

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node:
		children = self._children()
		return children[1] if len(children) == 2 else children[0]


@Meta.embed(Node, accept_tags('typed_argvalue'))
class InheritArgument(Node):
	@property
	@Meta.embed(Node, expandable)
	def class_type(self) -> 'Type':
		return self._at(0).as_a(Type)


@Meta.embed(Node, accept_tags('name'))
class ArgumentLabel(Node, ITerminal):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return via._full_path.parent_tag == 'argvalue'

	@property
	def invoker(self) -> 'FuncCall':
		return self._ancestor('funccall').as_a(FuncCall)


class Declable(Node, IDomain, ISymbol, ITerminal):
	@property
	@override
	def domain_name(self) -> str:
		return self.tokens

	@property
	@implements
	def symbol(self) -> 'Declable':
		return self

	@property
	@implements
	def declare(self) -> Node:
		"""
		Raises:
			InvalidRelationError: 不正な親子関係
		"""
		parent_tags = ['assign_namelist', 'for_namelist', 'except_clause', 'with_item', 'typedparam', 'import_as_names']
		if self._full_path.parent_tag in parent_tags and isinstance(self.parent, IDeclaration):
			return self.parent

		raise InvalidRelationError(f'node: {self}, parent: {self.parent}, parent_tag: {self._full_path.parent_tag}')


class DeclVar(Declable): pass


@Meta.embed(Node, accept_tags('var'))
class DeclClassVar(DeclVar):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return DeclableMatcher.is_decl_class_var(via)


@Meta.embed(Node, accept_tags('var'))
class DeclThisVarForward(DeclVar):
	"""Note: XXX このノードはアノテーションのためだけに存在。型推論、トランスパイルどちらにしても無視する想定"""

	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return DeclableMatcher.is_decl_this_var_forward(via)


@Meta.embed(Node, accept_tags('getattr'))
class DeclThisVar(DeclVar):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return DeclableMatcher.is_decl_this_var(via)

	@property
	@override
	def domain_name(self) -> str:
		return self.tokens_without_this

	@property
	@override
	def fullyname(self) -> str:
		"""Note: XXX クラス直下に配置するため例外的にスコープを調整"""
		return ModuleDSN.full_joined(self._ancestor('class_def').fullyname, self.domain_name)

	@property
	def tokens_without_this(self) -> str:
		return DSN.shift(self.tokens, 1)


@Meta.embed(Node, accept_tags('var', 'name'))
class DeclLocalVar(DeclVar):
	"""Note: XXX 'var'だけで本質的には問題ないはずだが、For.symbols/Catch.symbolで'name'が使われているため、これを取り込むため'name'を受け入れ"""

	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return DeclableMatcher.is_decl_local_var(via)


@Meta.embed(Node, accept_tags('name'))
class DeclParam(DeclLocalVar):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return DeclableMatcher.is_param(via)


class DeclClassParam(DeclParam):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return DeclableMatcher.is_param_class(via)

	@property
	def class_types(self) -> Node:
		return self._ancestor('class_def')


class DeclThisParam(DeclParam):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return DeclableMatcher.is_param_this(via)

	@property
	def class_types(self) -> Node:
		return self._ancestor('class_def')


class DeclName(Declable): pass


@Meta.embed(Node, accept_tags('name'))
class TypesName(DeclName):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return DeclableMatcher.in_decl_class_type(via)

	@property
	def class_types(self) -> Node:
		return self.parent


@Meta.embed(Node, accept_tags('var'))
class AltTypesName(TypesName):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return DeclableMatcher.in_decl_alt_class_type(via)


@Meta.embed(Node, accept_tags('name'))
class ImportName(DeclName):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return DeclableMatcher.in_decl_import(via)


@Meta.embed(Node, accept_tags('import_as_name'))
class ImportAsName(DeclName):
	@property
	@override
	def tokens(self) -> str:
		return self.symbol.tokens

	@property
	@override
	def symbol(self) -> ImportName:
		return self.alias if isinstance(self.alias, ImportName) else self.entity_symbol

	@property
	def entity_symbol(self) -> ImportName:
		return self._at(0).as_a(ImportName)

	@property
	def alias(self) -> ImportName | Empty:
		node = self._at(1)
		return node if isinstance(node, ImportName) else node.as_a(Empty)


class Reference(Node): pass


@Meta.embed(Node, accept_tags('getattr'))
class Relay(Reference, IDomain):
	@property
	@override
	def domain_name(self) -> str:
		return ModuleDSN.local_joined(self.receiver.domain_name, self.prop.tokens)

	@classmethod
	def match_feature(cls, via: Node) -> bool:
		if DeclableMatcher.is_decl_local_var(via) \
			or DeclableMatcher.is_decl_this_var(via) \
			or DeclableMatcher.in_decl_class_type(via) \
			or DeclableMatcher.in_decl_alt_class_type(via) \
			or DeclableMatcher.in_decl_import(via):
			return False

		return True

	@property
	@Meta.embed(Node, expandable)
	def receiver(self) -> 'Reference | FuncCall | Generator | Literal':
		return self._at(0).one_of(Reference, FuncCall, Generator, Literal)

	@property
	def prop(self) -> 'Var':
		return self._at(1).as_a(Var)


@Meta.embed(Node, accept_tags('var', 'name'))
class Var(Reference, IDomain, ITerminal):
	@property
	@override
	def domain_name(self) -> str:
		return self.tokens


@Meta.embed(Node, accept_tags('var'))
class ClassRef(Var):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return via.tokens == 'cls'

	@property
	def class_types(self) -> Node:
		return self._ancestor('class_def')


@Meta.embed(Node, accept_tags('var'))
class ThisRef(Var):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return via.tokens == 'self'


@Meta.embed(Node, accept_tags('getitem'))
class Indexer(Reference):
	@property
	@Meta.embed(Node, expandable)
	def receiver(self) -> 'Reference | FuncCall | Generator':
		return self._at(0).one_of(Reference, FuncCall, Generator)

	@property
	@Meta.embed(Node, expandable)
	def keys(self) -> list[Node]:
		return self._children('slice' if self.sliced else 'slices')

	@property
	def sliced(self) -> bool:
		return self._exists('slice')


@Meta.embed(Node, accept_tags('dotted_name'))
class Path(Node, ITerminal): pass


@Meta.embed(Node)
class ImportPath(Path):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return via._full_path.parent_tag == 'import_stmt'


@Meta.embed(Node)
class DecoratorPath(Path):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return via._full_path.parent_tag == 'decorator'


class Type(Node, IDomain):
	"""Note: Typeに固有のドメイン名はないが、同じ参照名を持つものは等価に扱って問題ないためIDomainを実装 FIXME GenericTypeは別なのでは？"""

	@property
	@override
	def domain_name(self) -> str:
		return self.type_name.tokens

	@property
	def type_name(self) -> 'Type':
		return self


class GeneralType(Type): pass


@Meta.embed(Node, accept_tags('typed_getattr'))
class RelayOfType(GeneralType):
	@property
	@Meta.embed(Node, expandable)
	def receiver(self) -> 'RelayOfType | VarOfType':
		return self._at(0).one_of(RelayOfType, VarOfType)

	@property
	def prop(self) -> Var:
		return self._at(1).as_a(Var)


@Meta.embed(Node, accept_tags('typed_var'))
class VarOfType(GeneralType, ITerminal): pass


@Meta.embed(Node, accept_tags('typed_getitem'))
class GenericType(Type):
	@property
	@override
	@Meta.embed(Node, expandable)
	def type_name(self) -> 'Type':
		return self._at(0).as_a(Type)

	@property
	def template_types(self) -> list[Type]:
		return [node.as_a(Type) for node in self._children('typed_slices')]

	@property
	def primary_type(self) -> Type:
		return self.template_types[0]


@Meta.embed(Node)
class ListType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._at(0).tokens == 'list'

	@property
	@override
	@Meta.embed(Node, expandable)
	def value_type(self) -> Type:
		return self.primary_type


@Meta.embed(Node)
class DictType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._at(0).tokens == 'dict'

	@property
	@Meta.embed(Node, expandable)
	def key_type(self) -> Type:
		return self.template_types[0]

	@property
	@override
	@Meta.embed(Node, expandable)
	def value_type(self) -> Type:
		return self.primary_type

	@property
	@override
	def primary_type(self) -> Type:
		"""Note: XXX value_typeをprimaryとするためoverride"""
		return self.template_types[1]


@Meta.embed(Node)
class CallableType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		"""Note: XXX TypeParametersはTypeではないため、template_typesは使わないこと"""
		children = via._children('typed_slices')
		return len(children) == 2 and children[0].is_a(TypeParameters)

	@property
	@Meta.embed(Node, expandable)
	def parameters(self) -> list[Type]:
		return self.template_types

	@property
	@Meta.embed(Node, expandable)
	def return_type(self) -> Type:
		return self._children('typed_slices')[1].as_a(Type)

	@property
	@override
	def template_types(self) -> list[Type]:
		return self._children('typed_slices')[0].as_a(TypeParameters).type_params


@Meta.embed(Node)
class CustomType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		"""Note: その他のGenericTypeと排他関係。実質的なフォールバック"""
		return True

	@property
	@override
	@Meta.embed(Node, expandable)
	def template_types(self) -> list[Type]:
		return super().template_types


@Meta.embed(Node, accept_tags('typed_or_expr'))
class UnionType(Type):
	@property
	@Meta.embed(Node, expandable)
	def or_types(self) -> list[Type]:
		return [node.as_a(Type) for node in self._children()]

	@property
	@override
	def domain_name(self) -> str:
		return Union.__name__


@Meta.embed(Node, accept_tags('typed_none'))
class NullType(Type, ITerminal):
	@property
	@override
	def domain_name(self) -> str:
		# XXX 定数化を検討
		return 'None'


@Meta.embed(Node, accept_tags('typed_list'))
class TypeParameters(Node):
	@property
	@Meta.embed(Node, expandable)
	def type_params(self) -> list[Type]:
		return [node.as_a(Type) for node in self._children()]


@Meta.embed(Node, accept_tags('funccall'))
class FuncCall(Node, IDomain):
	@property
	@override
	def domain_name(self) -> str:
		# XXX 一意な名称を持たないためIDで代用
		return ModuleDSN.identify(self.classification, self.id)

	@property
	@Meta.embed(Node, expandable)
	def calls(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def arguments(self) -> list['Argument']:
		if not self._exists('arguments'):
			return []

		return [node for node in self._children('arguments') if isinstance(node, Argument)]


@Meta.embed(Node)
class Super(FuncCall):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._at(0).tokens == 'super'

	@property
	def can_resolve_super(self) -> bool:
		from rogw.tranp.syntax.node.definition.statement_compound import Class  # FIXME 循環参照

		return len(self._fetch_decl_class().as_a(Class).inherits) > 0

	@property
	def super_class_symbol(self) -> Type:
		"""Note: シンタックス上はobjectの暗黙的な継承を判断できないため、can_resolve_superで事前に確認が必要"""
		from rogw.tranp.syntax.node.definition.statement_compound import Class  # FIXME 循環参照

		# XXX 簡易化のため単一継承と言う前提。MROは考慮せず先頭要素を直系の親クラスとする
		return self._fetch_decl_class().as_a(Class).inherits[0].type_name

	def _fetch_decl_class(self) -> Node:
		return self._ancestor('class_def')


@Meta.embed(Node, accept_tags('elipsis'))
class Elipsis(Node, ITerminal): pass


@Meta.embed(Node, accept_tags('for_in', 'comp_for_in'))
class ForIn(Node):
	@property
	@Meta.embed(Node, expandable)
	def iterates(self) -> Node:
		return self._at(0)


@Meta.embed(Node, accept_tags('comp_for'))
class CompFor(Node, IDeclaration):
	@property
	@implements
	@Meta.embed(Node, expandable)
	def symbols(self) -> list[Declable]:
		return [node.as_a(Declable) for node in self._children('for_namelist')]

	@property
	@Meta.embed(Node, expandable)
	def for_in(self) -> ForIn:
		return self._by('comp_for_in').as_a(ForIn)

	@property
	def iterates(self) -> Node:
		return self.for_in.iterates


class Generator(Node):
	@property
	def decl_vars(self) -> list[Declable]:
		raise NotImplementedError()


class Comprehension(Generator, IDomain, IScope, INamespace):
	"""Note: XXX 属するカテゴリーは何が最適か検討。無名関数に近い？"""

	@property
	@override
	def domain_name(self) -> str:
		return ModuleDSN.identify(self.classification, self.id)

	@property
	@Meta.embed(Node, expandable)
	def projection(self) -> Node:
		return self._children('comprehension')[0]

	@property
	@override
	@Meta.embed(Node, expandable)
	def fors(self) -> list[CompFor]:
		return [node.as_a(CompFor) for node in self._children('comprehension.comp_fors')]

	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node | Empty:
		node = self._children('comprehension')[2]
		return node if isinstance(node, Empty) else node

	@property
	@override
	def decl_vars(self) -> list[Declable]:
		return list(flatten([comp_for.symbols for comp_for in self.fors]))

	@property
	def binded_this(self) -> bool:
		"""Note: メソッド内に存在する場合は、メソッドのスコープを静的に束縛しているものとして扱う"""
		from rogw.tranp.syntax.node.definition.statement_compound import Constructor, Method  # FIXME 循環参照

		elems = self.parent._full_path.de_identify().elements
		has_own_classes = 'class_def' in elems and 'function_def' in elems
		has_own_method = has_own_classes and elems.index('class_def') < elems.index('function_def')
		return has_own_method and self.parent._ancestor('function_def').is_a(Constructor, Method)


@Meta.embed(Node, accept_tags('list_comp'))
class ListComp(Comprehension):
	pass


@Meta.embed(Node, accept_tags('dict_comp'))
class DictComp(Comprehension):
	pass


class DeclableMatcher:
	"""変数宣言ノードのマッチングヘルパー"""

	@classmethod
	def is_decl_class_var(cls, via: Node) -> bool:
		"""マッチング判定 (マッチング対象: クラス変数宣言)

		Args:
			via (Node): ノード
		Returns:
			bool: True = 対象
		"""
		via_full_path = EntryPath(via.full_path)
		is_decl_class_var = via_full_path.de_identify().shift(-1).origin.endswith('class_var_assign.assign_namelist')
		return is_decl_class_var

	@classmethod
	def is_decl_this_var_forward(cls, via: Node) -> bool:
		"""マッチング判定 (マッチング対象: インスタンス変数の前方宣言)

		Args:
			via (Node): ノード
		Returns:
			bool: True = 対象
		Note:
			XXX ASTへの依存度が非常に高い判定なので注意
			XXX 期待するパス: class_def_raw.block.anno_assign.assign_namelist.var
		"""
		via_full_path = EntryPath(via.full_path)
		elems = via_full_path.de_identify().elements
		actual_class_def_at = last_index_of(elems, 'class_def_raw')
		expect_class_def_at = max(0, len(elems) - 5)
		in_decl_class_var = actual_class_def_at == expect_class_def_at
		in_decl_var = via_full_path.de_identify().shift(-1).origin.endswith('anno_assign.assign_namelist')
		is_local = DSN.elem_counts(via.tokens) == 1
		is_receiver = via_full_path.last[1] in [0, -1]  # 代入式の左辺が対象
		return in_decl_var and in_decl_class_var and is_local and is_receiver

	@classmethod
	def is_decl_this_var(cls, via: Node) -> bool:
		"""マッチング判定 (マッチング対象: インスタンス変数宣言)

		Args:
			via (Node): ノード
		Returns:
			bool: True = 対象
		"""
		via_full_path = EntryPath(via.full_path)
		in_decl_var = via_full_path.de_identify().shift(-1).origin.endswith('anno_assign.assign_namelist')
		is_property = re.fullmatch(r'self.\w+', via.tokens) is not None
		is_receiver = via_full_path.last[1] in [0, -1]  # 代入式の左辺が対象
		return in_decl_var and is_property and is_receiver

	@classmethod
	def is_param_class(cls, via: Node) -> bool:
		"""マッチング判定 (マッチング対象: 仮引数(clsのみ))

		Args:
			via (Node): ノード
		Returns:
			bool: True = 対象
		"""
		via_full_path = EntryPath(via.full_path)
		tokens = via.tokens
		in_decl_var = via_full_path.parent_tag == 'typedparam'
		is_class = tokens == 'cls'
		is_local = DSN.elem_counts(tokens) == 1
		return in_decl_var and is_class and is_local

	@classmethod
	def is_param_this(cls, via: Node) -> bool:
		"""マッチング判定 (マッチング対象: 仮引数(selfのみ))

		Args:
			via (Node): ノード
		Returns:
			bool: True = 対象
		"""
		via_full_path = EntryPath(via.full_path)
		tokens = via.tokens
		in_decl_var = via_full_path.parent_tag == 'typedparam'
		is_this = tokens == 'self'
		is_local = DSN.elem_counts(tokens) == 1
		return in_decl_var and is_this and is_local

	@classmethod
	def is_param(cls, via: Node) -> bool:
		"""マッチング判定 (マッチング対象: 仮引数(cls/self以外))

		Args:
			via (Node): ノード
		Returns:
			bool: True = 対象
		"""
		via_full_path = EntryPath(via.full_path)
		tokens = via.tokens
		in_decl_param = via_full_path.parent_tag == 'typedparam'
		is_class_or_this = tokens in ['cls', 'self']
		return in_decl_param and not is_class_or_this

	@classmethod
	def is_decl_local_var(cls, via: Node) -> bool:
		"""マッチング判定 (マッチング対象: ローカル変数宣言)

		Args:
			via (Node): ノード
		Returns:
			bool: True = 対象
		"""
		# For/Catch/WithEntry/Comprehension
		via_full_path = EntryPath(via.full_path)
		is_identified_by_name_only = via_full_path.parent_tag in ['for_namelist', 'except_clause', 'with_item']
		if is_identified_by_name_only and via_full_path.last_tag == 'name':
			return True

		# Assign
		tokens = via.tokens
		is_class_or_this = tokens in ['cls', 'self']
		parent_tags = via_full_path.de_identify().shift(-1).elements[-2:]
		for_assign, for_namelist = parent_tags if len(parent_tags) >= 2 else ['', '']
		in_decl_var = for_assign in ['assign', 'anno_assign'] and for_namelist == 'assign_namelist'
		is_local = DSN.elem_counts(tokens) == 1
		return in_decl_var and not is_class_or_this and is_local

	@classmethod
	def in_decl_class_type(cls, via: Node) -> bool:
		"""マッチング判定 (マッチング対象: クラス宣言)

		Args:
			via (Node): ノード
		Returns:
			bool: True = 対象
		"""
		via_full_path = EntryPath(via.full_path)
		return via_full_path.parent_tag in ['class_def_raw', 'function_def_raw']

	@classmethod
	def in_decl_alt_class_type(cls, via: Node) -> bool:
		"""マッチング判定 (マッチング対象: タイプ再定義/テンプレートタイプ宣言)

		Args:
			via (Node): ノード
		Returns:
			bool: True = 対象
		"""
		via_full_path = EntryPath(via.full_path)
		if via_full_path.parent_tag != 'assign_namelist':
			return False

		elems = via_full_path.de_identify().elements
		expect_assign_at = len(elems) - 3
		is_class_assign = last_index_of(elems, 'class_assign') == expect_assign_at
		is_template_assign = last_index_of(elems, 'template_assign') == expect_assign_at
		return is_class_assign or is_template_assign

	@classmethod
	def in_decl_import(cls, via: Node) -> bool:
		"""マッチング判定 (マッチング対象: インポート)

		Args:
			via (Node): ノード
		Returns:
			bool: True = 対象
		"""
		via_full_path = EntryPath(via.full_path)
		return via_full_path.parent_tag == 'import_as_name'
