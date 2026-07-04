from collections.abc import Callable
from typing import NamedTuple, TypeAlias

from rogw.tranp.implements.syntax.tranp.token import Token

TupleToken: TypeAlias = tuple[str, str]
TupleTree: TypeAlias = tuple[str, list['TupleToken | TupleTree']]
TupleEntry: TypeAlias = TupleToken | TupleTree
ASTEntry: TypeAlias = 'ASTToken | ASTTree'

class ASTToken:
	"""AST(トークン)"""

	@classmethod
	def empty(cls) -> 'ASTToken':
		"""Returns: 空を表すインスタンス"""
		return cls('__empty__', Token.empty())

	def __init__(self, name: str, value: Token) -> None:
		"""インスタンスを生成

		Args:
			name: エントリー名
			value: トークン
		"""
		self._name = name
		self._value = value

	@property
	def name(self) -> str:
		"""Returns: エントリー名"""
		return self._name

	@property
	def value(self) -> Token:
		"""Returns: トークン"""
		return self._value

	def simplify(self) -> TupleToken:
		"""Returns: tuple形式"""
		return self.name, self.value.string

	def pretty(self, indent: str = '  ') -> str:
		"""Returns: フォーマット書式 XXX reprによるエスケープはNG"""
		return f"('{self.name}', '{self.value.string}')"

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}["{self.name}"]: {repr(self.value.string)}>'

	def __hash__(self) -> int:
		"""Returns: ハッシュ値"""
		return hash(self.simplify())

	def __eq__(self, other: 'ASTEntry | TupleEntry') -> bool:
		"""Args: other: 比較対象 Returns: True = 一致"""
		if isinstance(other, ASTToken):
			return self.name == other.name and self.value == other.value
		elif isinstance(other, tuple) and isinstance(other[1], str):
			return self.name == other[0] and self.value.string == other[1]
		else:
			return False

	def __ne__(self, other: 'ASTEntry | tuple[str, str]') -> bool:
		"""Args: other: 比較対象 Returns: True = 不一致"""
		return not self.__eq__(other)


class ASTTree:
	"""AST(ツリー)"""

	def __init__(self, name: str, children: list['ASTEntry']) -> None:
		"""インスタンスを生成

		Args:
			name: エントリー名
			children: 配下要素
		"""
		self._name = name
		self._children = children

	@property
	def name(self) -> str:
		"""Returns: エントリー名"""
		return self._name

	@property
	def children(self) -> list['ASTEntry']:
		"""Returns: 配下要素"""
		return self._children

	def simplify(self) -> TupleTree:
		"""Returns: tuple形式"""
		return self.name, [child.simplify() for child in self.children]

	def pretty(self, indent: str = '  ') -> str:
		"""Args: indent: インデント Returns: フォーマット書式"""
		children_str = f',\n{indent}'.join([f'\n{indent}'.join(child.pretty(indent).split('\n')) for child in self.children])
		return f"('{self.name}', [\n{indent}{children_str}\n])"

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}["{self.name}"]: [{', '.join([f'"{child.name}"' for child in self.children])}]>'

	def __hash__(self) -> int:
		"""Returns: ハッシュ値"""
		return hash(self.simplify())

	def __eq__(self, other: 'ASTEntry | TupleEntry') -> bool:
		"""Args: other: 比較対象 Returns: True = 一致"""
		if isinstance(other, ASTTree):
			return self.simplify() == other.simplify()
		elif isinstance(other, tuple) and isinstance(other[1], list):
			return self.simplify() == other
		else:
			return False

	def __ne__(self, other: 'ASTEntry | TupleEntry') -> bool:
		"""Args: other: 比較対象 Returns: True = 不一致"""
		return not self.__eq__(other)

	def normalize(self, normalizer_type: 'type[ASTNormalizer] | None' = None) -> list['ASTNormal']:
		"""ASTを正規化

		Args:
			normalizer_type: AST正規化ミドルウェアの型 (default = None)
		Returns:
			正規化したAST
		"""
		_normalizer = normalizer_type() if normalizer_type else ASTNormalizer()
		return _normalizer.normalize(self)


class ASTNormal(NamedTuple):
	"""AST正規化エントリー"""

	index: int
	name: str
	context: int | str | list[int]

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}[{self.name}]: #{self.index}, {self.context}>'

	def __str__(self) -> str:
		"""Returns: 文字列表現"""
		data = (self.index, self.name, self.context)
		return str(data)
	
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


class ASTNormalizer:
	"""AST正規化ミドルウェア"""

	Hander: TypeAlias = Callable[[ASTEntry, int], list[ASTNormal]]

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self._handlers: dict[str, ASTNormalizer.Hander] = {}

	def on(self, name: str, callback: Hander) -> None:
		"""ミドルウェアハンドラーを登録

		Args:
			name: コマンド名
			callback: ハンドラー
		"""
		self._handlers[name] = callback

	def normalize(self, entry: ASTEntry, seq: int = 0) -> list[ASTNormal]:
		"""ASTを正規化

		Args:
			entry: ASTエントリー
			seq: 出力インデックス (default = 0)
		Returns:
			正規化したAST
		"""
		if entry.name in self._handlers:
			return self._handlers[entry.name](entry, seq)
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
