import re
from typing import cast

from py2cpp.ast.dsn import DSN
from py2cpp.lang.implementation import implements, override
from py2cpp.lang.sequence import last_index_of
from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.literal import Literal
from py2cpp.node.definition.terminal import Empty
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.interface import IDomainName, ITerminal
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('getattr', 'var', 'name'))
class Fragment(Node):
	@property
	def is_class_var(self) -> bool:
		"""Note: マッチング対象: クラス変数"""
		# XXX ASTへの依存度が非常に高い判定なので注意
		# XXX 期待するパス: class_def_raw.block.assign_stmt.(assign|anno_assign).(getattr|var|name)
		elems = self._full_path.de_identify().elements
		actual_class_def_at = last_index_of(elems, 'class_def_raw')
		expect_class_def_at = max(0, len(elems) - 5)
		in_decl_class_var = actual_class_def_at == expect_class_def_at
		in_decl_var = self._full_path.parent_tag in ['assign', 'anno_assign']
		is_local = DSN.elem_counts(self.tokens) == 1
		return in_decl_var and in_decl_class_var and is_local

	@property
	def is_this_var(self) -> bool:
		"""Note: マッチング対象: インスタンス変数"""
		in_decl_var = self._full_path.parent_tag in ['assign', 'anno_assign']
		is_property = re.fullmatch(r'self.\w+', self.tokens) is not None
		return in_decl_var and is_property

	@property
	def is_param_class(self) -> bool:
		"""Note: マッチング対象: 仮引数(clsのみ)"""
		tokens = self.tokens
		in_decl_var = self._full_path.parent_tag in ['typedparam']
		is_class = tokens == 'cls'
		is_local = DSN.elem_counts(tokens) == 1
		return in_decl_var and is_class and is_local

	@property
	def is_param_this(self) -> bool:
		"""Note: マッチング対象: 仮引数(selfのみ)"""
		tokens = self.tokens
		in_decl_var = self._full_path.parent_tag in ['typedparam']
		is_this = tokens == 'self'
		is_local = DSN.elem_counts(tokens) == 1
		return in_decl_var and is_this and is_local

	@property
	def is_local_var(self) -> bool:
		"""Note: マッチング対象: ローカル変数/仮引数(cls/self以外)"""
		tokens = self.tokens
		in_decl_var = self._full_path.parent_tag in ['assign', 'anno_assign', 'typedparam', 'for_stmt', 'except_clause']
		is_class_or_this = tokens == 'cls' or tokens == 'self'
		is_local = DSN.elem_counts(tokens) == 1
		return in_decl_var and not is_class_or_this and is_local

	@property
	def in_decl_class_type(self) -> bool:
		return self._full_path.parent_tag in ['class_def_raw', 'enum_def', 'function_def_raw']

	@property
	def in_decl_import(self) -> bool:
		return self._full_path.parent_tag == 'import_names'


class Declable(Fragment, IDomainName, ITerminal):
	@property
	@implements
	def domain_id(self) -> str:
		return DSN.join(self.scope, self.tokens)

	@property
	@implements
	def domain_name(self) -> str:
		return DSN.join(self.module_path, self.tokens)

	@property
	@implements
	def can_expand(self) -> bool:
		return False


class DeclVar(Declable): pass


@Meta.embed(Node, accept_tags('var'), actualized(via=Fragment))
class ClassVar(DeclVar):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.is_class_var

	@property
	def class_domain(self) -> IDomainName:
		return cast(IDomainName, self._ancestor('class_def'))


@Meta.embed(Node, accept_tags('getattr'), actualized(via=Fragment))
class ThisVar(DeclVar):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.is_this_var

	@property
	@override
	def domain_id(self) -> str:
		return DSN.join(self.class_domain.domain_id, self.tokens_without_this)

	@property
	@override
	def domain_name(self) -> str:
		return DSN.join(self.class_domain.domain_name, self.tokens_without_this)

	@property
	def tokens_without_this(self) -> str:
		return DSN.join(*DSN.elements(self.tokens)[1:])

	@property
	def class_domain(self) -> IDomainName:
		return cast(IDomainName, self._ancestor('class_def'))


class BlockVar(DeclVar): pass


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class ParamClass(BlockVar):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.is_param_class

	@property
	def class_domain(self) -> IDomainName:
		return cast(IDomainName, self._ancestor('class_def'))


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class ParamThis(BlockVar):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.is_param_this

	@property
	def class_domain(self) -> IDomainName:
		return cast(IDomainName, self._ancestor('class_def'))


@Meta.embed(Node, accept_tags('var', 'name'), actualized(via=Fragment))
class LocalVar(BlockVar):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.is_local_var


class DeclName(Declable): pass


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class TypesName(DeclName):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.in_decl_class_type


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class ImportName(DeclName):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.in_decl_import


class Reference(Fragment, IDomainName):
	@property
	@implements
	def domain_id(self) -> str:
		return DSN.join(self.scope, self.tokens)

	@property
	@implements
	def domain_name(self) -> str:
		return DSN.join(self.module_path, self.tokens)


