from enum import Enum
from io import BytesIO
import re
import token as TokenTypes
from tokenize import TokenInfo, tokenize
from typing import Iterator, NamedTuple, TypeAlias

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
		Over0: 0回以上
		Over1: 1回以上
		Bit: 0/1
		NoRepeat: リピートなし(=通常比較)
		```
	"""
	Over0 = '*'
	Over1 = '+'
	Bit = '?'
	NoRepeat = 'off'


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


class ExpandRules(Enum):
	"""ツリーの展開規則

	Note:
		* 「展開」とは、自身のツリーを削除して上位ツリーに子を展開することを指す
		```
		Off: 展開なし(通常通り)
		OneTime: 子が1つの時に展開
		```
	"""
	Off = 'off'
	OneTime = '?'
	# Always = '_' XXX 仕組み的に対応が困難なため一旦非対応


ASTEntry: TypeAlias = 'ASTToken | ASTTree'
ASTToken: TypeAlias = tuple[str, str]
ASTTree: TypeAlias = tuple[str, list['ASTToken | ASTTree']]
EmptyToken = ('__empty__', '')


class Step(NamedTuple):
	"""マッチングの進行ステップを管理"""

	steping: bool
	steps: int

	@classmethod
	def ok(cls, steps: int) -> 'Step':
		"""マッチング成功

		Args:
			steps: 進行ステップ数
		Returns:
			インスタンス
		"""
		return cls(True, steps)

	@classmethod
	def ng(cls) -> 'Step':
		"""マッチング失敗

		Returns:
			インスタンス
		"""
		return cls(False, 0)


class TokenParser:
	"""トークンパーサー"""

	@classmethod
	def parse(cls, source: str) -> list[TokenInfo]:
		"""ソースコードを解析し、トークンに分解

		Args:
			source: ソースコード
		Returns:
			トークンリスト
		"""
		# 先頭のENCODING、末尾のENDMARKERを除外
		exclude_types = [TokenTypes.ENCODING, TokenTypes.ENDMARKER]
		tokens = [token for token in tokenize(BytesIO(source.encode('utf-8')).readline) if token.type not in exclude_types]
		# 存在しない末尾の空行を削除 ※実際に改行が存在する場合は'\n'になる
		if tokens[-1].type == TokenTypes.NEWLINE and len(tokens[-1].string) == 0:
			tokens.pop()

		return tokens


class SyntaxParser:
	"""シンタックスパーサー"""

	def __init__(self, rules: dict[str, PatternEntry]) -> None:
		"""インスタンスを生成

		Args:
			rules: ルールリスト
		"""
		self.rules = rules

	def parse(self, source: str, entry: str) -> ASTEntry:
		"""ソースコードを解析し、ASTを生成

		Args:
			source: ソースコード
			entry: エントリーポイントのシンボル
		Returns:
			AST
		"""
		tokens = TokenParser.parse(source)
		return self.match(tokens, len(tokens) - 1, entry)[1]

	def match(self, tokens: list[TokenInfo], end: int, symbol: str) -> tuple[Step, ASTEntry]:
		pattern = self.rules[symbol]
		if isinstance(pattern, Patterns) and pattern.rep == Repeators.NoRepeat:
			step, children = self._match_patterns(tokens, end, pattern)
			return step, self._expand_entry(symbol, children)
		elif isinstance(pattern, Patterns):
			step, children = self._match_patterns_repeat(tokens, end, pattern)
			return step, self._expand_entry(symbol, children)
		elif pattern.role == Roles.Symbol:
			step, entry = self.match(tokens, end, pattern.expression)
			return step, self._expand_entry(symbol, [entry])
		else:
			return self.match_non_terminal(tokens, end, symbol)

	def _expand_entry(self, symbol: str, children: list[ASTEntry]) -> ASTEntry:
		if symbol[0] == ExpandRules.OneTime.value and len(children) == 1:
			return children[0]

		return symbol, children

	def _match_patterns(self, tokens: list[TokenInfo], end: int, patterns: Patterns) -> tuple[Step, list[ASTEntry]]:
		if patterns.op == Operators.Or:
			return self._match_patterns_or(tokens, end, patterns)
		else:
			return self._match_patterns_and(tokens, end, patterns)

	def _match_patterns_or(self, tokens: list[TokenInfo], end: int, patterns: Patterns) -> tuple[Step, list[ASTEntry]]:
		for pattern in patterns:
			in_step, in_children = self._match_pattern_internal(tokens, end, pattern)
			if in_step.steping:
				return in_step, in_children

		return Step.ng(), []

	def _match_patterns_and(self, tokens: list[TokenInfo], end: int, patterns: Patterns) -> tuple[Step, list[ASTEntry]]:
		steps = 0
		children: list[ASTEntry] = []
		for pattern in reversed(patterns):
			in_step, in_children = self._match_pattern_internal(tokens, end - steps, pattern)
			if not in_step.steping:
				return Step.ng(), []

			children.extend(in_children)
			steps += in_step.steps

		return Step.ok(steps), list(reversed(children))

	def _match_pattern_internal(self, tokens: list[TokenInfo], end: int, pattern: PatternEntry) -> tuple[Step, list[ASTEntry]]:
		if isinstance(pattern, Patterns) and pattern.rep == Repeators.NoRepeat:
			return self._match_patterns(tokens, end, pattern)
		elif isinstance(pattern, Patterns):
			return self._match_patterns_repeat(tokens, end, pattern)
		elif pattern.role == Roles.Symbol:
			step, entry = self.match(tokens, end, pattern.expression)
			return step, [entry]
		else:
			step, _ = self._match_terminal(tokens, end, pattern)
			return step, []

	def _match_patterns_repeat(self, tokens: list[TokenInfo], end: int, patterns: Patterns) -> tuple[Step, list[ASTEntry]]:
		found = 0
		steps = 0
		children: list[ASTEntry] = []
		while 0 <= end - steps:
			in_step, in_children = self._match_patterns(tokens, end - steps, patterns)
			if not in_step.steping:
				break

			found += 1
			steps += in_step.steps
			children.extend(in_children)

			if patterns.rep == Repeators.Bit:
				break

		if found == 0:
			if patterns.rep in [Repeators.Over0, Repeators.Bit]:
				return Step.ok(0), []
			else:
				return Step.ng(), []

		return Step.ok(steps), list(reversed(children))

	def match_non_terminal(self, tokens: list[TokenInfo], end: int, symbol: str) -> tuple[Step, ASTEntry]:
		pattern = as_a(Pattern, self.rules[symbol])
		if self._match_token(tokens[end], pattern):
			return Step.ok(1), (symbol, tokens[end].string)

		return Step.ng(), EmptyToken
	
	def _match_terminal(self, tokens: list[TokenInfo], end: int, pattern: Pattern) -> tuple[Step, ASTEntry]:
		if self._match_token(tokens[end], pattern):
			return Step.ok(1), EmptyToken

		return Step.ng(), EmptyToken

	def _match_token(self, token: TokenInfo, pattern: Pattern) -> bool:
		if pattern.comp == Comps.Regexp:
			return re.fullmatch(pattern.expression[1:-1], token.string) is not None
		else:
			return pattern.expression[1:-1] == token.string
