from rogw.tranp.implements.syntax.tranp.rule import Operators, Pattern, Patterns, Repeators, Rules
from rogw.tranp.implements.syntax.tranp.tokenizer import TokenDefinition, Tokenizer


def python_rules() -> Rules:
	"""ルールを生成(Python用)

	Returns:
		ルール一覧
	"""
	return Rules.from_ast(
		('entry', [
			('rule', [
				('__empty__', ''),
				('symbol', 'entry'),
				('expr_rep', [
					('terms', [
						('symbol', 'exp'),
						('string', 'LN')
					]),
					('repeat', '+')
				])
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'LN'),
				('regexp', '/\n|EOF/')
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'bool'),
				('regexp', '/False|True/')
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'int'),
				('regexp', '/[1-9]\\d*/')
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'float'),
				('regexp', '/(0|[1-9]\\d*)[.]\\d+/')
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'str'),
				('regexp', '/\'[^\']*\'|"[^"]*"/')
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'none'),
				('string', '"None"')
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'name'),
				('regexp', '/[a-zA-Z_]\\w*/')
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'var'),
				('symbol', 'name')
			]),
			('rule', [
				('expand', '?'),
				('symbol', 'exp'),
				('symbol', 'primary')
			]),
			('rule', [
				('expand', '?'),
				('symbol', 'primary'),
				('terms_or', [
					('symbol', 'relay'),
					('symbol', 'invoke'),
					('symbol', 'indexer'),
					('symbol', 'atom')
				])
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'relay'),
				('terms', [
					('symbol', 'primary'),
					('string', '"."'),
					('symbol', 'name')
				])
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'invoke'),
				('terms', [
					('symbol', 'primary'),
					('string', '"("'),
					('expr_opt', [
						('symbol', 'args')
					]),
					('string', '")"')
				])
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'indexer'),
				('terms', [
					('symbol', 'primary'),
					('string', '"["'),
					('symbol', 'exp'),
					('string', '"]"')
				])
			]),
			('rule', [
				('expand', '?'),
				('symbol', 'atom'),
				('terms_or', [
					('symbol', 'var'),
					('symbol', 'bool'),
					('symbol', 'none'),
					('symbol', 'str'),
					('symbol', 'int'),
					('symbol', 'float')
				])
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'args'),
				('terms', [
					('symbol', 'exp'),
					('expr_rep', [
						('terms', [
							('string', '","'),
							('symbol', 'exp')
						]),
						('repeat', '*')
					])
				])
			])
		])
	)


def grammar_rules() -> Rules:
	"""ルールを生成(Grammar用)

	Returns:
		ルール一覧
	Note:
		```
		entry := (rule)+
		rule := [expand] symbol ":=" expr LN
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
		LN := /\n|EOF/
		```
	"""
	return Rules({
		'entry': Patterns([Pattern.S('rule')], rep=Repeators.OverOne),
		'rule': Patterns([Patterns([Pattern.S('expand')], rep=Repeators.OneOrEmpty), Pattern.S('symbol'), Pattern.T('":="'), Pattern.S('expr'), Pattern.S('LN')]),
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
		'LN': Pattern.T('/\n|EOF/'),
	})


def grammar_tokenizer() -> Tokenizer:
	"""トークンパーサーを生成(Grammar用)

	Returns:
		トークンパーサー
	"""
	definition = TokenDefinition()
	definition.comment = [TokenDefinition.build_quote_pair('//', '\n')]
	definition.quote = [TokenDefinition.build_quote_pair(c, c) for c in ['/', '"']]
	definition.symbol = ''.join(definition.symbol.split('/'))
	definition.pre_filters['comment_spaces'] = r'[ \t\f]*//.*$'
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
