from rogw.tranp.ast.dsn import DSN
import rogw.tranp.compatible.python.classes as classes
from rogw.tranp.lang.comment import Comment as CommentData
from rogw.tranp.lang.implementation import implements, override
from rogw.tranp.node.definition.terminal import Terminal
from rogw.tranp.node.embed import Meta, accept_tags, actualized, expandable
from rogw.tranp.node.interface import IDomain, ITerminal
from rogw.tranp.node.node import Node


class Literal(Node, IDomain):
	@property
	@override
	def domain_name(self) -> str:
		# XXX 一意な名称を持たないためIDで代用
		return DSN.identify(self.literal_identifier, self.id)

	@property
	def literal_identifier(self) -> str:
		raise NotImplementedError()


@Meta.embed(Node, accept_tags('number'))
class Number(Literal, ITerminal): pass


@Meta.embed(Node, actualized(via=Number))
class Integer(Number):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['number', 'DEC_NUMBER', 'HEX_NUMBER'])

	@property
	@implements
	def literal_identifier(self) -> str:
		return int.__name__


@Meta.embed(Node, actualized(via=Number))
class Float(Number):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['number', 'FLOAT_NUMBER'])

	@property
	@implements
	def literal_identifier(self) -> str:
		return float.__name__


@Meta.embed(Node, accept_tags('string'))
class String(Literal, ITerminal):
	@property
	@implements
	def literal_identifier(self) -> str:
		return str.__name__

	@property
	def plain(self) -> str:
		return self.tokens[1:-1]


@Meta.embed(Node, actualized(via=String))
class DocString(String):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		text = via.tokens
		return via._full_path.parent_tag == 'block' and text.startswith('"""') and text.endswith('"""')

	@property
	@override
	def plain(self) -> str:
		return self.tokens[3:-3]

	@property
	def data(self) -> CommentData:
		return CommentData.parse(self.plain)


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
		return classes.Pair.__name__


@Meta.embed(Node, accept_tags('list'))
class List(Literal):
	@property
	@Meta.embed(Node, expandable)
	def values(self) -> list[Node]:
		return self._children()

	@property
	@implements
	def literal_identifier(self) -> str:
		return list.__name__


@Meta.embed(Node, accept_tags('dict'))
class Dict(Literal):
	@property
	@Meta.embed(Node, expandable)
	def items(self) -> list[Pair]:
		return [node.as_a(Pair) for node in self._children()]

	@property
	@implements
	def literal_identifier(self) -> str:
		return dict.__name__


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
