from rogw.tranp.implements.syntax.tranp.parser import Operators, Pattern, Patterns, PatternEntry, Repeators


def python_rules() -> dict[str, PatternEntry]:
	"""ルールを生成(Python用)

	Returns:
		ルール一覧
	Note:
		### 名前の定義
		* symbol: 左辺の名前
		* pattern: 右辺の条件式
		* rule: symbolとpatternのペア
	"""
	return {
		# entrypoint
		'entry': Pattern.S('?exp'),
		# non terminal
		'bool': Pattern.T('/false|true/'),
		'int': Pattern.T('/[1-9][0-9]*/'),
		'float': Pattern.T('/(0|[1-9][0-9]*)[.][0-9]+/'),
		'str': Pattern.T('/\'[^\']*\'|"[^"]*"/'),
		'none': Pattern.T('"None"'),
		'name': Pattern.T('/[a-zA-Z_][0-9a-zA-Z_]*/'),
		# expression
		'var': Pattern.S('name'),
		'?exp': Pattern.S('?primary'),
		# primary
		'?primary': Patterns([Pattern.S('relay'), Pattern.S('invoke'), Pattern.S('indexer'), Pattern.S('?atom')], op=Operators.Or),
		'relay': Patterns([Pattern.S('?primary'), Pattern.T('"."'), Pattern.S('name')]),
		'invoke': Patterns([Pattern.S('?primary'), Pattern.T('"("'), Patterns([Pattern.S('args')], rep=Repeators.Bit), Pattern.T('")"')]),
		'indexer': Patterns([Pattern.S('?primary'), Pattern.T('"["'), Pattern.S('?exp'), Pattern.T('"]"')]),
		'?atom': Patterns([Pattern.S('var'), Pattern.S('bool'), Pattern.S('none'), Pattern.S('str'), Pattern.S('int'), Pattern.S('float')], op=Operators.Or),
		# element
		'args': Patterns([Pattern.S('?exp'), Patterns([Pattern.T('","'), Pattern.S('?exp')], rep=Repeators.Over0)]),
	}


def grammar_rules() -> dict[str, PatternEntry]:
	"""ルールを生成(Grammar用)

	Returns:
		ルール一覧
	Note:
		```
		entry := (rule)+
		rule := symbol ":=" expr "\n"
		expr := list | expr "|" list | "(" expr ")" (/[*+?]/)?
		list := term | list term
		term := literal | symbol
		symbol:= /[a-zA-Z_][0-9a-zA-Z_]*/
		literal := /"[^"]+"/
		```
	"""
	return {
		'entry': Patterns([Pattern.S('rule')], rep=Repeators.Over1),
		'rule': Patterns([Pattern.S('symbol'), Pattern.T('":="'), Pattern.S('expr'), Pattern.T('"\n"')]),
		'expr': Patterns([
			Pattern.S('list'),
			Patterns([Pattern.S('expr'), Pattern.T('"|"'), Pattern.S('list')]),
			Patterns([Pattern.T('"("'), Pattern.S('expr'), Pattern.T('")"'), Patterns([Pattern.T('/[*+?]/')])]),
		], op=Operators.Or),
		'list': Patterns([
			Pattern.S('term'),
			Patterns([Pattern.S('list'), Pattern.S('term')]),
		], op=Operators.Or),
		'term': Patterns([Pattern.S('literal'), Pattern.S('symbol')], op=Operators.Or),
		'symbol': Pattern.T('/[a-zA-Z_][0-9a-zA-Z_]*/'),
		'literal': Pattern.T('/"[^"]+"/'),
	}

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
"""
