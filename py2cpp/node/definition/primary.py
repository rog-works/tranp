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
class Fragment(Node): pass


class Symbol(Fragment, IDomainName, ITerminal):
	@property
	@implements
	def domain_id(self) -> str:
		return DSN.join(self.scope, self.tokens)

	@property
	@implements
	def domain_name(self) -> str:
		return DSN.join(self.module_path, self.tokens)

	@implements
	def can_expand(self) -> bool:
		return False


class Var(Symbol): pass


@Meta.embed(Node, actualized(via=Fragment))
class ThisVar(Var):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		is_decl_var = via._full_path.parent_tag in ['assign', 'anno_assign', 'typedparam']
		is_self = re.fullmatch(r'self.\w+', via.tokens) is not None
		return is_decl_var and is_self

	@property
	@override
	def domain_id(self) -> str:
		return DSN.join(cast(IDomainName, self.class_types).domain_id, self.tokens_without_this)

	@property
	@override
	def domain_name(self) -> str:
		return DSN.join(cast(IDomainName, self.class_types).domain_name, self.tokens_without_this)

	@property
	def tokens_without_this(self) -> str:
		return DSN.join(*DSN.elements(self.tokens)[1:])

	@property
	def class_types(self) -> Node:
		# XXX 中途半端感があるので修正を検討
		return self._ancestor('class_def')


@Meta.embed(Node, accept_tags('var', 'name'), actualized(via=Fragment))
class LocalVar(Var):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		is_decl_var = via._full_path.parent_tag in ['assign', 'anno_assign', 'typedparam', 'for_stmt', 'except_clause']
		is_not_self = not via.tokens.startswith('self')
		is_local = DSN.elem_counts(via.tokens) == 1
		return is_decl_var and is_not_self and is_local


class DeclName(Symbol): pass


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class ClassName(DeclName):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		is_decl_class = via._full_path.parent_tag in ['class_def_raw', 'enum_def', 'function_def_raw']
		return is_decl_class


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class ImportName(DeclName):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		is_decl_import = via._full_path.parent_tag == 'import_names'
		return is_decl_import


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
	def match_feature(cls, via: Node) -> bool:
		is_decl_var = via._full_path.parent_tag in ['assign', 'anno_assign', 'typedparam', 'for_stmt', 'except_clause']
		is_not_self = not via.tokens.startswith('self')
		is_local = DSN.elem_counts(via.tokens) == 1
		if is_decl_var and is_not_self and is_local:
			return False

		is_decl_var = via._full_path.parent_tag in ['assign', 'anno_assign', 'typedparam']
		is_self = re.fullmatch(r'self.\w+', via.tokens) is not None
		if is_decl_var and is_self:
			return False

		is_not_decl_class = via._full_path.parent_tag not in ['class_def_raw', 'enum_def', 'function_def_raw']
		is_not_decl_import = via._full_path.parent_tag not in ['import_stmt']
		is_relay = len(via._children()) == 2
		return is_not_decl_class and is_not_decl_import and is_relay

	@property
	@Meta.embed(Node, expandable)
	def receiver(self) -> 'Relay | FuncCall | Indexer | Literal':  # XXX 前方参照
		return self._at(0).one_of(Relay | FuncCall | Indexer | Literal)

	@property
	def property(self) -> 'Name':  # XXX 前方参照
		return self._at(1).as_a(Name)


@Meta.embed(Node, accept_tags('var', 'name'), actualized(via=Fragment))
class Name(Fragment, ITerminal):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		# XXX actualizeループの結果を元に排他的に決定(実質的なフォールバック)
		return True

	@implements
	def can_expand(self) -> bool:
		return False


@Meta.embed(Node, accept_tags('dotted_name'))
class Path(Node, ITerminal):
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
	def symbol(self) -> Symbol:  # FIXME シンボル以外も有り得るので不正確
		return self._at(0).as_a(Symbol)

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
	def symbol(self) -> Symbol:  # FIXME シンボル以外も有り得るので不正確
		return self._at(0).as_a(Symbol)


@Meta.embed(Node, accept_tags('typed_getattr', 'typed_var'))
class ClassType(Type): pass


@Meta.embed(Node, accept_tags('typed_getitem'))
class GenericType(Type): pass


class CollectionType(GenericType):
	@property
	def value_type(self) -> Symbol | GenericType:
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
	def value_type(self) -> Symbol | GenericType:
		return self._by('typed_slices.typed_slice')._at(0).one_of(Symbol | GenericType)


@Meta.embed(Node, actualized(via=GenericType))
class DictType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: GenericType) -> bool:
		return via.symbol.tokens == 'dict'

	@property
	@Meta.embed(Node, expandable)
	def key_type(self) -> Symbol | GenericType:
		return self._by('typed_slices.typed_slice[0]')._at(0).one_of(Symbol | GenericType)

	@property
	@override
	@Meta.embed(Node, expandable)
	def value_type(self) -> Symbol | GenericType:
		return self._by('typed_slices.typed_slice[1]')._at(0).one_of(Symbol | GenericType)


@Meta.embed(Node, accept_tags('typed_or_expr'))
class UnionType(GenericType):
	@property
	@Meta.embed(Node, expandable)
	def types(self) -> list[Symbol]:  # FIXME GenericTypeにも対応
		return [node.as_a(Symbol) for node in self._children()]


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
		return cast(Symbolization, self._ancestor('class_def')).symbol.as_a(Symbol)
