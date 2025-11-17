import re
from typing import NamedTuple

from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.implements.syntax.tranp.rule import Comps, Operators, Pattern, PatternEntry, Patterns, Repeators, Roles, Rules, Unwraps
from rogw.tranp.implements.syntax.tranp.tokenizer import ITokenizer, Token, Tokenizer
from rogw.tranp.lang.convertion import as_a


class Step:
	"""マッチングの進行ステップを管理"""

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

	def __init__(self, steping: bool, steps: int) -> None:
		"""インスタンスを生成

		Args:
			steping: True = マッチング成功
			steps: 進行ステップ数
		"""
		self._steping = steping
		self._steps = steps

	@property
	def steping(self) -> bool:
		"""Returns: True = マッチング成功"""
		return self._steping

	@property
	def steps(self) -> int:
		"""Returns: 進行ステップ数"""
		return self._steps

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}["{'OK' if self.steping else 'NG'}"]: {self.steps}>'


class Context(NamedTuple):
	"""解析コンテキスト"""

	position: int

	@classmethod
	def start(cls) -> 'Context':
		"""Returns: 開始時のインスタンス"""
		return cls(0)

	@property
	def cursor(self) -> int:
		"""Returns: 参照位置"""
		return self.position

	def step(self, steps: int) -> 'Context':
		"""ステップ数を加えて新規作成

		Args:
			steps: 追加の進行ステップ数
		Returns:
			インスタンス
		"""
		return Context(self.position + steps)


