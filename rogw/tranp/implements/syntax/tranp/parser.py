from enum import Enum
from io import BytesIO
import re
import token as TokenTypes
from tokenize import TokenInfo, tokenize
from typing import Iterator, TypeAlias

from rogw.tranp.lang.convertion import as_a


class Operators(Enum):
	And = 'and'
	Or = 'or'


class Repeators(Enum):
	Once = '1'
	Over0 = '*'
	Over1 = '+'
	Bit = '?'


class Roles(Enum):
	Symbol = 'symbol'
	Terminal = 'terminal'


class Comps(Enum):
	Regexp = 'regexp'
	Equals = 'equals'
	NoComp = 'no_comp'


PatternEntry: TypeAlias = 'Pattern | Patterns'


class Pattern:
	def __init__(self, pattern: str, role: Roles, comp: Comps) -> None:
		self.pattern = pattern
		self.role = role
		self.comp = comp

	@classmethod
	def S(cls, pattern: str) -> 'Pattern':
		return cls(pattern, Roles.Symbol, Comps.NoComp)

	@classmethod
	def T(cls, pattern: str) -> 'Pattern':
		comp = Comps.Regexp if pattern[0] == '/' else Comps.Equals
		return cls(pattern, Roles.Terminal, comp)


class Patterns:
	def __init__(self, children: list[PatternEntry], op: Operators = Operators.And, rep: Repeators = Repeators.Once) -> None:
		self.children = children
		self.op = op
		self.rep = rep

	def __len__(self) -> int:
		return len(self.children)

	def __getitem__(self, index: int) -> PatternEntry:
		return self.children[index]

	def __iter__(self) -> Iterator[PatternEntry]:
		for child in self.children:
			yield child


def rules() -> dict[str, PatternEntry]:
	return {
		# entrypoint
		'entry': Pattern.S('exp'),
		# non terminal
		'bool': Pattern.T('/false|true/'),
		'int': Pattern.T('/[1-9][0-9]*/'),
		'float': Pattern.T('/(0|[1-9][0-9]*)[.][0-9]+/'),
		'str': Pattern.T('/\'[^\']*\'|"[^"]*"/'),
		'none': Pattern.T('"None"'),
		'name': Pattern.T('/[a-zA-Z_][0-9a-zA-Z_]*/'),
		# expression
		'var': Pattern.S('name'),
		'exp': Pattern.S('primary'),
		# primary
		'primary': Patterns([Pattern.S('relay'), Pattern.S('invoke'), Pattern.S('indexer'), Pattern.S('atom')], op=Operators.Or),
		'relay': Patterns([Pattern.S('primary'), Pattern.T('"."'), Pattern.S('name')]),
		'invoke': Patterns([Pattern.S('primary'), Pattern.T('"("'), Patterns([Pattern.S('args')], rep=Repeators.Bit), Pattern.T('")"')]),
		'indexer': Patterns([Pattern.S('primary'), Pattern.T('"["'), Pattern.S('exp'), Pattern.T('"]"')]),
		'atom': Patterns([Pattern.S('var'), Pattern.S('bool'), Pattern.S('none'), Pattern.S('str'), Pattern.S('int'), Pattern.S('float')], op=Operators.Or),
		# element
		'args': Patterns([Pattern.S('exp'), Patterns([Pattern.T('","'), Pattern.S('exp')], rep=Repeators.Over0)]),
	}


ASTEntry: TypeAlias = 'ASTToken | ASTTree'
ASTToken: TypeAlias = tuple[str, str]
ASTTree: TypeAlias = tuple[str, list[ASTEntry]]
EmptyToken = ('__empty__', '')


class TokenParser:
	@classmethod
	def parse(cls, source: str) -> list[TokenInfo]:
		# 先頭のENCODE、末尾のENDMARKERを除外
		exclude_types = [TokenTypes.ENCODING, TokenTypes.ENDMARKER]
		tokens = [token for token in tokenize(BytesIO(source.encode('utf-8')).readline) if token.type not in exclude_types]
		# 存在しない末尾の空行を削除 ※実際に改行が存在する場合は'\n'になる
		if tokens[-1].type == TokenTypes.NEWLINE and len(tokens[-1].string) == 0:
			tokens.pop()

		return tokens


