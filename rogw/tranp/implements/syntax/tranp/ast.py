from typing import NamedTuple, TypeAlias

from rogw.tranp.implements.syntax.tranp.token import Token

TupleToken: TypeAlias = tuple[str, str]
TupleTree: TypeAlias = tuple[str, list['TupleToken | TupleTree']]
TupleEntry: TypeAlias = TupleToken | TupleTree


class ASTToken:
	"""AST(トークン)"""

	def __init__(self, name: str, value: Token) -> None:
		self._name = name
		self._value = value

	@property
	def name(self) -> str:
		return self._name

	@property
	def value(self) -> Token:
		return self._value

	@classmethod
	def empty(cls) -> 'ASTToken':
		"""Returns: 空を表すインスタンス"""
		return cls('__empty__', Token.empty())

	def simplify(self) -> TupleEntry:
		"""Returns: tuple形式"""
		return self.name, self.value.string

	def pretty(self, indent: str = '  ') -> str:
		"""Returns: フォーマット書式"""
		return f"('{self.name}', '{self.value.string}')"

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<ASTToken[{self.name}]: "{self.value.string}">'

	def __str__(self) -> str:
		"""Returns: 文字列表現"""
		return f'("{self.name}", "{self.value.string}")'

	def __hash__(self) -> int:
		"""Returns: ハッシュ値"""
		return hash(self.__repr__())

	def __eq__(self, other: 'ASTToken | tuple[str, str]') -> bool:
		"""Args: other: 比較対象 Returns: True = 一致"""
		if isinstance(other, ASTToken):
			return self.name == other.name and self.value == other.value
		else:
			return self.name == other[0] and self.value.string == other[1]

	def __ne__(self, other: 'ASTToken | tuple[str, str]') -> bool:
		"""Args: other: 比較対象 Returns: True = 一致"""
		return not self.__eq__(other)


class ASTTree(NamedTuple):
	"""AST(ツリー)"""

	name: str
	children: list['ASTToken | ASTTree']

	def simplify(self) -> TupleEntry:
		"""Returns: tuple形式"""
		return self.name, [child.simplify() for child in self.children]

	def pretty(self, indent: str = '  ') -> str:
		"""Args: indent: インデント Returns: フォーマット書式"""
		children_str = f',\n{indent}'.join([f'\n{indent}'.join(child.pretty(indent).split('\n')) for child in self.children])
		return f"('{self.name}', [\n{indent}{children_str}\n])"


ASTEntry: TypeAlias = 'ASTToken | ASTTree'
