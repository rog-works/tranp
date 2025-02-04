import re

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
		self._states: dict[tuple[int, str], bool] = {}

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
		step, entry = self._match_symbol(tokens, 0, entrypoint)
		if step.steps != length:
			message = ErrorCollector(source, tokens, step.steps).summary()
			raise ValueError(f'Syntax parse error. First token not reached. {message}')

		return entry

	def _match_symbol(self, tokens: list[Token], begin: int, path: str) -> tuple[Step, ASTEntry]:
		"""パターン(シンボル参照)を検証し、ASTエントリーを生成

		Args:
			tokens: トークンリスト
			end: 評価開始位置
			symbol: シンボル
		Returns:
			(ステップ, ASTエントリー)
		"""
		# 参照ステートがブロック中か判定
		symbol = DSN.right(path, 1)
		on_state = begin, symbol
		if on_state in self._states:
			return Step.ng(), ASTToken.empty()

		# 左再帰を開始したステートをブロックリストに登録
		if path.count(symbol) > 1:
			block_state = begin, DSN.elements(path)[-2]
			self._states[block_state] = True

		pattern = self.rules[symbol]
		if isinstance(pattern, Pattern) and pattern.role == Roles.Terminal:
			step, token = self._match_terminal(tokens, begin, pattern, path)
			entry = ASTToken(symbol, token) if step.steping else ASTToken.empty()
			return step, entry
		else:
			step, children = self._match_entry(tokens, begin, pattern, path)
			return step, self._unwrap_children(symbol, children)

	def _unwrap_children(self, symbol: str, children: list[ASTEntry]) -> ASTEntry:
		"""子のASTエントリーを展開し、ASTエントリーを生成

		Args:
			symbol: シンボル
			children: 配下要素
		Returns:
			ASTエントリー
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

	def _match_entry(self, tokens: list[Token], begin: int, pattern: PatternEntry, path: str, allow_repeat: bool = True) -> tuple[Step, list[ASTEntry]]:
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
				return self._match_repeat(tokens, begin, pattern, path)
			elif pattern.op == Operators.And:
				return self._match_and(tokens, begin, pattern, path)
			else:
				return self._match_or(tokens, begin, pattern, path)
		else:
			if pattern.role == Roles.Terminal:
				step, _ = self._match_terminal(tokens, begin, pattern, path)
				return step, []
			else:
				step, entry = self._match_symbol(tokens, begin, DSN.join(path, pattern.expression))
				return step, [entry]

	def _match_or(self, tokens: list[Token], begin: int, patterns: Patterns, path: str) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(OR)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			end: 評価開始位置
			patterns: マッチングパターングループ
		Returns:
			(ステップ, ASTエントリーリスト)
		"""
		for pattern in patterns:
			in_step, in_children = self._match_entry(tokens, begin, pattern, path)
			if in_step.steping:
				return in_step, in_children

		return Step.ng(), []

	def _match_and(self, tokens: list[Token], begin: int, patterns: Patterns, path: str) -> tuple[Step, list[ASTEntry]]:
		"""パターングループ(AND)を検証し、子のASTエントリーを生成

		Args:
			tokens: トークンリスト
			end: 評価開始位置
			patterns: マッチングパターングループ
		Returns:
			(ステップ, ASTエントリーリスト)
		Note:
			```
			XXX ステップの進行によって参照インデックスが負の値になるが、このメソッドでは許容する @see _match_terminal
			XXX これは、0個以上にマッチする条件(OverZero/OneOrZero/OneOrEmpty)が存在する仕様に起因する
			```
		"""
		# AND条件の先頭の左再帰は同じ条件の繰り返しによって本来は無限ループするが、ブロックリストによって1回以上評価されない
		# これにより並列条件が順に進み、最終的に非終端要素によってこのAND条件の先頭要素が解決される
		# これを基点に後続要素のマッチングを反復することで、期待するASTの構築が完了する
		first = patterns[0]
		if isinstance(first, Pattern) and first.role == Roles.Symbol and path.find(first.expression) != -1:
			first_step, first_children = self._match_entry(tokens, begin, patterns[0], path)
			if not first_step.steping:
				return Step.ng(), []

			finish = False
			ok = False
			steps = first_step.steps
			children_list: list[list[ASTEntry]] = []
			while not finish:
				# 先頭要素の後続のみ反復し、一致しなくなるまで繰り返す
				ok_count = 1
				in_steps = 0
				children: list[ASTEntry] = []
				for index in range(len(patterns)):
					if index == 0:
						continue

					in_step, in_children = self._match_entry(tokens, begin + steps + in_steps, patterns[index], path)
					if not in_step.steping:
						finish = True
						break

					children.extend(in_children)
					in_steps += in_step.steps
					ok_count += 1

				if ok_count == len(patterns):
					ok = True
					children_list.append(children)
					steps += in_steps

			if not ok:
				return Step.ng(), []

			# 先にマッチしたエントリーを内側にラップしてASTを構築
			symbol = DSN.right(path, 1)
			begin_entry = first_children[0]
			for in_children in children_list:
				begin_entry = self._unwrap_children(symbol, [begin_entry, *in_children])

			return Step.ok(steps), [begin_entry]
		else:
			steps = 0
			children: list[ASTEntry] = []
			for pattern in patterns:
				in_step, in_children = self._match_entry(tokens, begin + steps, pattern, path)
				if not in_step.steping:
					return Step.ng(), []

				children.extend(in_children)
				steps += in_step.steps

			return Step.ok(steps), children

	def _match_repeat(self, tokens: list[Token], begin: int, patterns: Patterns, path: str) -> tuple[Step, list[ASTEntry]]:
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
		while begin + steps < len(tokens):
			in_step, in_children = self._match_entry(tokens, begin + steps, patterns, path, allow_repeat=False)
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

	def _match_terminal(self, tokens: list[Token], begin: int, pattern: Pattern, path: str) -> tuple[Step, Token]:
		"""パターン(終端/非終端要素)を検証し、マッチしたトークンを返す

		Args:
			tokens: トークンリスト
			end: 評価開始位置
			pattern: マッチングパターン
		Returns:
			(ステップ, トークン)
		Note:
			```
			XXX トークン参照時の境界チェックはこのメソッド内でのみ行う
			XXX この制約に伴い、トークン参照、及び境界チェックはこのメソッド以外では基本的に実施しないものとする
			```
		"""
		if len(tokens) <= begin:
			return Step.ng(), Token.empty()

		ok = self._compare_token(tokens[begin], pattern)
		return (Step.ok(1), tokens[begin]) if ok else (Step.ng(), Token.empty())
	
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
	"""エラー出力ユーティリティー

	Note:
		```
		XXX 現状のSyntaxParserの解析手法を考慮すると、エラーの発生個所(=進捗停止位置)はほぼ改行であると予想されるため、エラーメッセージが意味を成さない懸念がある
		XXX SyntaxParserに最も進行したステップを記録するように修正し、それを基にエラー発生個所を見出す方法を検討
		```
	"""

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
		remain = total - self.steps
		return f'cause index: {remain - 1}, pass: {self.steps}/{total}, token: {repr(self._cause_token.string)}'

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
		last = len(self.tokens) - 1
		return self.tokens[last - self.steps]

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
