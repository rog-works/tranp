import re
from typing import cast

from py2cpp.ast.dsn import DSN
from py2cpp.lang.implementation import implements, override
from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.literal import Literal
from py2cpp.node.definition.terminal import Empty
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.interface import IDomainName, ITerminal
from py2cpp.node.node import Node
from py2cpp.node.protocol import Symbolization

@Meta.embed(Node, accept_tags('getattr', 'var', 'name'))
class Fragment(Node):
	@property
	def is_this_var(self) -> bool:
		"""Note: マッチング対象: インスタンス変数"""
		tokens = self.tokens
		in_decl_var = self._full_path.parent_tag in ['assign', 'anno_assign']
		is_property = re.fullmatch(r'self.\w+', tokens) is not None
		return in_decl_var and is_property

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
		"""Note: マッチング対象: クラス変数/ローカル変数/仮引数(self以外)"""
		tokens = self.tokens
		in_decl_var = self._full_path.parent_tag in ['assign', 'anno_assign', 'typedparam', 'for_stmt', 'except_clause']
		is_this = tokens == 'self'
		is_local = DSN.elem_counts(tokens) == 1
		return in_decl_var and not is_this and is_local

	@property
	def in_decl_class_type(self) -> bool:
		return self._full_path.parent_tag in ['class_def_raw', 'enum_def', 'function_def_raw']

	@property
	def in_decl_import(self) -> bool:
		return self._full_path.parent_tag == 'import_names'


class Symbol(Fragment, IDomainName, ITerminal):
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


class Var(Symbol): pass


@Meta.embed(Node, actualized(via=Fragment))
class ThisVar(Var):
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


class BlockVar(Var): pass


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


class DeclName(Symbol): pass


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class ClassTypeName(DeclName):
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
	def property(self) -> 'Name':  # XXX 前方参照
		return self._at(1).as_a(Name)


@Meta.embed(Node, accept_tags('var', 'name'), actualized(via=Fragment))
class Name(Reference, ITerminal):
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


class Type(Node, IDomainName):
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
	def symbol(self) -> 'Type | Name':  # XXX symbol以外の名前を検討 XXX Nameは微妙
		return self._at(0).one_of(Type | Name)


@Meta.embed(Node, accept_tags('typed_getattr', 'typed_var'))
class GeneralType(Type, ITerminal):
	@property
	@implements
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
class NoneType(Type, ITerminal):
	@property
	@implements
	def can_expand(self) -> bool:
		return False


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
	def class_symbol(self) -> Symbol:
		# FIXME 親クラスを参照するべきなので誤り
		return cast(Symbolization, self._ancestor('class_def')).symbol.as_a(Symbol)
