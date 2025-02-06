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

	posision: int
	minimum: int
	maximum: int

	@classmethod
	def start(cls) -> 'Context':
		"""Returns: 開始時のインスタンス"""
		return cls(0, -1, -1)

	@property
	def cursor(self) -> int:
		"""Returns: 参照位置"""
		return self.posision + max(0, self.minimum)

	@property
	def accepted_recursive(self) -> bool:
		"""Returns: True = 左再帰を受け入れ"""
		return self.minimum == -1 and self.maximum == -1

	def step(self, steps: int) -> 'Context':
		"""ステップ数を加えて新規作成。ステップ数が1以上の時は暗黙的に読み取り位置の制限を解除

		Args:
			steps: 追加の進行ステップ数
		Returns:
			インスタンス
		Note:
			### ステップ進行時の制限解除の必然性
			* 読み取り位置の制限は実質的に無限再帰の抑制ために存在
			* 無限再帰が起きる条件は「同条件の繰り返し」であり、逆に言えば条件が変われば無限再帰にはならない
			* ステップの進行=条件の変化であり、制限の解除によって通常の解析条件に戻るだけで悪影響はない
		"""
		if steps == 0:
			return Context(self.posision + steps, self.minimum, self.maximum)
		else:
			return Context(self.posision + steps + max(0, self.minimum), -1, -1)

	def block_step(self, steps: int = 0, minimum: int = -1, maximum: int = -1) -> 'Context':
		"""ステップ数を加えて新規作成。作成したコンテキスト上では左再帰がブロックされる

		Args:
			steps: 追加の進行ステップ数 (default = 0)
			minimum: 読み取り位置の下限 (default = -1)
			maximum: 読み取り位置の上限 (default = -1)
		Returns:
			インスタンス
		"""
		return Context(self.posision + steps, minimum, maximum)


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
			elif pattern.op == Operators.And and context.accepted_recursive and self.rules.recursive_of(pattern[0]):
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
		# XXX 読み取り位置の上限を考慮(左再帰時) @see _match_and_recursive_first
		ok_limit = context.maximum == -1 or patterns.min_size <= context.maximum
		ok_range = context.posision + patterns.min_size <= len(tokens)
		if not (ok_limit and ok_range):
			return Step.ng(), []

		steps = 0
		children: list[ASTEntry] = []
		for index, pattern in enumerate(patterns):
			# XXX 読み取り位置の下限を考慮(左再帰時) @see _match_and_recursive_extend
			if index < context.minimum:
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
			context: 解析コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
		Returns:
			(ステップ, ASTエントリーリスト)
		Note:
			```
			### 左再帰の成立条件
			* AND条件のルールの先頭要素が左再帰の場合が対象
			### 左再帰の否定条件
			* 先頭要素以外の再帰 (同条件の繰り返しにならず無限ループに陥らないため対処が不要)
			* 1要素しか存在しない場合の再帰 (構文的に意味が無い)
			* OR条件に単独で存在する再帰 (グループ化してAND条件にすることで対処が可能なため非対応)
			```
		Examples:
			```
			recursive := rule
			// OKパターン
			rule := recursive "." name
			rule := (recursive) | other | ...
			// NGパターン
			rule := "@" recursive ...
			rule := recursive
			rule := recursive | other | ...
			```
		"""
		first_step, first_children = self._match_and_recursive_first(tokens, context, patterns, route)
		if not first_step.steping:
			return Step.ng(), []

		extend_step, extend_children = self._match_and_recursive_extend(tokens, context, patterns, route, first_children)
		if not extend_step.steping:
			return Step.ng(), []

		symbol = DSN.right(route, 1)
		if extend_children[0].name != symbol:
			return Step.ng(), []

		return Step.ok(extend_step.steps + 1), as_a(ASTTree, extend_children[0]).children

	def _match_and_recursive_first(self, tokens: list[Token], context: Context, patterns: Patterns, route: str) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(AND/左再帰/先頭要素)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: 解析コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
		Returns:
			(ステップ, ASTエントリーリスト)
		Note:
			```
			* 最小単位である1トークンでマッチングし、それを基点とする
			* 2トークン以上が最小単位だった場合は必ず失敗する XXX 要検討
			```
		"""
		first_pattern = as_a(Pattern, patterns[0])
		first_context = context.block_step(maximum=1)
		step, children = self._match_entry(tokens, first_context, first_pattern, route)
		if not step.steping:
			return Step.ng(), []

		return step, [self._unwrap_recursive_children(first_pattern, route, children)]
	
	def _match_and_recursive_extend(self, tokens: list[Token], context: Context, patterns: Patterns, route: str, step_children: list[ASTEntry]) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(AND/左再帰/先頭要素の拡張)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			context: 解析コンテキスト
			patterns: マッチングパターングループ
			route: 探索ルート
			step_children: 前段で解析済みのASTエントリーリスト
		Returns:
			(ステップ, ASTエントリーリスト)
		Note:
			```
			### 処理内容
			* マッチングの基点である先頭要素をスキップし、後続の要素とのマッチングを繰り返す
			* 本来のASTの構造から先頭要素が欠けた状態でマッチングするため、ASTを再構築
			* 繰り返す度に直前のレスポンスを内側にスタック
			### 拡張の条件
			* マッチングパターンは必ずグループである前提 (左再帰の成立条件) @see _match_and_recursive
			* 結果が期待通りの場合、必ずASTTreeが得られる
			* これに該当しない結果を得た場合はマッチング失敗と見做す (構文上の曖昧性があり、これは避けられない)
			```
		"""
		recursive_symbol = DSN.elements(route)[-2]
		first_pattern = as_a(Pattern, patterns[0])
		steps = 0
		children = step_children.copy()
		while context.cursor + steps < len(tokens):
			in_context = context.block_step(steps=steps, minimum=1)
			in_step, in_children = self._match_entry(tokens, in_context, first_pattern, route)
			if not in_step.steping:
				break

			# 解決したエントリーが再帰呼び出しを伴うルールから取得したものか確認 XXX 展開の仕様を考慮するとこの判定の確実性は怪しいため、検討の余地あり
			unwrap_entry = self._unwrap_recursive_children(first_pattern, route, in_children)
			entry_rule = self.rules[unwrap_entry.name]
			if not isinstance(entry_rule, Patterns) or recursive_symbol not in entry_rule.symbols:
				children.clear()
				break

			unwrap_tree = as_a(ASTTree, unwrap_entry)
			expect_tree = ASTTree(unwrap_tree.name, [*children, *unwrap_tree.children])
			children: list[ASTEntry] = [expect_tree]
			steps += in_step.steps

		if len(children) == 0:
			return Step.ng(), []

		return Step.ok(steps), children

	def _unwrap_recursive_children(self, first_pattern: Pattern, route: str, children: list[ASTEntry]) -> ASTEntry:
		"""再帰処理によって取得したASTエントリーから不要な階層を展開

		Args:
			first_pattern: マッチングパターン(先頭要素)
			route: 探索ルート
			children: 再帰処理中のASTエントリーリスト
		Returns:
			ASTツリー
		"""
		begin = route.rfind(first_pattern.expression)
		count = DSN.elem_counts(route[begin:])
		entry = children[0]
		candidates: list[str] = []
		for index in range(count - 1):
			if index == 0 or entry.name in candidates:
				assert isinstance(entry, ASTTree) and len(entry.children) == 1
				candidates = as_a(Patterns, self.rules[entry.name]).symbols
				entry = entry.children[0]

		return entry

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
		"""パターン(終端/非終端要素)を検証し、マッチしたトークンを返す

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
