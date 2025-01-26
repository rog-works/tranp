import re
from typing import Iterator, Literal, TypeAlias

from rogw.tranp.lang.convertion import as_a

PatternEntry: TypeAlias = 'Pattern | Patterns'
Operator: TypeAlias = Literal['and', 'or']
Repeator: TypeAlias = Literal['1', '*', '+', '?']
Roles: TypeAlias = Literal['symbol', 'terminal']
Comps: TypeAlias = Literal['reg', 'str', 'none']


class Pattern:
	def __init__(self, pattern: str, role: Roles, comp: Comps) -> None:
		self.pattern = pattern
		self.role = role
		self.comp = comp

	@classmethod
	def S(cls, pattern: str) -> 'Pattern':
		return cls(pattern, 'symbol', 'none')

	@classmethod
	def T(cls, pattern: str) -> 'Pattern':
		comp = 'reg' if pattern[0] == '/' else 'str'
		return cls(pattern, 'terminal', comp)


class Patterns:
	def __init__(self, children: list[PatternEntry], op: Operator = 'and', rep: Repeator = '1') -> None:
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
		'primary': Patterns([Pattern.S('relay'), Pattern.S('invoke'), Pattern.S('indexer'), Pattern.S('atom')], op='or'),
		'relay': Patterns([Pattern.S('primary'), Pattern.T('"."'), Pattern.S('name')]),
		'invoke': Patterns([Pattern.S('primary'), Pattern.T('"("'), Patterns([Pattern.S('args')], rep='?'), Pattern.T('")"')]),
		'indexer': Patterns([Pattern.S('primary'), Pattern.T('"["'), Pattern.S('exp'), Pattern.T('"]"')]),
		'atom': Patterns([Pattern.S('var'), Pattern.S('bool'), Pattern.S('none'), Pattern.S('str'), Pattern.S('int'), Pattern.S('float')], op='or'),
		# element
		'args': Patterns([Pattern.S('exp'), Patterns([Pattern.T('","'), Pattern.S('exp')], rep='*')]),
	}


Entry: TypeAlias = 'Token | Tree'
Token: TypeAlias = tuple[str, str]
Tree: TypeAlias = tuple[str, list[Entry]]
Empty = ('__empty__', '')


class Parser:
	def __init__(self, patterns: dict[str, PatternEntry]) -> None:
		self.patterns = patterns

	def parse(self, tokens: list[str], entry: str) -> Entry:
		return self.match(tokens, len(tokens) - 1, entry)[1]

	def match(self, tokens: list[str], end: int, rule_name: str) -> tuple[int, Entry]:
		pattern = self.patterns[rule_name]
		if isinstance(pattern, Patterns):
			return self.match_patterns(tokens, end, rule_name)
		elif pattern.role == 'terminal':
			return self.match_non_terminal(tokens, end, rule_name)
		else:
			return self.match(tokens, end, pattern.pattern)

	def match_patterns(self, tokens: list[str], end: int, rule_name: str) -> tuple[int, Entry]:
		patterns = as_a(Patterns, self.patterns[rule_name])
		if patterns.op == 'or':
			step, children = self._match_patterns_or(tokens, end, patterns)
			return step, (rule_name, children)
		else:
			step, children = self._match_patterns_and(tokens, end, patterns)
			return step, (rule_name, children)

	def _match_repeat(self, tokens: list[str], end: int, patterns: Patterns) -> tuple[int, list[Entry]]:
		found = 0
		step = 0
		children: list[Entry] = []
		while True:
			if patterns.op == 'or':
				in_step, in_children = self._match_patterns_or(tokens, end - step, patterns)
			else:
				in_step, in_children = self._match_patterns_and(tokens, end - step, patterns)

			step += in_step
			children.extend(in_children)

			if in_step == 0:
				break
			elif patterns.rep in ['1', '?']:
				break

			found += 1

		if found == 0:
			if patterns.rep in ['*', '?']:
				return 0, []
			else:
				# FIXME 許可して良い場合を区別できない
				return -1, []

		return step, children

	def _match_patterns_or(self, tokens: list[str], end: int, patterns: Patterns) -> tuple[int, list[Entry]]:
		for pattern in patterns:
			in_children: list[Entry] = []
			if isinstance(pattern, Patterns):
				in_step, in_entry = self._match_repeat(tokens, end, pattern)
				in_children.extend(in_entry)
			elif pattern.role == 'terminal':
				in_step, in_entry = self._match_terminal(tokens, end, pattern)
				in_children.append(in_entry)
			else:
				in_step, in_entry = self.match(tokens, end, pattern.pattern)
				in_children.append(in_entry)

			if in_step > 0:
				return in_step, in_children

		return 0, []

	def _match_patterns_and(self, tokens: list[str], end: int, patterns: Patterns) -> tuple[int, list[Entry]]:
		step = 0
		children: list[Entry] = []
		for pattern in reversed(patterns):
			in_children: list[Entry] = []
			if isinstance(pattern, Patterns):
				in_step, in_entry = self._match_repeat(tokens, end - step, pattern)
				in_children.extend(in_entry)
			elif pattern.role == 'terminal':
				in_step, in_entry = self._match_terminal(tokens, end - step, pattern)
				in_children.append(in_entry)
			else:
				in_step, in_entry = self.match(tokens, end - step, pattern.pattern)
				in_children.append(in_entry)

			if in_step == 0:
				return 0, []

			children.extend(in_children)
			step += in_step

		return step, children

	def match_non_terminal(self, tokens: list[str], end: int, rule_name: str) -> tuple[int, Entry]:
		pattern = as_a(Pattern, self.patterns[rule_name])
		if self._a_terminal(tokens, end, pattern):
			return 1, (rule_name, tokens[end])

		return 0, Empty
	
	def _match_terminal(self, tokens: list[str], end: int, pattern: Pattern) -> tuple[int, Entry]:
		if self._a_terminal(tokens, end, pattern):
			return 1, (pattern.pattern, tokens[end])

		return 0, Empty

	def _a_terminal(self, tokens: list[str], end: int, pattern: Pattern) -> bool:
		if pattern.comp == 'reg':
			return re.fullmatch(pattern.pattern[1:-1], tokens[end]) is not None
		else:
			return pattern.pattern[1:-1] == tokens[end]


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
