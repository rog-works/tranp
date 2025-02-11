from collections.abc import Iterator

from rogw.tranp.implements.syntax.tranp.rule import Rules, Unwraps
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
		tasks = Tasks.from_rules(self.rules)
		stack: list[StackParser] = [StackParser(tasks, entrypoint)]
		index = 0
		entries: list[ASTEntry] = []
		while index < len(tokens) and len(stack) > 0:
			parser = stack[-1]
			finish_names = parser.parse(tokens, index)
			if parser.entrypoint in finish_names:
				stack.pop()

			token = tokens[index]
			for name in finish_names:
				ast, entries = self.wrap_ast(token, entries, name)
				yield ast

			if self.steped(finish_names):
				index += 1

			stack.extend(self.new_stack(tasks, finish_names))

	def steped(self, finish_names: list[str]) -> bool:
		"""トークンの読み出しが完了したか判定

		Args:
			finish_names: シンボルリスト(処理完了)
		Returns:
			True = 完了
		"""
		return len([True for name in finish_names if name not in self.rules]) > 0

	def new_stack(self, tasks: Tasks, finish_names: list[str]) -> list['StackParser']:
		stack: list[StackParser] = []
		for name in finish_names:
			for effect in tasks.depends.effects(name):
				if len(tasks.depends.recursive(effect)) > 0:
					stack.append(StackParser(tasks.clone(), effect))

		return stack

	def wrap_ast(self, token: Token, entries: list[ASTEntry], name: str) -> tuple[ASTEntry, list[ASTEntry]]:
		"""今回解析した結果からASTを生成し、以前のASTを内部にスタック

		Args:
			token: トークン
			prev_entries: ASTエントリーリスト(以前)
			finish_names: シンボルリスト(処理完了)
		Returns:
			(ASTエントリー, ASTエントリーリスト(新))
		"""
		if name not in self.rules:
			ast = ASTToken(token.type.name, token)
			return ast, [*entries, ast]
		else:
			ast = ASTTree(name, self._unwrap(entries))
			return ast, [ast]

	def _unwrap(self, entries: list[ASTEntry]) -> list[ASTEntry]:
		"""子のASTエントリーを展開

		Args:
			entries: 配下要素
		Returns:
			展開後のASTエントリーリスト
		"""
		unwraped: list[ASTEntry] = []
		for entry in entries:
			if isinstance(entry, ASTToken):
				unwraped.append(entry)
			elif self.rules.unwrap_by(entry.name) == Unwraps.OneTime and len(entry.children) == 1:
				unwraped.append(entry.children[0])
			elif self.rules.unwrap_by(entry.name) == Unwraps.Always:
				unwraped.extend(entry.children)
			else:
				unwraped.append(entry)

		return unwraped


class StackParser:
	def __init__(self, tasks: Tasks, entrypoint: str) -> None:
		self.tasks = tasks
		self.entrypoint = entrypoint

	def parse(self, tokens: list[Token], index: int) -> list[str]:
		token = tokens[index]
		self.tasks.ready(names=self.tasks.lookup(self.entrypoint))
		self.tasks.step(index, token, state=States.Idle)
		finish_names = self.tasks.state_of(States.Done)
		finish_names.extend(self.accept(index))
		return finish_names

	def accept(self, index: int) -> list[str]:
		"""シンボル更新イベントを発火。完了したシンボルを返却

		Args:
			tasks: タスク一覧
			entrypoint: 基点のシンボル名
		Returns:
			シンボルリスト(処理完了)
		"""
		finish_names = []
		while True:
			update_names = self.tasks.accept(index, States.Idle)
			if len(update_names) == 0:
				break

			finish_names.extend(self.tasks.state_of(States.Done, names=update_names))
			allow_names = self.tasks.lookup(self.entrypoint)
			lookup_names = self.tasks.lookup_advance(update_names, allow_names)
			self.tasks.ready(names=lookup_names)

		return finish_names
