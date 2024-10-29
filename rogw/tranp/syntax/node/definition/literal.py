from typing import override

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.lang.annotation import implements
from rogw.tranp.lang.comment import Comment as CommentData
from rogw.tranp.syntax.node.behavior import IDomain, ITerminal
from rogw.tranp.syntax.node.definition.expression import Expander
from rogw.tranp.syntax.node.definition.terminal import Terminal
from rogw.tranp.syntax.node.embed import Meta, accept_tags, expandable
from rogw.tranp.syntax.node.node import Node


class Literal(Node, IDomain):
	@property
	@override
	def domain_name(self) -> str:
		# XXX 一意な名称を持たないためIDで代用
		return ModuleDSN.identify(self.literal_identifier, self.id)

	@property
	def literal_identifier(self) -> str:
		raise NotImplementedError()


@Meta.embed(Node, accept_tags('number'))
class Number(Literal, ITerminal): pass


@Meta.embed(Node)
class Integer(Number):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['number', 'DEC_NUMBER', 'HEX_NUMBER'])

	@property
	@implements
	def literal_identifier(self) -> str:
		return int.__name__

	@property
	def as_int(self) -> int:
		return int(self.tokens)


@Meta.embed(Node)
class Float(Number):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['number', 'FLOAT_NUMBER'])

	@property
	@implements
	def literal_identifier(self) -> str:
		return float.__name__

	@property
	def as_float(self) -> float:
		return float(self.tokens)


@Meta.embed(Node, accept_tags('string'))
class String(Literal, ITerminal):
	@property
	@implements
	def literal_identifier(self) -> str:
		return str.__name__

	@property
	def as_string(self) -> str:
		return self.tokens[1:-1]


@Meta.embed(Node)
class DocString(String):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		text = via.tokens
		return via._full_path.parent_tag == 'block' and text.startswith('"""') and text.endswith('"""')

	@property
	@override
	def as_string(self) -> str:
		return self.tokens[3:-3]

	@property
	def data(self) -> CommentData:
		return CommentData.parse(self.as_string)


class Boolean(Literal, ITerminal):
	@property
	@implements
	def literal_identifier(self) -> str:
		return bool.__name__


@Meta.embed(Node, accept_tags('const_true'))
class Truthy(Boolean): pass


@Meta.embed(Node, accept_tags('const_false'))
class Falsy(Boolean): pass


@Meta.embed(Node, accept_tags('key_value'))
class Pair(Literal):
	@property
	@Meta.embed(Node, expandable)
	def first(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def second(self) -> Node:
		return self._at(1)

	@property
	@implements
	def literal_identifier(self) -> str:
		return 'Pair'


@Meta.embed(Node, accept_tags('list'))
class List(Literal):
	@property
	@Meta.embed(Node, expandable)
	def values(self) -> list[Expander | Node]:
		return self._children()

	@property
	@implements
	def literal_identifier(self) -> str:
		return list.__name__


@Meta.embed(Node, accept_tags('dict'))
class Dict(Literal):
	@property
	@Meta.embed(Node, expandable)
	def items(self) -> list[Pair | Node]:
		return self._children()

	@property
	@implements
	def literal_identifier(self) -> str:
		return dict.__name__


@Meta.embed(Node, accept_tags('tuple'))
class Tuple(Literal):
	@property
	@Meta.embed(Node, expandable)
	def values(self) -> list[Node]:
		return self._children()

	@property
	@implements
	def literal_identifier(self) -> str:
		return tuple.__name__


@Meta.embed(Node, accept_tags('const_none'))
class Null(Literal, ITerminal):
	@property
	@override
	def domain_name(self) -> str:
		# XXX Noneはシングルトンであり、全て同一と見なすため識別子のみとする
		return self.literal_identifier

	@property
	@implements
	def literal_identifier(self) -> str:
		return 'None'
