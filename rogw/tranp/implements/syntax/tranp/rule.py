from collections.abc import Mapping
from enum import Enum
from typing import Iterator, TypeAlias, ValuesView

from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.lang.convertion import as_a


class Roles(Enum):
	"""パターンの役割

	Note:
		```
		Symbol: シンボル
		Terminal: 終端要素
		```
	"""
	Symbol = 'symbol'
	Terminal = 'terminal'


class Comps(Enum):
	"""文字列の比較メソッド

	Note:
		```
		Regexp: 正規表現(完全一致)
		Equals: 通常比較
		NoComp: 使わない
		```
	"""
	Regexp = 'regexp'
	Equals = 'equals'
	NoComp = 'off'


class Operators(Enum):
	"""比較演算子(マッチンググループ用)

	Note:
		```
		And: 論理積
		Or: 論理和
		```
	"""
	And = 'and'
	Or = 'or'


class Repeators(Enum):
	"""リピート種別(マッチンググループ用)

	Note:
		```
		OverZero: 0回以上
		OverOne: 1回以上
		OneOrZero: 1/0
		OneOrEmpty: 1/Empty
		NoRepeat: リピートなし(=通常比較)
		```
	"""
	OverZero = '*'
	OverOne = '+'
	OneOrZero = '?'
	OneOrEmpty = '[]'
	NoRepeat = 'off'


class Expandors(Enum):
	"""ツリーの展開種別

	Note:
		「展開」とは、自身のツリーを削除して上位ツリーに子を展開することを指す
		```
		Off: 展開なし(通常通り)
		OneTime: 子が1つの時に展開
		```
	"""
	Off = 'off'
	OneTime = '?'
	# Always = '_' XXX 仕組み的に対応が困難なため一旦非対応


PatternEntry: TypeAlias = 'Pattern | Patterns'


class Pattern:
	"""マッチングパターン"""

	def __init__(self, expression: str, role: Roles, comp: Comps) -> None:
		"""インスタンスを生成

		Args:
			expression: マッチング式
			role: パターンの役割
			comp: 文字列の比較メソッド
		"""
		self.expression = expression
		self.role = role
		self.comp = comp

	@classmethod
	def S(cls, expression: str) -> 'Pattern':
		"""インスタンスを生成(シンボル用)

		Args:
			expression: マッチング式
		Returns:
			インスタンス
		"""
		return cls(expression, Roles.Symbol, Comps.NoComp)

	@classmethod
	def T(cls, expression: str) -> 'Pattern':
		"""インスタンスを生成(終端要素用)

		Args:
			expression: マッチング式
		Returns:
			インスタンス
		"""
		comp = Comps.Regexp if expression[0] == '/' else Comps.Equals
		return cls(expression, Roles.Terminal, comp)


class Patterns:
	"""マッチングパターングループ"""

	def __init__(self, entries: list[PatternEntry], op: Operators = Operators.And, rep: Repeators = Repeators.NoRepeat) -> None:
		"""インスタンスを生成

		Args:
			entries: 配下要素
			op: 比較演算子
			rep: リピート種別
		"""
		self.entries = entries
		self.op = op
		self.rep = rep

	def __len__(self) -> int:
		"""Returns: 要素数"""
		return len(self.entries)

	def __iter__(self) -> Iterator[PatternEntry]:
		"""Returns: イテレーター"""
		for child in self.entries:
			yield child

	def __getitem__(self, index: int) -> PatternEntry:
		"""配下要素を取得

		Args:
			index: インデックス
		Returns:
			配下要素
		"""
		return self.entries[index]


