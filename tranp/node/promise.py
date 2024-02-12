from typing import Protocol

from tranp.node.node import Node


class IDeclare:
	"""シンボルとして定義されるノードの共通インターフェイス"""

	@property
	def symbol(self) -> Node:
		"""Note: シンボル名を表すノード。実体はDeclable"""
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
