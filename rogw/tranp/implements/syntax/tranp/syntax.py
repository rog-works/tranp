import re

from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.implements.syntax.tranp.rule import Comps, Expandors, Operators, Pattern, PatternEntry, Patterns, Repeators, Roles, Rules
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
		return f'<{self.__class__.__name__}[{"OK" if self.steping else "NG"}]: {self.steps}>'


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
		step, entry = self._match_symbol(tokens, length - 1, entrypoint)
		if step.steps != length:
			raise ValueError(f'Syntax parse error. First token not reached. step: {step.steps}/{length}. token: {tokens[max(0, length - step.steps - 1)]}')

		return entry

	def _match_symbol(self, tokens: list[Token], end: int, symbol: str) -> tuple[Step, ASTEntry]:
		"""パターン(シンボル参照)を検証し、ASTエントリーを生成

		Args:
			tokens: トークンリスト
			end: 評価開始位置
			symbol: シンボル
		Returns:
			(ステップ, ASTエントリー)
		"""
		pattern = self.rules[symbol]
		if isinstance(pattern, Pattern) and pattern.role == Roles.Terminal:
			# 非終端要素
			ok = self._compare_terminal(tokens[end], pattern)
			if ok:
				return Step.ok(1), ASTToken(symbol, tokens[end])
			else:
				return Step.ng(), ASTToken.empty()
		else:
			step, children = self._match_entry(tokens, end, pattern)
			return step, self._expand_entry(symbol, children)

	def _expand_entry(self, symbol: str, children: list[ASTEntry]) -> ASTEntry:
		"""自身の子として生成されたASTエントリーを上位のASTツリーに展開

		Args:
			symbol: シンボル
			children: 配下要素
		Returns:
			子のASTエントリー
		Note:
			XXX 自身と子を入れ替えると言う単純な実装のため、複数の子を上位のツリーに展開できない
		"""
		if self.rules.expand_by(symbol) == Expandors.OneTime and len(children) == 1:
			return children[0]

		return ASTTree(symbol, children)

	def _match_entry(self, tokens: list[Token], end: int, pattern: PatternEntry, allow_repeat: bool = True) -> tuple[Step, list[ASTEntry]]:
		"""パターンエントリーを検証し、ASTエントリーを生成

		Args:
			tokens: トークンリスト
			end: 評価開始位置
			pattern: パターンエントリー
			allow_repeat: True = リピートへ遷移 (default = True)
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		if isinstance(pattern, Patterns):
			if pattern.rep != Repeators.NoRepeat and allow_repeat:
				return self._match_repeat(tokens, end, pattern)
			elif pattern.op == Operators.And:
				return self._match_and(tokens, end, pattern)
			else:
				return self._match_or(tokens, end, pattern)
		else:
			if pattern.role == Roles.Terminal:
				# 終端要素
				ok = self._compare_terminal(tokens[end], pattern)
				return Step.ok(1) if ok else Step.ng(), []
			else:
				step, entry = self._match_symbol(tokens, end, pattern.expression)
				return step, [entry]

	def _match_or(self, tokens: list[Token], end: int, patterns: Patterns) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(OR)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			end: 評価開始位置
			patterns: マッチングパターングループ
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		for pattern in patterns:
			in_step, in_children = self._match_entry(tokens, end, pattern)
			if in_step.steping:
				return in_step, in_children

		return Step.ng(), []

	def _match_and(self, tokens: list[Token], end: int, patterns: Patterns) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(AND)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			end: 評価開始位置
			patterns: マッチングパターングループ
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		steps = 0
		children: list[ASTEntry] = []
		for pattern in reversed(patterns):
			in_step, in_children = self._match_entry(tokens, end - steps, pattern)
			if not in_step.steping:
				return Step.ng(), []

			children.extend(reversed(in_children))
			steps += in_step.steps

		return Step.ok(steps), list(reversed(children))

	def _match_repeat(self, tokens: list[Token], end: int, patterns: Patterns) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(リピート)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			end: 評価開始位置
			patterns: マッチングパターングループ
		Returns:
			(ステップ, ASTエントリーリスト)
		Raises:
			AssertionError: リピートなしのグループを指定
		"""
		assert patterns.rep != Repeators.NoRepeat, 'Must be repeated patterns'

		found = 0
		steps = 0
		children: list[ASTEntry] = []
		while 0 <= end - steps:
			in_step, in_children = self._match_entry(tokens, end - steps, patterns, allow_repeat=False)
			if not in_step.steping:
				break

			found += 1
			steps += in_step.steps
			children.extend(reversed(in_children))

			if patterns.rep in [Repeators.OneOrZero, Repeators.OneOrEmpty]:
				break

		if found == 0:
			if patterns.rep in [Repeators.OverZero, Repeators.OneOrZero]:
				return Step.ok(0), []
			elif patterns.rep == Repeators.OneOrEmpty:
				return Step.ok(0), [ASTToken.empty()]
			else:
				return Step.ng(), []

		return Step.ok(steps), list(reversed(children))
	
	def _compare_terminal(self, token: Token, pattern: Pattern) -> bool:
		"""終端/非終端要素の検証

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