class Rules(Mapping):
	"""ルール管理

	Note:
		```
		### 名前の定義
		* symbol: 左辺の名前
		* pattern: 右辺の条件式
		* rule: symbolとpatternのペア
		```
	"""

	def __init__(self, rules: dict[str, PatternEntry]) -> None:
		"""インスタンスを生成

		Args:
			rules: ルール一覧
		"""
		super().__init__()
		self._rules = rules

	def __len__(self) -> int:
		"""Returns: 要素数"""
		return len(self._rules)

	def __iter__(self) -> Iterator[str]:
		"""Returns: イテレーター(シンボル名)"""
		return self.keys()

	def __getitem__(self, symbol: str) -> PatternEntry:
		"""パターンを取得

		Args:
			symbol: シンボル名
		Returns:
			パターン
		"""
		if symbol in self._rules:
			return self._rules[symbol]
		else:
			return self._rules[f'{Expandors.OneTime.value}{symbol}']

	def keys(self) -> Iterator[str]:
		"""Returns: イテレーター(シンボル名)"""
		for key in self._rules.keys():
			yield key[1:] if key[0] == Expandors.OneTime.value else key

	def values(self) -> ValuesView[PatternEntry]:
		"""Returns: イテレーター(パターン)"""
		return self._rules.values()

	def items(self) -> Iterator[tuple[str, PatternEntry]]:
		"""Returns: イテレーター(シンボル名, パターン)"""
		for key, rule in self._rules.items():
			key_ = key[1:] if key[0] == Expandors.OneTime.value else key
			yield key_, rule

	def expand_by(self, symbol: str) -> Expandors:
		"""指定のシンボルの展開ルールを取得

		Args:
			symbol: シンボル名
		Returns:
			展開ルール
		"""
		if symbol in self._rules:
			return Expandors.Off
		else:
			return Expandors.OneTime

	@classmethod
	def from_ast(cls, tree: ASTTree) -> 'Rules':
		return SerializeAST.restore(tree)


class SerializeAST:
	@classmethod
	def restore(cls, tree: ASTTree) -> 'Rules':
		assert tree.name == 'entry', f'Must be name is "entry" from "{tree.name}"'

		rules = dict([cls._for_rule(as_a(ASTTree, child)) for child in tree.children])
		return Rules(rules)

	@classmethod
	def _for_rule(cls, tree: ASTTree) -> tuple[str, PatternEntry]:
		assert tree.name == 'rule', f'Must be name is "rule" from "{tree.name}"'

		expand = cls._fetch_token(tree, 0, 'expand')
		symbol = cls._fetch_token(tree, 1, 'symbol')
		expr = cls._for_expr(tree.children[2])
		return f'{expand.value.string}{symbol.name}', expr

	@classmethod
	def _for_expr(cls, entry: ASTEntry) -> PatternEntry:
		if isinstance(entry, ASTToken):
			if entry.name == 'symbol':
				return cls._for_expr_symbol(entry)
			elif entry.name in ['string', 'regexp']:
				return cls._for_expr_terminal(entry)
		else:
			if entry.name == 'terms':
				return cls._for_expr_terms(entry)
			elif entry.name == 'terms_or':
				return cls._for_expr_terms_or(entry)
			elif entry.name == 'expr_opt':
				return cls._for_expr_opt(entry)
			elif entry.name == 'expr_rep':
				return cls._for_expr_rep(entry)

		assert False, f'Never. Undetermine expr entry. from "{entry.name}"'

	@classmethod
	def _for_expr_symbol(cls, token: ASTToken) -> Pattern:
		return Pattern.S(token.value.string)

	@classmethod
	def _for_expr_terminal(cls, token: ASTToken) -> Pattern:
		return Pattern.T(token.value.string)

	@classmethod
	def _for_expr_terms(cls, tree: ASTTree) -> Patterns:
		return Patterns([cls._for_expr(child) for child in tree.children])

	@classmethod
	def _for_expr_terms_or(cls, tree: ASTTree) -> Patterns:
		return Patterns([cls._for_expr(child) for child in tree.children], op=Operators.Or)

	@classmethod
	def _for_expr_opt(cls, tree: ASTTree) -> Patterns:
		return Patterns([cls._for_expr(child) for child in tree.children], rep=Repeators.OneOrEmpty)

	@classmethod
	def _for_expr_rep(cls, tree: ASTTree) -> Patterns:
		repeat = cls._fetch_token(tree, -1, 'repeat')
		assert repeat.value.string in '*+?', f'Invalid repeat value. expected for ("*", "+", "?") from "{repeat.value.string}"'

		rep = Repeators(repeat.value.string)
		expr_num = len(tree.children) - 1
		return Patterns([cls._for_expr(tree.children[i]) for i in range(expr_num)], rep=rep)

	@classmethod
	def _fetch_token(cls, tree: ASTTree, index: int, expected: str) -> ASTToken:
		token = as_a(ASTToken, tree.children[index])
		assert token.name == expected, f'Must be token name is "{token.name}" from {token.name}'
		return token
