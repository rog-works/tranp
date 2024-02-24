from rogw.tranp.lang.implementation import override
from rogw.tranp.node.embed import Meta, accept_tags
from rogw.tranp.node.interface import IDomain, ITerminal
from rogw.tranp.node.node import Node


class Terminal(Node):
	@classmethod
	def match_terminal(cls, via: Node, allow_tags: list[str]) -> bool:  # XXX
		rel_paths = [node._full_path.relativefy(via.full_path) for node in via._under_expand()]
		for rel_path in rel_paths:
			if not rel_path.consists_of_only(*allow_tags):
				return False

		return True

	@property
	@override
	def can_expand(self) -> bool:
		"""
		Note:
			FIXME 比較演算子のみ暗黙的な展開を抑制 ※それ以外の演算子とASTの展開方式が異なるため
			FIXME 比較演算子だけ抑制すれば良いとは限らないのでTerminalとExpressionの分離を検討
		"""
		return self.tag not in ['comp_op', 'comp_in', 'comp_not_in', 'comp_is', 'comp_is_not']


@Meta.embed(Node, accept_tags('__empty__', 'const_none'))
class Empty(Node, IDomain, ITerminal):
	@property
	@override
	def domain_name(self) -> str:
		return 'Empty'
