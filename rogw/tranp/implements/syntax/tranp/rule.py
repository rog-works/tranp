from collections.abc import Mapping
from enum import Enum
from typing import Iterator, TypeAlias, ValuesView, cast

from rogw.tranp.implements.syntax.tranp.ast import TupleEntry, TupleToken, TupleTree
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
	"""ルールリスト管理

	Note:
		```
		### 呼称の定義
		* symbol: 左辺の名前
		* pattern: 右辺の条件式
		* rule: symbolとpatternのペア
		```
	"""

	@classmethod
	def from_ast(cls, tree: TupleTree) -> 'Rules':
		"""ASTツリーからインスタンスを復元

		Args:
			tree: ASTツリー
		Returns:
			インスタンス
		"""
		return ASTSerializer.restore(tree)

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

	def org_symbols(self) -> Iterator[str]:
		"""Returns: イテレーター(オリジナルのシンボル名)"""
		for key in self._rules.keys():
			yield key

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

	def pretty(self) -> str:
		"""Returns: フォーマット文字列"""
		return Prettier.pretty(self)


class Prettier:
	"""フォーマットユーティリティー"""

	@classmethod
	def pretty(cls, rules: Rules) -> str:
		"""ルールリストをフォーマット

		Args:
			rules: ルールリスト
		Returns:
			フォーマット文字列
		"""
		return '\n'.join([cls._pretty_rule(org_symbol, rules[org_symbol]) for org_symbol in rules.org_symbols()])

	@classmethod
	def _pretty_rule(cls, org_symbol: str, pattern: PatternEntry) -> str:
		"""ルールをフォーマット

		Args:
			org_symbol: オリジナルのシンボル名
			pattern: マッチングパターンエントリー
		Returns:
			フォーマット文字列
		"""
		return f'{org_symbol} := {cls._pretty_pattern_entry(pattern)}'

	@classmethod
	def _pretty_pattern_entry(cls, pattern: PatternEntry) -> str:
		"""パターンエントリーをフォーマット

		Args:
			pattern: マッチングパターンエントリー
		Returns:
			フォーマット文字列
		"""
		if isinstance(pattern, Pattern):
			return cls._pretty_pattern(pattern)
		elif isinstance(pattern, Patterns):
			return cls._pretty_patterns(pattern)

	@classmethod
	def _pretty_pattern(cls, pattern: Pattern) -> str:
		"""パターンをフォーマット

		Args:
			pattern: マッチングパターン
		Returns:
			フォーマット文字列
		"""
		return f'{pattern.expression}'

	@classmethod
	def _pretty_patterns(cls, patterns: Patterns) -> str:
		"""パターングループをフォーマット

		Args:
			pattern: マッチングパターングループ
		Returns:
			フォーマット文字列
		"""
		if patterns.op == Operators.And:
			return cls._pretty_patterns_and(patterns)
		else:
			return cls._pretty_patterns_or(patterns)

	@classmethod
	def _pretty_patterns_and(cls, patterns: Patterns) -> str:
		"""パターングループをフォーマット(AND)

		Args:
			pattern: マッチングパターングループ
		Returns:
			フォーマット文字列
		"""
		pretty_patterns = ' '.join([cls._pretty_pattern_entry(pattern) for pattern in patterns.entries])
		return cls._deco_repeat(pretty_patterns, patterns.rep)

	@classmethod
	def _pretty_patterns_or(cls, patterns: Patterns) -> str:
		"""パターングループをフォーマット(OR)

		Args:
			pattern: マッチングパターングループ
		Returns:
			フォーマット文字列
		"""
		pretty_patterns = ' | '.join([cls._pretty_pattern_entry(pattern) for pattern in patterns.entries])
		return cls._deco_repeat(pretty_patterns, patterns.rep)

	@classmethod
	def _deco_repeat(cls, pretty_patterns: str, rep: Repeators) -> str:
		"""パターングループのフォーマットにリピートを付与

		Args:
			pretty_patterns: フォーマット文字列
			rep: リピート種別
		Returns:
			付与後の文字列
		"""
		if rep == Repeators.NoRepeat:
			return pretty_patterns
		elif rep == Repeators.OneOrEmpty:
			return f'[{pretty_patterns}]'
		else:
			return f'{pretty_patterns}{rep.value}'


