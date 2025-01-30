from typing import NamedTuple, TypeAlias

from rogw.tranp.implements.syntax.tranp.token import Token


class ASTToken(NamedTuple):
	"""AST(トークン)"""

	name: str
	value: Token

	@classmethod
	def empty(cls) -> 'ASTToken':
		"""Returns: 空を表すインスタンス"""
		return cls('__empty__', Token.empty())

	def simplify(self) -> tuple[str, str | list[tuple]]:
		"""Returns: 簡易書式(tuple/str)"""
		return self.name, self.value.string

	def pretty(self, indent: str = '  ') -> str:
		"""Returns: フォーマット書式"""
		return f"('{self.name}', '{self.value.string}')"


class ASTTree(NamedTuple):
	"""AST(ツリー)"""

	name: str
	children: list['ASTToken | ASTTree']

	def simplify(self) -> tuple[str, str | list[tuple]]:
		"""Returns: 簡易書式(tuple/str)"""
		return self.name, [child.simplify() for child in self.children]

	def pretty(self, indent: str = '  ') -> str:
		"""Args: indent: インデント Returns: フォーマット書式"""
		children_str = f',\n{indent}'.join([f'\n{indent}'.join(child.pretty(indent).split('\n')) for child in self.children])
		return f"('{self.name}', [\n{indent}{children_str}\n])"


ASTEntry: TypeAlias = 'ASTToken | ASTTree'
