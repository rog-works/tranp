from py2cpp.node.embed import Meta, accept_tags, expandable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('argvalue'))
class Argument(Node):
	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node:
		return self._at(0)


@Meta.embed(Node, accept_tags('typed_argvalue'))
class InheritArgument(Node):
	@property
	@Meta.embed(Node, expandable)
	def class_type(self) -> Node:  # XXX 理想はTypeだが、参照違反になるため一旦Nodeで対応
		return self._at(0)