class SyntaxParser:
	"""シンタックスパーサー"""

	def __init__(self, rules: Rules, tokenizer: ITokenizer | None = None) -> None:
		"""インスタンスを生成

		Args:
			rules: ルールリスト
			tokenizer: トークンパーサー (default = None)
		"""
		self.rules = rules
		self.tokenizer = tokenizer if tokenizer else Tokenizer()

	def parse(self, source: str, entrypoint: str) -> ASTTree:
		"""ソースコードを解析し、ASTを生成

		Args:
			source: ソースコード
			entrypoint: エントリーポイントのシンボル
		Returns:
			ASTツリー
		Raises:
			ValueError: パースに失敗(最初のトークンに未到達)
		"""
		tokens = self.tokenizer.parse(source)
		length = len(tokens)
		step, entry = self._match_symbol(tokens, Context.start(), entrypoint)
		if step.steps != length:
			message = ErrorCollector(source, tokens, length - 1 - step.steps).summary()
			raise ValueError(f'Syntax parse error. First token not reached. {message}')

		return as_a(ASTTree, entry)

	def _match_symbol(self, tokens: list[Token], context: Context, route: str) -> tuple[Step, ASTEntry]:
		"""パターン(シンボル参照)を検証し、ASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: 解析コンテキスト
			symbol: シンボル
			route: 探索ルート
		Returns:
			(ステップ, ASTエントリー)
		"""
		symbol = DSN.right(route, 1)
		pattern = self.rules[symbol]
		if isinstance(pattern, Pattern) and pattern.role == Roles.Terminal:
			step, token = self._match_terminal(tokens, context, pattern, route)
			entry = ASTToken(symbol, token) if step.steping else ASTToken.empty()
			return step, entry
		else:
			step, children = self._match_entry(tokens, context, pattern, route)
			return step, self._unwrap_children(symbol, children)

	def _unwrap_children(self, symbol: str, children: list[ASTEntry]) -> ASTTree:
		"""子のASTエントリーを展開し、ASTツリーを生成

		Args:
			symbol: シンボル
			children: 配下要素
		Returns:
			ASTツリー
		"""
		unwraped: list[ASTEntry] = []
		for child in children:
			if isinstance(child, ASTToken):
				unwraped.append(child)
			elif self.rules.unwrap_by(child.name) == Unwraps.OneTime and len(child.children) == 1:
				unwraped.append(child.children[0])
			elif self.rules.unwrap_by(child.name) == Unwraps.Always:
				unwraped.extend(child.children)
			else:
				unwraped.append(child)

		return ASTTree(symbol, unwraped)

	def _match_entry(self, tokens: list[Token], context: Context, pattern: PatternEntry, route: str, allow_repeat: bool = True) -> tuple[Step, list[ASTEntry]]:
		"""パターンエントリーを検証し、ASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: 解析コンテキスト
			pattern: パターンエントリー
			route: 探索ルート
			allow_repeat: True = リピートへ遷移 (default = True)
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		if isinstance(pattern, Patterns):
			if pattern.rep != Repeators.NoRepeat and allow_repeat:
				return self._match_repeat(tokens, context, pattern, route)
			elif pattern.op == Operators.Or:
				return self._match_or(tokens, context, pattern, route)
			else:
				return self._match_and(tokens, context, pattern, route)
		else:
			if pattern.role == Roles.Terminal:
				step, _ = self._match_terminal(tokens, context, pattern, route)
				return step, []
			else:
				step, entry = self._match_symbol(tokens, context, DSN.join(route, pattern.expression))
				return step, [entry]

	def _match_or(self, tokens: list[Token], context: Context, patterns: Patterns, route: str) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(OR)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: 解析コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		for pattern in patterns:
			in_step, in_children = self._match_entry(tokens, context, pattern, route)
			if in_step.steping:
				return in_step, in_children

		return Step.ng(), []

	def _match_and(self, tokens: list[Token], context: Context, patterns: Patterns, route: str) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(AND)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: 解析コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		steps = 0
		children: list[ASTEntry] = []
		length = len(patterns)
		for i in range(length):
			index = length - 1 - i
			pattern = patterns[index]
			in_step, in_children = self._match_entry(tokens, context.step(steps), pattern, route)
			if not in_step.steping:
				return Step.ng(), []

			children.extend(in_children)
			steps += in_step.steps

		return Step.ok(steps), list(reversed(children))

	def _match_repeat(self, tokens: list[Token], context: Context, patterns: Patterns, route: str) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(リピート)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: 解析コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		assert patterns.rep != Repeators.NoRepeat, 'Must be repeated patterns'

		found = 0
		steps = 0
		children: list[ASTEntry] = []
		while context.cursor + steps < len(tokens):
			in_step, in_children = self._match_entry(tokens, context.step(steps), patterns, route, allow_repeat=False)
			if not in_step.steping:
				break

			found += 1
			steps += in_step.steps
			children.extend(in_children)

			if patterns.rep in [Repeators.OneOrZero, Repeators.OneOrEmpty]:
				break

		if found == 0:
			if patterns.rep in [Repeators.OverZero, Repeators.OneOrZero]:
				return Step.ok(0), []
			elif patterns.rep == Repeators.OneOrEmpty:
				return Step.ok(0), [ASTToken.empty()]
			else:
				return Step.ng(), []

		return Step.ok(steps), children

	def _match_terminal(self, tokens: list[Token], context: Context, pattern: Pattern, route: str) -> tuple[Step, Token]:
		"""パターン(終端/非終端記号)を検証し、マッチしたトークンを返す

		Args:
			tokens: トークンリスト
			context: 解析コンテキスト
			pattern: マッチングパターン
			route: 探索ルート
		Returns:
			(ステップ, トークン)
		"""
		if len(tokens) <= context.cursor:
			return Step.ng(), Token.empty()

		token = tokens[len(tokens) - 1 - context.cursor]
		ok = self._compare_token(token, pattern)
		return (Step.ok(1), token) if ok else (Step.ng(), Token.empty())
	
	def _compare_token(self, token: Token, pattern: Pattern) -> bool:
		"""終端/非終端記号のトークンが一致するか判定

		Args:
			token: トークン
			pattern: マッチングパターン
		Returns:
			True = 一致
		"""
		if pattern.comp == Comps.Regexp:
			return re.fullmatch(pattern.expression, token.string) is not None
		else:
			return pattern.expression == token.string


class ErrorCollector:
	"""エラー出力ユーティリティー"""

	def __init__(self, source: str, tokens: list[Token], steps: int) -> None:
		"""インスタンスを生成

		Args:
			source: ソースコード
			tokens: トークンリスト
			steps: 進行ステップ数
		"""
		self.source = source
		self.tokens = tokens
		self.steps = steps

	def summary(self) -> str:
		"""Returns: エラー概要"""
		progress = self._progress()
		lines = self._quotation_lines()
		return '\n'.join([progress, *lines])

	def _progress(self) -> str:
		"""Returns: 進捗"""
		total = len(self.tokens)
		return f'pass: {self.steps}/{total}, token: {repr(self._cause_token.string)}'

	def _quotation_lines(self) -> list[str]:
		"""Returns: 該当行の引用"""
		line_no = self._cause_source_map.begin_line + 1
		line_ns = ' ' * len(str(line_no))
		return [
			f'({line_no}) >>> {self._cause_line}',
			f' {line_ns}      {self._cause_line_mark}',
		]

	@property
	def _cause_token(self) -> Token:
		"""Returns: 該当トークン"""
		return self.tokens[self.steps]

	@property
	def _cause_source_map(self) -> Token.SourceMap:
		"""Returns: 該当トークンのソースマップ"""
		return self._cause_token.source_map

	@property
	def _cause_token_range(self) -> tuple[int, int]:
		"""Returns: 該当トークンの範囲"""
		source_map = self._cause_source_map
		diff = source_map.end_column - source_map.begin_column
		return (
			source_map.begin_column,
			source_map.begin_column + diff if source_map.begin_line == source_map.end_line else len(self._cause_line)
		)

	@property
	def _cause_line(self) -> str:
		"""Returns: 該当行"""
		lines = self.source.split('\n')
		# XXX EOFはbegin_lineが-1のため、結果的に最終行が対象となる
		return lines[self._cause_source_map.begin_line]

	@property
	def _cause_line_mark(self) -> str:
		"""Returns: 該当行のマーク"""
		begin, end = self._cause_token_range
		indent = ' ' * begin
		# XXX 改行が対象の場合、差分が0になるため最小値を設ける
		explain = '^' * max(1, end - begin)
		return f'{indent}{explain}'
