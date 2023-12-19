from py2cpp.node.embed import Meta, accept_tags
from py2cpp.node.node import Node


class Terminal(Node):
	@classmethod
	def match_terminal(cls, via: Node, allow_tags: list[str]) -> bool:  # XXX
		rel_paths = [node._full_path.relativefy(via.full_path) for node in via._under_expansion()]
		for rel_path in rel_paths:
			if not rel_path.consists_of_only(*allow_tags):
				return False

		return True


@Meta.embed(Node, accept_tags('__empty__', 'const_none'))
class Empty(Node): pass


@Meta.embed(Node, accept_tags('const_none'))
class Null(Node): pass
