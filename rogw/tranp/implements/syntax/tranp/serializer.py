from typing import Callable, NamedTuple

from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.lang.middleware import Middleware


class ASTNormal(NamedTuple):
	"""AST正規化エントリー"""

	index: int
	name: str
	context: int | str | list[int]

	@property
	def string(self) -> str:
		"""Returns: トークン文字列 Raises: AssetionError: トークン型以外で使用"""
		assert isinstance(self.context, str)
		return self.context

	@property
	def child_ids(self) -> list[int]:
		"""Returns: 配下要素のIDリスト Raises: AssetionError: ツリー型以外で使用"""
		assert isinstance(self.context, list)
		return self.context

	@property
	def jump_at(self) -> int:
		"""Returns: ジャンプ先のインデックス Raises: AssetionError: ジャンプ型以外で使用"""
		assert isinstance(self.context, int)
		return self.context


class ASTSerializer:
	"""ASTシリアライザー"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self._middleware = Middleware[list[ASTNormal]]()

	def on(self, name: str, callback: Callable[['ASTSerializer', ASTEntry, int], list[ASTNormal]]) -> None:
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
			return self.normalize_tree(entry, seq)

	def normalize_token(self, token: ASTToken, seq: int) -> list[ASTNormal]:
		"""ASTトークンを正規化

		Args:
			token: ASTトークン
			seq: 出力インデックス
		Returns:
			正規化したAST
		"""
		return [ASTNormal(seq, token.name, token.value.string)]

	def normalize_tree(self, tree: ASTTree, seq: int) -> list[ASTNormal]:
		"""ASTツリーを正規化

		Args:
			tree: ASTツリー
			seq: 出力インデックス
		Returns:
			正規化したAST
		"""
		entries: list[ASTNormal] = []
		child_ids: list[int] = []
		offset = 0
		for child in tree.children:
			normalized = self.normalize(child, seq + offset)
			child_ids.append(normalized[-1].index)
			entries.extend(normalized)
			offset += len(normalized)

		tree_id = seq + offset
		entries.append(ASTNormal(tree_id, tree.name, child_ids))
		return entries
