from py2cpp.ast.dsn import DSN
from py2cpp.lang.implementation import implements
from py2cpp.node.definition.terminal import Terminal
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.interface import IDomainName, ITerminal
from py2cpp.node.node import Node


class Literal(Node, ITerminal, IDomainName):
	@property
	@implements
	def can_expand(self) -> bool:
		return False

	@property
	@implements
	def fullyname(self) -> str:
		return DSN.join(self.scope, self.domain_name)


@Meta.embed(Node, accept_tags('number'))
class Number(Literal): pass


@Meta.embed(Node, actualized(via=Number))
class Integer(Number):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['number', 'DEC_NUMBER', 'HEX_NUMBER'])

	@property
	@implements
	def domain_name(self) -> str:
		return 'int'


@Meta.embed(Node, actualized(via=Number))
class Float(Number):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['number', 'FLOAT_NUMBER'])

	@property
	@implements
	def domain_name(self) -> str:
		return 'float'


@Meta.embed(Node, accept_tags('string'))
class String(Literal):
	@property
	@implements
	def domain_name(self) -> str:
		return 'str'

	@property
	def plain(self) -> str:
		return self.tokens[1:-1]


class Boolean(Literal):
	@property
	@implements
	def domain_name(self) -> str:
		return 'bool'


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
	def can_expand(self) -> bool:
		return True

	@property
	@implements
	def domain_name(self) -> str:
		return 'pair_'


@Meta.embed(Node, accept_tags('list'))
class List(Literal):
	@property
	@Meta.embed(Node, expandable)
	def values(self) -> list[Node]:
		return self._children()

	@property
	@implements
	def can_expand(self) -> bool:
		return True

	@property
	@implements
	def domain_name(self) -> str:
		return 'list'


@Meta.embed(Node, accept_tags('dict'))
class Dict(Literal):
	@property
	@Meta.embed(Node, expandable)
	def items(self) -> list[Pair]:
		return [node.as_a(Pair) for node in self._children()]

	@property
	@implements
	def can_expand(self) -> bool:
		return True

	@property
	@implements
	def domain_name(self) -> str:
		return 'dict'


@Meta.embed(Node, accept_tags('const_none'))
class Null(Literal):
	@property
	@implements
	def domain_name(self) -> str:
		return 'None'