@Meta.embed(Node, accept_tags('getattr'), actualized(via=Fragment))
class Relay(Reference):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		if via.is_local_var or via.is_this_var:
			return False

		if via.in_decl_class_type or via.in_decl_import:
			return False

		return True

	@property
	@Meta.embed(Node, expandable)
	def receiver(self) -> 'Reference | FuncCall | Indexer | Literal':  # XXX 前方参照
		return self._at(0).one_of(Reference | FuncCall | Indexer | Literal)

	@property
	def prop(self) -> 'Var':  # XXX 前方参照
		return self._at(1).as_a(Var)


@Meta.embed(Node, accept_tags('var', 'name'), actualized(via=Fragment))
class Var(Reference, ITerminal):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		# XXX actualizeループの結果を元に排他的に決定(実質的なフォールバック)
		return True

	@property
	@implements
	def can_expand(self) -> bool:
		return False


@Meta.embed(Node, accept_tags('dotted_name'))
class Path(Node, ITerminal):
	@property
	@implements
	def can_expand(self) -> bool:
		return False


@Meta.embed(Node, actualized(via=Path))
class ImportPath(Path):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return via._full_path.parent_tag == 'import_stmt'


@Meta.embed(Node, actualized(via=Path))
class DecoratorPath(Path):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return via._full_path.parent_tag == 'decorator'


@Meta.embed(Node, accept_tags('getitem'))
class Indexer(Node):
	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Reference:  # XXX symbol以外の名前を検討
		return self._at(0).as_a(Reference)

	@property
	@Meta.embed(Node, expandable)
	def key(self) -> Node:
		return self._by('slices.slice')._at(0)


class Type(Node, IDomainName, ITerminal):
	@property
	@implements
	def can_expand(self) -> bool:
		return True

	@property
	@implements
	def domain_id(self) -> str:
		return DSN.join(self.scope, self.symbol.tokens)

	@property
	@implements
	def domain_name(self) -> str:
		return DSN.join(self.module_path, self.symbol.tokens)

	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> 'Type':  # XXX symbol以外の名前を検討
		"""
		Note:
			XXX 終端要素の場合は自分自身をシンボルとして扱う
			XXX 派生クラスでexpandableの設定が矛盾する場合がある。終端要素は展開しないので必ずしも必要ない。直接的な害は無いが勘違いしやすいので修正を検討
		"""
		return self if not self.can_expand else self._at(0).as_a(Type)


@Meta.embed(Node, accept_tags('typed_getattr', 'typed_var'))
class GeneralType(Type):
	@property
	@override
	def can_expand(self) -> bool:
		return False


@Meta.embed(Node, accept_tags('typed_getitem'))
class GenericType(Type): pass


class CollectionType(GenericType):
	@property
	def value_type(self) -> Type:
		raise NotImplementedError()


@Meta.embed(Node, actualized(via=GenericType))
class ListType(CollectionType):
	@classmethod
	@override
	def match_feature(cls, via: GenericType) -> bool:
		return via.symbol.tokens == 'list'

	@property
	@override
	@Meta.embed(Node, expandable)
	def value_type(self) -> Type:
		return self._by('typed_slices.typed_slice')._at(0).as_a(Type)


@Meta.embed(Node, actualized(via=GenericType))
class DictType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: GenericType) -> bool:
		return via.symbol.tokens == 'dict'

	@property
	@Meta.embed(Node, expandable)
	def key_type(self) -> Type:
		return self._by('typed_slices.typed_slice[0]')._at(0).one_of(Type)

	@property
	@override
	@Meta.embed(Node, expandable)
	def value_type(self) -> Type:
		return self._by('typed_slices.typed_slice[1]')._at(0).one_of(Type)


@Meta.embed(Node, accept_tags('typed_or_expr'))
class UnionType(GenericType):
	@property
	@Meta.embed(Node, expandable)
	def types(self) -> list[Type]:
		return [node.as_a(Type) for node in self._children()]


@Meta.embed(Node, accept_tags('typed_none'))
class NullType(Type, ITerminal):
	@property
	@override
	def can_expand(self) -> bool:
		return False

	@property
	@override
	def domain_id(self) -> str:
		# XXX 定数化を検討
		return DSN.join(self.module_path, 'None')

	@property
	@override
	def domain_name(self) -> str:
		return self.domain_id


@Meta.embed(Node, accept_tags('funccall'))
class FuncCall(Node):
	@property
	@Meta.embed(Node, expandable)
	def calls(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def arguments(self) -> list[Argument]:
		args = self._at(1)
		return [node.as_a(Argument) for node in args._children()] if not args.is_a(Empty) else []


@Meta.embed(Node, actualized(via=FuncCall))
class Super(FuncCall):
	@classmethod
	@override
	def match_feature(cls, via: FuncCall) -> bool:
		return via.calls.tokens == 'super'

	@property
	def parent_symbol(self) -> Type:
		from py2cpp.node.definition.statement_compound import Class  # FIXME 循環参照

		decl_class = self._ancestor('class_def').as_a(Class)
		# XXX 簡易化のため単一継承と言う前提。MROは考慮せず先頭要素を直系の親クラスとする
		return decl_class.parents[0].symbol
