from collections.abc import Iterator

from rogw.tranp.implements.syntax.tranp.rule import Pattern, Roles, Rules, Unwraps
from rogw.tranp.implements.syntax.tranp.state import States
from rogw.tranp.implements.syntax.tranp.task import Tasks
from rogw.tranp.implements.syntax.tranp.token import Token
from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.implements.syntax.tranp.tokenizer import ITokenizer, Tokenizer


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

	def parse(self, source: str, entrypoint: str) -> Iterator[ASTEntry]:
		"""ソースコードを解析してASTを生成

		Args:
			source: ソースコード
			entrypoint: 基点のシンボル名
		Returns:
			ASTエントリー
		"""
		tokens = self.tokenizer.parse(source)
		return self._parse(Tasks(self.rules), tokens, entrypoint)

	def _parse(self, tasks: Tasks, tokens: list[Token], entrypoint: str) -> Iterator[ASTEntry]:
		"""ソースコードを解析してASTを生成

		Args:
			tasks: タスク一覧
			tokens: トークンリスト
			entrypoint: 基点のシンボル名
		Returns:
			イテレーター(ASTエントリー)
		"""
		index = 0
		entries: list[ASTEntry] = []
		while index < len(tokens):
			token = tokens[index]
			tasks.ready(names=tasks.lookup(entrypoint))
			tasks.step(token, state=States.Idle)
			finish_names = tasks.state_of(States.Done)
			finish_names.extend(self.accept(tasks, entrypoint))
			if len(finish_names) == 0:
				continue

			if self.steped(finish_names):
				index += 1

			# エントリーポイントは終了条件が無いため明示的に終了 XXX 自然に終わる方法を検討
			if index == len(tokens) and entrypoint not in finish_names:
				finish_names.append(entrypoint)

			ast, entries = self.stack(token, entries, finish_names)
			yield ast

	def accept(self, tasks: Tasks, entrypoint: str) -> list[str]:
		"""シンボル更新イベントを発火。完了したシンボルを返却

		Args:
			tasks: タスク一覧
			entrypoint: 基点のシンボル名
		Returns:
			シンボルリスト(処理完了)
		"""
		finish_names = []
		while True:
			update_names = tasks.accept(States.Idle)
			if len(update_names) == 0:
				break

			finish_names.extend(tasks.state_of(States.Done, names=update_names))
			allow_names = tasks.lookup(entrypoint)
			lookup_names = tasks.lookup_advance(update_names, allow_names)
			tasks.ready(names=lookup_names)

		return finish_names

	def steped(self, finish_names: list[str]) -> bool:
		"""トークンの読み出しが完了したか判定

		Args:
			finish_names: シンボルリスト(処理完了)
		Returns:
			True = 完了
		"""
		for name in finish_names:
			if name not in self.rules:
				return True

		return False

	def stack(self, token: Token, prev_entries: list[ASTEntry], finish_names: list[str]) -> tuple[ASTEntry, list[ASTEntry]]:
		"""今回解析した結果からASTを生成し、以前のASTを内部にスタック

		Args:
			token: トークン
			prev_entries: ASTエントリーリスト(以前)
			finish_names: シンボルリスト(処理完了)
		Returns:
			(ASTエントリー, ASTエントリーリスト(新))
		"""
		entries: list[ASTEntry] = prev_entries.copy()
		ast = entries[0] if len(entries) > 0 else ASTToken.empty()
		terminal_name = ''
		for name in finish_names:
			if name not in self.rules:
				terminal_name = name
				continue

			pattern = self.rules[name]
			if isinstance(pattern, Pattern) and pattern.role == Roles.Terminal:
				assert pattern.expression == terminal_name and pattern.expression in finish_names
				ast = ASTToken(name, token)
				entries.append(ast)
			else:
				ast = ASTTree(name, self._unwrap(entries))
				entries = [ast]

		assert isinstance(ast, ASTTree) and len(entries) == 1
		return ast, entries

	def _unwrap(self, children: list[ASTEntry]) -> list[ASTEntry]:
		"""子のASTエントリーを展開

		Args:
			children: 配下要素
		Returns:
			展開後のASTエントリーリスト
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

		return unwraped
