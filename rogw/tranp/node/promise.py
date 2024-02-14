from typing import Protocol

from rogw.tranp.node.node import Node


class IDeclare:
	"""シンボルを保有するノードの共通インターフェイス

	Note:
		# 対象 | 1 on 1/n
		* ClassDef | 1 on 1
		* Assign | 1 on n
		* Parameter | 1 on 1
		* For | 1 on n
		* Catch | 1 on 1
		* Comprehension | 1 on n
	"""

	@property
	def symbols(self) -> list[Node]:
		"""list[Node]: シンボルとなるDeclableノードのリスト"""
		raise NotImplementedError()


class StatementBlock(Protocol):
	"""ステートメントを所持するノードの共通インターフェイス

	Note:
		# 対象
		* Entrypoint
		* Block
		* ClassDef
	"""

	@property
	def statements(self) -> list[Node]:
		"""list[Node]: ステートメントノードリスト"""
		...
