from rogw.tranp.implements.syntax.tranp.rule import Rules
from rogw.tranp.implements.syntax.tranp.tokenizer import TokenDefinition, Tokenizer


def python_rules() -> Rules:
	"""ルールを生成(Python用)

	Returns:
		ルール一覧
	"""
	return Rules.from_ast(
		('entry', [
			('rule', [
				('symbol', 'entry'),
				('__empty__', ''),
				('expr_rep', [
					('terms', [
						('symbol', 'expr'),
						('string', '"\n"')
					]),
					('repeat', '+')
				])
			]),
			('rule', [
				('symbol', 'expr'),
				('unwrap', '1'),
				('symbol', 'comp_or')
			]),
			('rule', [
				('symbol', 'comp_or'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'comp_and'),
							('symbol', 'op_or')
						]),
						('repeat', '*')
					]),
					('symbol', 'comp_and')
				])
			]),
			('rule', [
				('symbol', 'comp_and'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'comp_not'),
							('symbol', 'op_and')
						]),
						('repeat', '*')
					]),
					('symbol', 'comp_not')
				])
			]),
			('rule', [
				('symbol', 'comp_not'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('symbol', 'op_not'),
						('repeat', '?')
					]),
					('symbol', 'comparison')
				])
			]),
			('rule', [
				('symbol', 'comparison'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'calc_sum'),
							('symbol', 'op_comp')
						]),
						('repeat', '*')
					]),
					('symbol', 'calc_sum')
				])
			]),
			('rule', [
				('symbol', 'calc_sum'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'calc_mul'),
							('symbol', 'op_add')
						]),
						('repeat', '*')
					]),
					('symbol', 'calc_mul')
				])
			]),
			('rule', [
				('symbol', 'calc_mul'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'calc_unary'),
							('symbol', 'op_mul')
						]),
						('repeat', '*')
					]),
					('symbol', 'calc_unary')
				])
			]),
			('rule', [
				('symbol', 'calc_unary'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('symbol', 'op_unary'),
						('repeat', '?')
					]),
					('symbol', 'primary')
				])
			]),
			('rule', [
				('symbol', 'op_or'),
				('__empty__', ''),
				('string', '"or"')
			]),
			('rule', [
				('symbol', 'op_and'),
				('__empty__', ''),
				('string', '"and"')
			]),
			('rule', [
				('symbol', 'op_in'),
				('__empty__', ''),
				('string', '"in"')
			]),
			('rule', [
				('symbol', 'op_is'),
				('__empty__', ''),
				('string', '"is"')
			]),
			('rule', [
				('symbol', 'op_not'),
				('__empty__', ''),
				('string', '"not"')
			]),
			('rule', [
				('symbol', 'op_comp'),
				('__empty__', ''),
				('terms_or', [
					('symbol', 'op_comp_s'),
					('terms', [
						('expr_rep', [
							('symbol', 'op_not'),
							('repeat', '?')
						]),
						('symbol', 'op_in')
					]),
					('terms', [
						('symbol', 'op_is'),
						('expr_rep', [
							('symbol', 'op_not'),
							('repeat', '?')
						])
					])
				])
			]),
			('rule', [
				('symbol', 'op_comp_s'),
				('__empty__', ''),
				('regexp', r'/==|!=|<=|>=|<|>/')
			]),
			('rule', [
				('symbol', 'op_add'),
				('__empty__', ''),
				('regexp', r'/[+-]/')
			]),
			('rule', [
				('symbol', 'op_mul'),
				('__empty__', ''),
				('regexp', r'/[*\/%]/')
			]),
			('rule', [
				('symbol', 'op_unary'),
				('__empty__', ''),
				('regexp', r'/[+-]/')
			]),
			('rule', [
				('symbol', 'primary'),
				('unwrap', '1'),
				('terms_or', [
					('symbol', 'relay'),
					('symbol', 'invoke'),
					('symbol', 'indexer'),
					('symbol', 'atom')
				])
			]),
			('rule', [
				('symbol', 'relay'),
				('__empty__', ''),
				('terms', [
					('symbol', 'primary'),
					('string', '"."'),
					('symbol', 'name')
				])
			]),
			('rule', [
				('symbol', 'invoke'),
				('__empty__', ''),
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
				('symbol', 'indexer'),
				('__empty__', ''),
				('terms', [
					('symbol', 'primary'),
					('string', '"["'),
					('symbol', 'slice'),
					('string', '"]"')
				])
			]),
			('rule', [
				('symbol', 'atom'),
				('unwrap', '1'),
				('terms_or', [
					('symbol', 'bool'),
					('symbol', 'none'),
					('symbol', 'var'),
					('symbol', 'str'),
					('symbol', 'int'),
					('symbol', 'float'),
					('symbol', 'group_expr')
				])
			]),
			('rule', [
				('symbol', 'var'),
				('__empty__', ''),
				('symbol', 'name')
			]),
			('rule', [
				('symbol', 'group_expr'),
				('__empty__', ''),
				('terms', [
					('string', '"("'),
					('symbol', 'expr'),
					('string', '")"')
				])
			]),
			('rule', [
				('symbol', 'args'),
				('__empty__', ''),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'expr'),
							('string', '","')
						]),
						('repeat', '*')
					]),
					('symbol', 'expr')
				])
			]),
			('rule', [
				('symbol', 'slice'),
				('unwrap', '*'),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'expr'),
							('string', '":"')
						]),
						('repeat', '*')
					]),
					('symbol', 'expr')
				])
			]),
			('rule', [
				('symbol', 'bool'),
				('__empty__', ''),
				('regexp', r'/False|True/')
			]),
			('rule', [
				('symbol', 'none'),
				('__empty__', ''),
				('string', '"None"')
			]),
			('rule', [
				('symbol', 'name'),
				('__empty__', ''),
				('regexp', r'/[a-zA-Z_]\w*/')
			]),
			('rule', [
				('symbol', 'str'),
				('__empty__', ''),
				('regexp', r'/\'[^\']*\'|"[^"]*"/')
			]),
			('rule', [
				('symbol', 'int'),
				('__empty__', ''),
				('regexp', r'/0|[1-9]\d*/')
			]),
			('rule', [
				('symbol', 'float'),
				('__empty__', ''),
				('regexp', r'/(0|[1-9]\d*)[.]\d+/')
			])
		])
	)


