import re
from typing import NamedTuple

from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.implements.syntax.tranp.rule import Comps, Unwraps, Operators, Pattern, PatternEntry, Patterns, Repeators, Roles, Rules
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

	pos: int
	min: int
	max: int

	@classmethod
	def start(cls) -> 'Context':
		"""Returns: 開始時のインスタンス"""
		return cls(0, -1, -1)

	@property
	def cursor(self) -> int:
		"""Returns: 参照位置"""
		return self.pos + max(0, self.min)

	@property
	def accepted_recursive(self) -> bool:
		"""Returns: True = 左再帰を受け入れ"""
		return self.min == -1 and self.max == -1

	def step(self, step: int) -> 'Context':
		"""ステップ数を加えて新規作成

		Args:
			step: 追加の進行ステップ数
		Returns:
			インスタンス
		"""
		if step == 0:
			return Context(self.pos + step, self.min, self.max)
		else:
			return Context(self.pos + step + max(0, self.min), -1, -1)


class SyntaxParser:
	"""シンタックスパーサー

	Note:
		```
		### 特記事項
		* ソースの末尾から先頭に向かって解析する
		* Grammar上のAND条件は右から順に評価する
		* Grammar上のOR条件は左から順に評価する
		* 左再帰による無限ループは抑制されない
		* 左再帰する場合は必ず先に別の条件を評価しなければならない
		```
	"""

	def __init__(self, rules: Rules, tokenizer: ITokenizer | None = None) -> None:
		"""インスタンスを生成

		Args:
			rules: ルールリスト
			tokenizer: トークンパーサー (default = None)
		"""
		self.rules = rules
		self.tokenizer = tokenizer if tokenizer else Tokenizer()

	def parse(self, source: str, entrypoint: str) -> ASTEntry:
		"""ソースコードを解析し、ASTを生成

		Args:
			source: ソースコード
			entrypoint: エントリーポイントのシンボル
		Returns:
			ASTエントリー XXX 要件的にほぼツリーであることが確定
		Raises:
			ValueError: パースに失敗(最初のトークンに未到達)
		"""
		tokens = self.tokenizer.parse(source)
		length = len(tokens)
		step, entry = self._match_symbol(tokens, Context.start(), entrypoint)
		if step.steps != length:
			message = ErrorCollector(source, tokens, step.steps).summary()
			raise ValueError(f'Syntax parse error. Last token not reached. {message}')

		return entry

	def _match_symbol(self, tokens: list[Token], context: Context, route: str) -> tuple[Step, ASTEntry]:
		"""パターン(シンボル参照)を検証し、ASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: コンテキスト
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
			context: コンテキスト
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
			elif pattern.op == Operators.And and context.accepted_recursive and self.rules.recursive_by(pattern[0]):
				return self._match_and_recursive(tokens, context, pattern, route)
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
			context: コンテキスト
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
			context: コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		passed = context.max == -1 or patterns.size <= context.max
		inside = context.cursor + patterns.size < len(tokens)
		if not (passed and inside):
			return Step.ng(), []

		steps = 0
		children: list[ASTEntry] = []
		for index, pattern in enumerate(patterns):
			if index < context.min:
				continue

			in_step, in_children = self._match_entry(tokens, context.step(steps), pattern, route)
			if not in_step.steping:
				return Step.ng(), []

			children.extend(in_children)
			steps += in_step.steps

		return Step.ok(steps), children

	def _match_and_recursive(self, tokens: list[Token], context: Context, patterns: Patterns, route: str) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(AND/左再帰)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		first_step, first_children = self._match_and_recursive_first(tokens, context, patterns, route)
		if not first_step.steping or first_step.steps != 1:
			raise ValueError(f'Unexpected result. step: {first_step.__repr__()}, context: {context}, route: {route}')

		extend_step, extend_children = self._match_and_recursive_extend(tokens, context, patterns, route, first_children)
		if not extend_step.steping:
			return Step.ng(), []

		step, children = self._match_and_recursive_remain(tokens, context.step(extend_step.steps), patterns, route, extend_children)
		if not step.steping:
			return Step.ng(), []

		return Step.ok(extend_step.steps + step.steps + 1), children

	def _match_and_recursive_first(self, tokens: list[Token], context: Context, patterns: Patterns, route: str) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(AND/左再帰/先頭要素)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		first_pattern = as_a(Pattern, patterns[0])
		first_context = Context(context.pos, -1, 1)
		step, children = self._match_entry(tokens, first_context, first_pattern, route)
		return step, self._unwarp_recursive_children(first_pattern, route, children)
	
	def _match_and_recursive_extend(self, tokens: list[Token], context: Context, patterns: Patterns, route: str, step_children: list[ASTEntry]) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(AND/左再帰/先頭要素の拡張)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
			step_children: 解析済みのASTエントリーリスト
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		first_pattern = as_a(Pattern, patterns[0])
		steps = 0
		children = step_children.copy()
		symbol = DSN.right(route, 1)
		while context.cursor + steps < len(tokens):
			in_context = Context(context.pos + steps, 1, -1)
			in_step, in_children = self._match_entry(tokens, in_context, first_pattern, route)
			if not in_step.steping:
				break

			unwrapped = self._unwarp_recursive_children(first_pattern, route, in_children)
			children: list[ASTEntry] = [ASTTree(symbol, [*children, *unwrapped])]
			steps += in_step.steps

		if len(children) == 0:
			return Step.ng(), []

		return Step.ok(steps), children

	def _match_and_recursive_remain(self, tokens: list[Token], context: Context, patterns: Patterns, route: str, step_children: list[ASTEntry]) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(AND/左再帰/後続要素)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
			step_children: 解析済みのASTエントリーリスト
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		steps = 0
		children = step_children.copy()
		for index, in_pattern in enumerate(patterns):
			if index < 1:
				continue

			in_context = Context(context.pos + steps, 1, -1)
			in_step, in_children = self._match_entry(tokens, in_context, in_pattern, route)
			if not in_step.steping:
				return Step.ng(), []

			children.extend(in_children)
			steps += in_step.steps

		return Step.ok(steps), children

	def _unwarp_recursive_children(self, first_pattern: Pattern, route: str, children: list[ASTEntry]) -> list[ASTEntry]:
		"""再帰処理によって取得したASTエントリーから不要な階層を展開

		Args:
			first_pattern: マッチングパターン(先頭要素)
			route: 探索ルート
			children: 再帰処理中のASTエントリーリスト
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		symbol = DSN.right(route, 1)
		index = route.find(first_pattern.expression)
		routes = DSN.elements(route[index:])
		unwrapped = children
		for index, elem in enumerate(routes):
			if unwrapped[0].name != elem:
				continue

			if symbol == elem or self.rules.unwrap_by(elem) != Unwraps.Off:
				assert unwrapped[0].name == elem and isinstance(unwrapped[0], ASTTree)
				unwrapped = unwrapped[0].children

		return unwrapped

	def _match_repeat(self, tokens: list[Token], context: Context, patterns: Patterns, route: str) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(リピート)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
		Returns:
			(ステップ, ASTエントリーリスト)
		Raises:
			AssertionError: リピートなしのグループを指定
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
		"""パターン(終端/非終端要素)を検証し、マッチしたトークンを返す

		Args:
			tokens: トークンリスト
			context: コンテキスト
			pattern: マッチングパターン
			route: 探索ルート
		Returns:
			(ステップ, トークン)
		Note:
			```
			XXX トークン参照時の境界チェックはこのメソッド内でのみ行う
			XXX この制約に伴い、トークン参照、及び境界チェックはこのメソッド以外では基本的に実施しないものとする
			```
		"""
		if len(tokens) <= context.cursor:
			return Step.ng(), Token.empty()

		token = tokens[context.cursor]
		ok = self._compare_token(token, pattern)
		return (Step.ok(1), token) if ok else (Step.ng(), Token.empty())
	
	def _compare_token(self, token: Token, pattern: Pattern) -> bool:
		"""終端/非終端要素のトークンが一致するか判定

		Args:
			token: トークン
			pattern: マッチングパターン
		Returns:
			True = 一致
		"""
		if pattern.comp == Comps.Regexp:
			return re.fullmatch(pattern.expression[1:-1], token.string) is not None
		else:
			return pattern.expression[1:-1] == token.string


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
