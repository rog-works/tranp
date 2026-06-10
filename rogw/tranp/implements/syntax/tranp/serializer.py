
from typing import Any, Callable, Literal, TypeAlias

from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.lang.middleware import Middleware

ASTNormal: TypeAlias = tuple[int, str, int | str | list[int]]

IdIndex: Literal[0] = 0
IdCommand: Literal[1] = 1
IdContext: Literal[2] = 2


class ASTSerializer:
	"""ASTシリアライザー"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self._middleware = Middleware[list[ASTNormal]]()

	def on(self, name: str, callback: Callable[['ASTSerializer', ASTTree, int], list[ASTNormal]]) -> None:
		"""コールバックを登録

		Args:
			name: コマンド名
			callback: コールバック
		"""
		self._middleware.on(name, callback)

	def normalize(self, entry: ASTEntry, seq: int = 0) -> list[ASTNormal]:
		"""ASTを正規化

		Args:
			entry: ASTエントリー
			seq: 出力インデックス (default = 0)
		Returns:
			正規化したAST
		"""
		if self._middleware.usable(entry.name):
			return self._middleware.emit(entry.name, serializer=self, entry=entry, seq=seq)
		elif isinstance(entry, ASTToken):
			return self.normalize_token(entry, seq)
		else:
			return self.normalize_node(entry, seq)

	def normalize_token(self, token: ASTToken, seq: int) -> list[ASTNormal]:
		"""ASTトークンを正規化

		Args:
			token: ASTトークン
			seq: 出力インデックス
		Returns:
			正規化したAST
		"""
		return [(seq, token.name, token.value.string)]

	def normalize_node(self, tree: ASTTree, seq: int) -> list[ASTNormal]:
		"""ASTツリーを正規化

		Args:
			tree: ASTツリー
			seq: 出力インデックス
		Returns:
			正規化したAST
		"""
		entries: list[tuple[int, str, Any]] = []
		child_ids: list[int] = []
		offset = 0
		for child in tree.children:
			normalized = self.normalize(child, seq + offset)
			child_ids.append(normalized[-1][IdIndex])
			entries.extend(normalized)
			offset += len(normalized)

		tree_id = seq + offset
		entries.append((tree_id, tree.name, child_ids))
		return entries
