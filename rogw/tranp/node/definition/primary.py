import re
from typing import Union, cast

from rogw.tranp.ast.dsn import DSN
from rogw.tranp.errors import LogicError
from rogw.tranp.lang.implementation import implements, override
from rogw.tranp.lang.sequence import last_index_of
from rogw.tranp.node.definition.literal import Literal
from rogw.tranp.node.definition.terminal import Empty
from rogw.tranp.node.embed import Meta, accept_tags, actualized, expandable
from rogw.tranp.node.interface import IDomain, ITerminal
from rogw.tranp.node.node import Node
from rogw.tranp.node.promise import IDeclaration, ISymbol


@Meta.embed(Node, accept_tags('getattr', 'var', 'name'))
class Fragment(Node, IDomain):
	@property
	@override
	def domain_name(self) -> str:
		return self.tokens

	@property
	def is_decl_class_var(self) -> bool:
		"""Note: マッチング対象: クラス変数宣言"""
		# XXX ASTへの依存度が非常に高い判定なので注意
		# XXX 期待するパス: class_def_raw.block.anno_assign.assign_namelist.(getattr|var|name)
		elems = self._full_path.de_identify().elements
		actual_class_def_at = last_index_of(elems, 'class_def_raw')
		expect_class_def_at = max(0, len(elems) - 5)
		in_decl_class_var = actual_class_def_at == expect_class_def_at
		in_decl_var = self._full_path.de_identify().shift(-1).origin.endswith('anno_assign.assign_namelist')
		is_local = DSN.elem_counts(self.tokens) == 1
		is_receiver = self._full_path.last[1] in [0, -1]  # 代入式の左辺が対象
		return in_decl_var and in_decl_class_var and is_local and is_receiver

	@property
	def is_decl_this_var(self) -> bool:
		"""Note: マッチング対象: インスタンス変数宣言"""
		in_decl_var = self._full_path.de_identify().shift(-1).origin.endswith('anno_assign.assign_namelist')
		is_property = re.fullmatch(r'self.\w+', self.tokens) is not None
		is_receiver = self._full_path.last[1] in [0, -1]  # 代入式の左辺が対象
		return in_decl_var and is_property and is_receiver

	@property
	def is_param_class(self) -> bool:
		"""Note: マッチング対象: 仮引数(clsのみ)"""
		tokens = self.tokens
		in_decl_var = self._full_path.parent_tag == 'typedparam'
		is_class = tokens == 'cls'
		is_local = DSN.elem_counts(tokens) == 1
		return in_decl_var and is_class and is_local

	@property
	def is_param_this(self) -> bool:
		"""Note: マッチング対象: 仮引数(selfのみ)"""
		tokens = self.tokens
		in_decl_var = self._full_path.parent_tag == 'typedparam'
		is_this = tokens == 'self'
		is_local = DSN.elem_counts(tokens) == 1
		return in_decl_var and is_this and is_local

	@property
	def is_decl_local_var(self) -> bool:
		"""Note: マッチング対象: ローカル変数宣言/仮引数(cls/self以外)"""
		# For/Catch/Comprehension
		is_identified_by_name_only = self._full_path.parent_tag in ['for_namelist', 'except_clause']
		if is_identified_by_name_only and self._full_path.last_tag == 'name':
			return True

		# Parameter(cls/self以外)
		tokens = self.tokens
		in_decl_param = self._full_path.parent_tag == 'typedparam'
		is_class_or_this = tokens in ['cls', 'self']
		if in_decl_param:
			return not is_class_or_this

		# Assign
		parent_tags = self._full_path.de_identify().shift(-1).elements[-2:]
		for_assign, for_namelist = parent_tags if len(parent_tags) >= 2 else ['', '']
		in_decl_var = for_assign in ['assign', 'anno_assign'] and for_namelist == 'assign_namelist'
		is_local = DSN.elem_counts(tokens) == 1
		return in_decl_var and not is_class_or_this and is_local

	@property
	def in_decl_class_type(self) -> bool:
		return self._full_path.parent_tag in ['class_def_raw', 'function_def_raw']

	@property
	def in_decl_import(self) -> bool:
		return self._full_path.parent_tag == 'import_names'


class Declable(Fragment, ISymbol, ITerminal):
	@property
	@implements
	def symbol(self) -> 'Declable':
		return self

	@property
	@implements
	def declare(self) -> Node:
		parent_tags = ['assign_namelist', 'for_namelist', 'except_clause']
		if self._full_path.parent_tag in parent_tags and isinstance(self.parent, IDeclaration):
			return self.parent

		raise LogicError(f'Unexpected parent. node: {self}, parent: {self.parent}')


class DeclVar(Declable): pass


@Meta.embed(Node, accept_tags('var'), actualized(via=Fragment))
class DeclClassVar(DeclVar):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.is_decl_class_var


@Meta.embed(Node, accept_tags('getattr'), actualized(via=Fragment))
class DeclThisVar(DeclVar):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.is_decl_this_var

	@property
	@override
	def domain_name(self) -> str:
		return self.tokens_without_this

	@property
	@override
	def fullyname(self) -> str:
		"""Note: XXX クラス直下に配置するため例外的にスコープを調整"""
		return DSN.join(self._ancestor('class_def').scope, self.domain_name)

	@property
	def tokens_without_this(self) -> str:
		return DSN.shift(self.tokens, 1)