def grammar_rules() -> Rules:
	"""ルールを生成(Grammar用)

	Returns:
		ルール一覧
	"""
	return Rules.from_ast(
		('entry', [
			('rule', [
				('symbol', 'entry'),
				('__empty__', ''),
				('expr_rep', [
					('symbol', 'rule'),
					('repeat', '+')
				])
			]),
			('rule', [
				('symbol', 'rule'),
				('__empty__', ''),
				('terms', [
					('symbol', 'symbol'),
					('expr_opt', [
						('terms', [
							('string', '"["'),
							('symbol', 'unwrap'),
							('string', '"]"')
						]),
					]),
					('string', '":="'),
					('symbol', 'expr'),
					('string', '"\n"')
				])
			]),
			('rule', [
				('symbol', 'expr'),
				('unwrap', '1'),
				('symbol', 'terms_or')
			]),
			('rule', [
				('symbol', 'terms_or'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'terms'),
							('string', '"|"')
						]),
						('repeat', '*')
					]),
					('symbol', 'terms')
				])
			]),
			('rule', [
				('symbol', 'terms'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('symbol', 'term'),
						('repeat', '*')
					]),
					('symbol', 'term')
				])
			]),
			('rule', [
				('symbol', 'term'),
				('unwrap', '1'),
				('terms_or', [
					('symbol', 'symbol'),
					('symbol', 'string'),
					('symbol', 'regexp'),
					('symbol', 'expr_opt'),
					('symbol', 'expr_rep')
				])
			]),
			('rule', [
				('symbol', 'expr_opt'),
				('__empty__', ''),
				('terms', [
					('string', '"["'),
					('symbol', 'expr'),
					('string', '"]"')
				])
			]),
			('rule', [
				('symbol', 'expr_rep'),
				('__empty__', ''),
				('terms', [
					('string', '"("'),
					('symbol', 'expr'),
					('string', '")"'),
					('expr_opt', [
						('symbol', 'repeat')
					])
				])
			]),
			('rule', [
				('symbol', 'symbol'),
				('__empty__', ''),
				('regexp', r'/[a-zA-Z_]\w*/')
			]),
			('rule', [
				('symbol', 'string'),
				('__empty__', ''),
				('regexp', '/"[^"]+"/')
			]),
			('rule', [
				('symbol', 'regexp'),
				('__empty__', ''),
				('regexp', '/[\\/].+[\\/]/')
			]),
			('rule', [
				('symbol', 'repeat'),
				('__empty__', ''),
				('regexp', '/[*+?]/')
			]),
			('rule', [
				('symbol', 'unwrap'),
				('__empty__', ''),
				('regexp', '/[1*]/')
			])
		])
	)


def grammar_tokenizer() -> Tokenizer:
	"""トークンパーサーを生成(Grammar用)

	Returns:
		トークンパーサー
	"""
	definition = TokenDefinition()
	definition.comment = [TokenDefinition.build_quote_pair('//', '\n')]
	definition.quote = [TokenDefinition.build_quote_pair(c, c) for c in ['/', '"']]
	definition.symbol = ''.join(definition.symbol.split('/'))
	return Tokenizer(definition=definition)
