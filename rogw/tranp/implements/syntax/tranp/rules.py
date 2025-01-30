from rogw.tranp.implements.syntax.tranp.parser import Operators, Pattern, Patterns, Repeators, Rules
from rogw.tranp.implements.syntax.tranp.tokenizer import TokenDefinition, Tokenizer


def python_rules() -> Rules:
	"""ルールを生成(Python用)

	Returns:
		ルール一覧
	Note:
		### 名前の定義
		* symbol: 左辺の名前
		* pattern: 右辺の条件式
		* rule: symbolとpatternのペア
	"""
	return Rules({
		# entrypoint
		'entry': Patterns([Pattern.S('exp'), Pattern.T('"\n"')], rep=Repeators.OverOne),
		# non terminal
		'bool': Pattern.T('/False|True/'),
		'int': Pattern.T('/[1-9][0-9]*/'),
		'float': Pattern.T('/(0|[1-9][0-9]*)[.][0-9]+/'),
		'str': Pattern.T('/\'[^\']*\'|"[^"]*"/'),
		'none': Pattern.T('"None"'),
		'name': Pattern.T('/[a-zA-Z_][0-9a-zA-Z_]*/'),
		# expression
		'var': Pattern.S('name'),
		'?exp': Pattern.S('primary'),
		# primary
		'?primary': Patterns([Pattern.S('relay'), Pattern.S('invoke'), Pattern.S('indexer'), Pattern.S('atom')], op=Operators.Or),
		'relay': Patterns([Pattern.S('primary'), Pattern.T('"."'), Pattern.S('name')]),
		'invoke': Patterns([Pattern.S('primary'), Pattern.T('"("'), Patterns([Pattern.S('args')], rep=Repeators.OneOrEmpty), Pattern.T('")"')]),
		'indexer': Patterns([Pattern.S('primary'), Pattern.T('"["'), Pattern.S('exp'), Pattern.T('"]"')]),
		'?atom': Patterns([Pattern.S('var'), Pattern.S('bool'), Pattern.S('none'), Pattern.S('str'), Pattern.S('int'), Pattern.S('float')], op=Operators.Or),
		# element
		'args': Patterns([Pattern.S('exp'), Patterns([Pattern.T('","'), Pattern.S('exp')], rep=Repeators.OverZero)]),
	})


def grammar_rules() -> Rules:
	"""ルールを生成(Grammar用)

	Returns:
		ルール一覧
	Note:
		```
		entry := (rule)+
		rule := (expand)? symbol ":=" expr "\n"
		?expr := terms_or
		?terns_or := (terms "|")* terms
		?terms := (term)* term
		?term := symbol | string | regexp | expr_opt | expr_rep
		expr_opt := "[" expr "]"
		expr_rep := "(" expr ")" [repeat]
		symbol := /[a-zA-Z_][0-9a-zA-Z_]*/
		string := /"[^"]+"/
		regexp := /\\/[^\\/]+\\//
		repeat := /[*+?]/
		expand := "?"
		```
	"""
	return Rules({
		'entry': Patterns([Pattern.S('rule')], rep=Repeators.OverOne),
		'rule': Patterns([Patterns([Pattern.S('expand')], rep=Repeators.OneOrZero), Pattern.S('symbol'), Pattern.T('":="'), Pattern.S('expr'), Pattern.T('"\n"')]),
		'?expr': Pattern.S('terms_or'),
		'?terms_or': Patterns([
			Patterns([Pattern.S('terms'), Pattern.T('"|"')], rep=Repeators.OverZero),
			Pattern.S('terms'),
		]),
		'?terms': Patterns([
			Patterns([Pattern.S('term')], rep=Repeators.OverZero),
			Pattern.S('term'),
		]),
		'?term': Patterns([
			Pattern.S('symbol'),
			Pattern.S('string'),
			Pattern.S('regexp'),
			Pattern.S('expr_opt'),
			Pattern.S('expr_rep'),
		], op=Operators.Or),
		'expr_opt': Patterns([
			Pattern.T('"["'), Pattern.S('expr'), Pattern.T('"]"'),
		]),
		'expr_rep': Patterns([
			Pattern.T('"("'), Pattern.S('expr'), Pattern.T('")"'),
			Patterns([Pattern.S('repeat')], rep=Repeators.OneOrEmpty),
		]),
		'symbol': Pattern.T('/[a-zA-Z_][0-9a-zA-Z_]*/'),
		'string': Pattern.T('/"[^"]+"/'),
		'regexp': Pattern.T('/\\/[^\\/]+\\//'),
		'repeat': Pattern.T('/[*+?]/'),
		'expand': Pattern.T('"?"'),
	})


def grammar_tokenizer() -> Tokenizer:
	"""トークンパーサーを生成(Grammar用)

	Returns:
		トークンパーサー
	"""
	definition = TokenDefinition()
	definition.quote = [TokenDefinition.build_quote_pair(c, c) for c in ['/', '"']]
	return Tokenizer(definition=definition)


"""
Note:
```
### EBNF
[
	'entry ::= exp',
	'bool ::= /False|True/',
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
	'invoke ::= primary "(" [args] ")"',
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