class Lexer:
	def __init__(self, patterns: dict[str, PatternEntry]) -> None:
		self.patterns = patterns

	def parse(self, source: str, entry: str) -> ASTEntry:
		tokens = TokenParser.parse(source)
		return self.match(tokens, len(tokens) - 1, entry)[1]

	def match(self, tokens: list[TokenInfo], end: int, rule_name: str) -> tuple[int, ASTEntry]:
		pattern = self.patterns[rule_name]
		if isinstance(pattern, Patterns):
			return self.match_patterns(tokens, end, rule_name)
		elif pattern.role == Roles.Terminal:
			return self.match_non_terminal(tokens, end, rule_name)
		else:
			return self.match(tokens, end, pattern.pattern)

	def match_patterns(self, tokens: list[TokenInfo], end: int, rule_name: str) -> tuple[int, ASTEntry]:
		patterns = as_a(Patterns, self.patterns[rule_name])
		if patterns.op == Operators.Or:
			step, children = self._match_patterns_or(tokens, end, patterns)
			return step, (rule_name, children)
		else:
			step, children = self._match_patterns_and(tokens, end, patterns)
			return step, (rule_name, children)

	def _match_patterns_or(self, tokens: list[TokenInfo], end: int, patterns: Patterns) -> tuple[int, list[ASTEntry]]:
		for pattern in patterns:
			in_step, in_children = self._match_patterns_for_entry(tokens, end, pattern)
			if in_step > 0:
				return in_step, in_children

		return 0, []

	def _match_patterns_and(self, tokens: list[TokenInfo], end: int, patterns: Patterns) -> tuple[int, list[ASTEntry]]:
		step = 0
		children: list[ASTEntry] = []
		for pattern in reversed(patterns):
			in_step, in_children = self._match_patterns_for_entry(tokens, end - step, pattern)
			if in_step == 0:
				return 0, []

			children.extend(in_children)
			step += in_step

		return step, list(reversed(children))

	def _match_patterns_for_entry(self, tokens: list[TokenInfo], end: int, pattern: PatternEntry) -> tuple[int, list[ASTEntry]]:
		if isinstance(pattern, Patterns):
			return self._match_repeat(tokens, end, pattern)
		elif pattern.role == Roles.Terminal:
			step, _ = self._match_terminal(tokens, end, pattern)[0], []
			return step, []
		else:
			step, entry = self.match(tokens, end, pattern.pattern)
			return step, [entry]

	def _match_repeat(self, tokens: list[TokenInfo], end: int, patterns: Patterns) -> tuple[int, list[ASTEntry]]:
		found = 0
		step = 0
		children: list[ASTEntry] = []
		while True:
			in_step, in_children = self._match_repeat_operation(tokens, end - step, patterns)
			step += in_step
			children.extend(in_children)

			if in_step == 0:
				break
			elif patterns.rep in [Repeators.Once, Repeators.Bit]:
				break

			found += 1

		if found == 0:
			if patterns.rep in [Repeators.Over0, Repeators.Bit]:
				return 0, []
			else:
				# FIXME 許可して良い場合を区別できない
				return -1, []

		return step, children

	def _match_repeat_operation(self, tokens: list[TokenInfo], end: int, patterns: Patterns) -> tuple[int, list[ASTEntry]]:
		if patterns.op == Operators.Or:
			return self._match_patterns_or(tokens, end, patterns)
		else:
			return self._match_patterns_and(tokens, end, patterns)

	def match_non_terminal(self, tokens: list[TokenInfo], end: int, rule_name: str) -> tuple[int, ASTEntry]:
		pattern = as_a(Pattern, self.patterns[rule_name])
		if self._a_terminal(tokens, end, pattern):
			return 1, (rule_name, tokens[end].string)

		return 0, EmptyToken
	
	def _match_terminal(self, tokens: list[TokenInfo], end: int, pattern: Pattern) -> tuple[int, ASTEntry]:
		if self._a_terminal(tokens, end, pattern):
			return 1, (pattern.pattern, tokens[end].string)

		return 0, EmptyToken

	def _a_terminal(self, tokens: list[TokenInfo], end: int, pattern: Pattern) -> bool:
		if pattern.comp == Comps.Regexp:
			return re.fullmatch(pattern.pattern[1:-1], tokens[end].string) is not None
		else:
			return pattern.pattern[1:-1] == tokens[end].string


"""
Note:
```
### EBNF
[
	'entry ::= exp',
	'bool ::= /false|true/',
	'int ::= /[1-9][0-9]*/',
	'float ::= /(0|[1-9][0-9]*)[.][0-9]+/',
	'str ::= /\'[^\']*\'|"[^"]*"/',
	'none ::= "None"',
	'var ::= /[a-zA-Z_][0-9a-zA-Z_]*/',
	'exp ::= primary',
	# FIXME 演算は一旦非対応
	# 'exp ::= or_test',
	# 'or_test ::= and_test ("or" and_test)*',
	# 'and_test ::= not_test ("and" not_test_)*',
	# 'not_test ::= "not" not_test | comparison',
	# 'comparison ::= sum (comp_op sum)*',
	# 'sum ::= term (add_op term)*',
	# 'term ::= factor (mul_op factor)*',
	# 'factor ::= unary_op factor | primary',
	# 'comp_op ::= "<" | ">" | "==" | "<=" | ">=" | "!=" | "in" | "not" "in" | "is" | "is" "not"',
	# 'add_op ::= "+" | "-"',
	# 'mul_op ::= "*" | "/" | "%"',
	# 'unary_op ::= "+" | "-"',
	'primary ::= relay | invoke | indexer | atom',
	'relay ::= primary "." var',
	'invoke ::= primary "(" (args)? ")"',
	'indexer ::= primary "[" exp "]"',
	'args ::= exp ("," exp)*',
	'atom ::= var | bool | none | str | int | float',
	# FIXME list | dict | group_exp は一旦非対応
	# 'list ::= "[" [list_exps] "]"',
	# 'dict ::= "{" [dict_exps] "}"',
	# 'group_exp ::= "(" exp ")"',
	# 'list_exps ::= exp ("," exp)*',
	# 'dict_exps ::= dict_pair ("," dict_pair)*',
	# 'dict_pair ::= exp ":" exp',
]
### AST('a.b.c')
('relay', [
	('relay', [
		('var', [
			('name', 'a'),
		]),
		('name', 'b'),
	]),
	('name', 'c'),
])
### AST('a.b('c').d')
('relay', [
	('invoke', [
		('relay', [
			('var', [
				('name', 'a'),
			]),
			('name', 'b'),
		]),
		('args', [
			('exp', [
				('str', 'c'),
			]),
		]),
	]),
	('name', 'd'),
])
```
"""
