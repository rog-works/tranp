from typing import Protocol

from rogw.tranp.node.node import Node


class IDeclaration:
	"""シンボルを宣言するノードの共通インターフェイス

	Note:
		# 対象 | 1 on 1/n
		* ClassDef | 1 on 1
		* AnnoAssign | 1 on 1
		* MoveAssign | 1 on n
		* Parameter | 1 on 1
		* For | 1 on n
		* Catch | 1 on 1
		* Comprehension | 1 on n
	"""

	@property
	def symbols(self) -> list[Node]:
		"""list[Node]: シンボルとなるDeclableノードのリスト"""
		raise NotImplementedError()


class ISymbol:
	"""シンボルとなるノードの共通インターフェイス

	Note:
		# 対象
		* ClassDef
		* Declable
		* Parameter
	"""

	@property
	def symbol(self) -> Node:
		"""Node: シンボルへの参照"""
		raise NotImplementedError()

	@property
	def declare(self) -> Node:
		"""Node: 自身の親であるシンボル宣言ノード"""
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