class ASTSerializer:
	"""シリアライザー(AST)"""

	@classmethod
	def restore(cls, tree: TupleTree) -> 'Rules':
		"""ASTツリーからルールリストを復元

		Args:
			tree: ASTツリー
		Returns:
			ルールリスト
		"""
		assert cls._name(tree) == 'entry', f'Must be name is "entry" from "{cls._name(tree)}"'

		rules = dict([cls._for_rule(cls._as_tree(child)) for child in cls._children(tree)])
		return Rules(rules)

	@classmethod
	def _for_rule(cls, tree: TupleTree) -> tuple[str, PatternEntry]:
		"""ASTツリーからルールを復元

		Args:
			tree: ASTツリー
		Returns:
			(シンボル名, マッチングパターンエントリー)
		"""
		assert cls._name(tree) == 'rule', f'Must be name is "rule" from "{cls._name(tree)}"'

		expand = cls._fetch_token(tree, 0, 'expand', allow_empty=True)
		symbol = cls._fetch_token(tree, 1, 'symbol')
		expr = cls._for_expr(cls._children(tree)[2])
		return f'{cls._value(expand)}{cls._value(symbol)}', expr

	@classmethod
	def _for_expr(cls, entry: TupleEntry) -> PatternEntry:
		"""ASTエントリーからパターンを復元

		Args:
			entry: ASTエントリー
		Returns:
			マッチングパターンエントリー
		"""
		name = cls._name(entry)
		if isinstance(entry[1], str):
			token = cls._as_token(entry)
			if name == 'symbol':
				return cls._for_expr_symbol(token)
			elif name in ['string', 'regexp']:
				return cls._for_expr_terminal(token)
		else:
			tree = cls._as_tree(entry)
			if name == 'terms':
				return cls._for_expr_terms(tree)
			elif name == 'terms_or':
				return cls._for_expr_terms_or(tree)
			elif name == 'expr_opt':
				return cls._for_expr_opt(tree)
			elif name == 'expr_rep':
				return cls._for_expr_rep(tree)

		assert False, f'Never. Undetermine expr entry. from "{name}"'

	@classmethod
	def _for_expr_symbol(cls, token: TupleToken) -> Pattern:
		"""ASTトークンからパターンを復元(シンボル)

		Args:
			token: ASTトークン
		Returns:
			マッチングパターン
		"""
		return Pattern.S(cls._value(token))

	@classmethod
	def _for_expr_terminal(cls, token: TupleToken) -> Pattern:
		"""ASTトークンからパターンを復元(終端要素)

		Args:
			token: ASTトークン
		Returns:
			マッチングパターン
		"""
		return Pattern.T(cls._value(token))

	@classmethod
	def _for_expr_terms(cls, tree: TupleTree) -> Patterns:
		"""ASTツリーからパターングループを復元(AND)

		Args:
			tree: ASTツリー
		Returns:
			マッチングパターングループ
		"""
		return Patterns([cls._for_expr(child) for child in cls._children(tree)])

	@classmethod
	def _for_expr_terms_or(cls, tree: TupleTree) -> Patterns:
		"""ASTツリーからパターングループを復元(OR)

		Args:
			tree: ASTツリー
		Returns:
			マッチングパターングループ
		"""
		return Patterns([cls._for_expr(child) for child in cls._children(tree)], op=Operators.Or)

	@classmethod
	def _for_expr_opt(cls, tree: TupleTree) -> Patterns:
		"""ASTツリーからパターングループを復元(リピート/[])

		Args:
			tree: ASTツリー
		Returns:
			マッチングパターングループ
		"""
		return Patterns([cls._for_expr(child) for child in cls._children(tree)], rep=Repeators.OneOrEmpty)

	@classmethod
	def _for_expr_rep(cls, tree: TupleTree) -> Patterns:
		"""ASTツリーからパターングループを復元(リピート/*+?)

		Args:
			tree: ASTツリー
		Returns:
			マッチングパターングループ
		"""
		repeat = cls._fetch_token(tree, -1, 'repeat')
		rep_value = cls._value(repeat)
		assert rep_value in '*+?', f'Invalid repeat value. expected for ("*", "+", "?") from "{rep_value}"'

		rep = Repeators(rep_value)
		expr_num = len(cls._children(tree)) - 1
		return Patterns([cls._for_expr(cls._children(tree)[i]) for i in range(expr_num)], rep=rep)

	@classmethod
	def _fetch_token(cls, tree: TupleTree, index: int, expected: str, allow_empty: bool = False) -> TupleToken:
		"""ASTツリーの配下から指定のASTトークンを取得

		Args:
			tree: ASTツリー
			index: インデックス
			expected: エントリー名
			allow_empty: True = 空の要素を許可 (default = False)
		Returns:
			ASTトークン
		"""
		token = cls._as_token(cls._children(tree)[index])
		assert cls._name(token) == expected or allow_empty, f'Must be token name is "{expected}" from {cls._name(token)}'
		return token

	@classmethod
	def _name(cls, entry: TupleEntry) -> str:
		"""ASTエントリーからエントリー名を取得

		Args:
			entry: ASTエントリー
		Returns:
			エントリー名
		"""
		return entry[0]

	@classmethod
	def _value(cls, entry: TupleEntry) -> str:
		"""ASTエントリーからトークンの値を取得

		Args:
			entry: ASTエントリー
		Returns:
			トークンの値
		"""
		return as_a(str, entry[1])

	@classmethod
	def _children(cls, entry: TupleEntry) -> list[TupleEntry]:
		"""ASTエントリーから配下要素を取得

		Args:
			entry: ASTエントリー
		Returns:
			配下要素
		"""
		return as_a(list, entry[1])

	@classmethod
	def _as_token(cls, entry: TupleEntry) -> TupleToken:
		"""ASTエントリーをASTトークンにキャスト

		Args:
			entry: ASTエントリー
		Returns:
			ASTトークン
		"""
		assert isinstance(entry[1], str), f'Must be token. name: {cls._name(entry)}'
		return cast(TupleToken, entry)

	@classmethod
	def _as_tree(cls, entry: TupleEntry) -> TupleTree:
		"""ASTエントリーをASTツリーにキャスト

		Args:
			entry: ASTエントリー
		Returns:
			ASTツリー
		"""
		assert isinstance(entry[1], list), f'Must be tree. name: {cls._name(entry)}'
		return cast(TupleTree, entry)
