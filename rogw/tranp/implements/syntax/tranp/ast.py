from typing import TypeAlias

from rogw.tranp.implements.syntax.tranp.token import Token

TupleToken: TypeAlias = tuple[str, str]
TupleTree: TypeAlias = tuple[str, list['TupleToken | TupleTree']]
TupleEntry: TypeAlias = TupleToken | TupleTree


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

	def simplify(self) -> TupleEntry:
		"""Returns: tuple形式"""
		return self.name, self.value.string

	def pretty(self, indent: str = '  ') -> str:
		"""Returns: フォーマット書式"""
		return f"('{self.name}', '{self.value.string}')"

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}[{self.name}]: {repr(self.value.string)}>'

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

	def simplify(self) -> TupleEntry:
		"""Returns: tuple形式"""
		return self.name, [child.simplify() for child in self.children]

	def pretty(self, indent: str = '  ') -> str:
		"""Args: indent: インデント Returns: フォーマット書式"""
		children_str = f',\n{indent}'.join([f'\n{indent}'.join(child.pretty(indent).split('\n')) for child in self.children])
		return f"('{self.name}', [\n{indent}{children_str}\n])"

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}[{self.name}]: [{', '.join([f'"{child.name}"' for child in self.children])}]>'

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


ASTEntry: TypeAlias = 'ASTToken | ASTTree'