class DeclBlockVar(DeclVar): pass


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class DeclClassParam(DeclBlockVar):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.is_param_class

	@property
	def class_types(self) -> Node:
		return self._ancestor('class_def')


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class DeclThisParam(DeclBlockVar):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.is_param_this

	@property
	def class_types(self) -> Node:
		return self._ancestor('class_def')


@Meta.embed(Node, accept_tags('var', 'name'), actualized(via=Fragment))
class DeclLocalVar(DeclBlockVar):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.is_decl_local_var


class DeclName(Declable): pass


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class TypesName(DeclName):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.in_decl_class_type

	@property
	def class_types(self) -> Node:
		return self.parent


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class ImportName(DeclName):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.in_decl_import


class Reference(Fragment): pass


@Meta.embed(Node, accept_tags('getattr'), actualized(via=Fragment))
class Relay(Reference):
	@property
	@override
	def domain_name(self) -> str:
		return DSN.join(self.receiver.domain_name, self.prop.tokens)

	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		if via.is_decl_local_var or via.is_decl_this_var:
			return False

		if via.in_decl_class_type or via.in_decl_import:
			return False

		return True

	@property
	@Meta.embed(Node, expandable)
	def receiver(self) -> 'Reference | FuncCall | Indexer | Literal':
		return self._at(0).one_of(Reference | FuncCall | Indexer | Literal)

	@property
	def prop(self) -> 'Variable':
		return self._at(1).as_a(Variable)


class Var(Reference, ITerminal): pass


@Meta.embed(Node, accept_tags('var'), actualized(via=Fragment))
class ClassRef(Var):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.tokens == 'cls'

	@property
	def class_symbol(self) -> TypesName:
		return cast(ISymbol, self._ancestor('class_def')).symbol.as_a(TypesName)


@Meta.embed(Node, accept_tags('var'), actualized(via=Fragment))
class ThisRef(Var):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via.tokens == 'self'


@Meta.embed(Node, accept_tags('name'), actualized(via=Fragment))
class ArgumentLabel(Var):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		return via._full_path.parent_tag == 'argvalue'

	@property
	def invoker(self) -> 'FuncCall':
		return self._ancestor('funccall').as_a(FuncCall)


@Meta.embed(Node, accept_tags('var', 'name'), actualized(via=Fragment))
class Variable(Var):
	@classmethod
	def match_feature(cls, via: Fragment) -> bool:
		"""Note: XXX actualizeループの結果を元に排他的に決定(実質的なフォールバック)"""
		return True


@Meta.embed(Node, accept_tags('dotted_name'))
class Path(Node, ITerminal): pass


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
	def receiver(self) -> 'Reference | FuncCall | Indexer':
		return self._at(0).one_of(Reference | FuncCall | Indexer)

	@property
	@Meta.embed(Node, expandable)
	def key(self) -> Node:
		return self._children('slices')[0]


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
		return self._at(0).one_of(RelayOfType | VarOfType)

	@property
	def prop(self) -> Variable:
		return self._at(1).as_a(Variable)


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


@Meta.embed(Node, actualized(via=GenericType))
class ListType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: GenericType) -> bool:
		return via.type_name.tokens == 'list'

	@property
	@override
	@Meta.embed(Node, expandable)
	def value_type(self) -> Type:
		return self.primary_type


@Meta.embed(Node, actualized(via=GenericType))
class DictType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: GenericType) -> bool:
		return via.type_name.tokens == 'dict'

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


@Meta.embed(Node, actualized(via=GenericType))
class CallableType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: GenericType) -> bool:
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


@Meta.embed(Node, actualized(via=GenericType))
class CustomType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: GenericType) -> bool:
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
		return DSN.identify(self.classification, self._id())

	@property
	@Meta.embed(Node, expandable)
	def calls(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def arguments(self) -> list['Argument']:
		return [node.as_a(Argument) for node in self._children('arguments')] if self._exists('arguments') else []

	def arg_index_of(self, argument: 'Argument') -> int:
		"""Note: 無関係のノードを渡すとエラーを出力"""
		return [index for index, in_argument in enumerate(self.arguments) if in_argument == argument].pop()


@Meta.embed(Node, actualized(via=FuncCall))
class Super(FuncCall):
	@classmethod
	@override
	def match_feature(cls, via: FuncCall) -> bool:
		return via.calls.tokens == 'super'

	@property
	def super_class_symbol(self) -> Type:
		from rogw.tranp.node.definition.statement_compound import Class  # FIXME 循環参照

		decl_class = self._ancestor('class_def').as_a(Class)
		# XXX 簡易化のため単一継承と言う前提。MROは考慮せず先頭要素を直系の親クラスとする
		return decl_class.inherits[0].type_name


@Meta.embed(Node, accept_tags('argvalue'))
class Argument(Node):
	@property
	@Meta.embed(Node, expandable)
	def label(self) -> ArgumentLabel | Empty:
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
	def class_type(self) -> Type:
		return self._at(0).as_a(Type)


@Meta.embed(Node, accept_tags('elipsis'))
class Elipsis(Node, ITerminal): pass
