from py2cpp.lang.annotation import override
from py2cpp.node.embed import Meta, accept_tags, actualized, expansionable
from py2cpp.node.node import Node
from py2cpp.node.definition.expression import Expression
from py2cpp.node.definition.terminal import Terminal


@Meta.embed(Node, accept_tags('factor'), actualized(via=Expression))
class UnaryOperator(Node):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		if via.tag != 'factor':  # XXX accept_tagsを使う
			return False

		if via._at(0).to_string() not in ['+', '-', '~']:
			return False

		return len(via._children()) == 2

	@property
	@Meta.embed(Node, expansionable(order=0))
	def operator(self) -> Terminal:
		return self._at(0).as_a(Terminal)

	@property
	@Meta.embed(Node, expansionable(order=1))
	def value(self) -> Node:
		return self._at(1).as_a(Expression).actualize()


# @Meta.embed(Node, accept_tags('group_expr'), actualized(via=Expression))
class Group(Node):  # FIXME impl トランスパイルの性質上必要だが、あると色々と邪魔になる
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return False
