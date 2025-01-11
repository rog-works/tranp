from typing import Protocol

from rogw.tranp.syntax.node.node import Node


class IDeclaration:
	"""シンボルを宣言するノードの共通インターフェイス

	Note:
		# 対象 | 1 on 1/n
		* ClassDef | 1 on 1
		* AnnoAssign | 1 on 1
		* MoveAssign | 1 on n
		* Import | 1 on n
		* Parameter | 1 on 1
		* For | 1 on n
		* Catch | 1 on 1
		* WithEntry | 1 on 1
		* Comprehension | 1 on n
	"""

	@property
	def symbols(self) -> list[Node]:
		"""Returns: シンボルとなるDeclableノードのリスト"""
		raise NotImplementedError()


class ISymbol:
	"""シンボルとなるノードの共通インターフェイス

	Note:
		# 対象 | 宣言 | シンボル
		* ClassDef | o | o
		* Declable | x | o
		* Parameter | o | o
	"""

	@property
	def symbol(self) -> Node:
		"""Note: 自身、または配下のシンボルノード"""
		raise NotImplementedError()

	@property
	def declare(self) -> Node:
		"""Note: 自身、または親であるシンボル宣言ノード"""
		raise NotImplementedError()


class StatementBlock(Protocol):
	"""ステートメントを所持するノードの共通インターフェイス

	Note:
		# 対象
		* Entrypoint
		* Block
		* ClassDef
		* If/ElseIf/Else
		* For/While
		* Try/Catch
		* With
	"""

	@property
	def statements(self) -> list[Node]:
		"""Returns: ステートメントノードリスト"""
		...
