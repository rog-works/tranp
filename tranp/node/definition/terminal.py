from tranp.lang.implementation import implements, override
from tranp.node.embed import Meta, accept_tags
from tranp.node.interface import IDomain, ITerminal
from tranp.node.node import Node


class Terminal(Node):
	@classmethod
	def match_terminal(cls, via: Node, allow_tags: list[str]) -> bool:  # XXX
		rel_paths = [node._full_path.relativefy(via.full_path) for node in via._under_expand()]
		for rel_path in rel_paths:
			if not rel_path.consists_of_only(*allow_tags):
				return False

		return True


@Meta.embed(Node, accept_tags('__empty__', 'const_none'))
class Empty(Node, IDomain, ITerminal):
	@property
	@override
	def domain_name(self) -> str:
		return 'Empty'

	@property
	@implements
	def can_expand(self) -> bool:
		return False
