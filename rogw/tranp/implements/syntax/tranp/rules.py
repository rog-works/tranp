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
				('__empty__', ''),
				('symbol', 'entry'),
				('expr_rep', [
					('terms', [
						('symbol', 'exp'),
						('string', '"\n"')
					]),
					('repeat', '+')
				])
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
				('symbol', 'var'),
				('symbol', 'name')
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
				('__empty__', ''),
				('symbol', 'entry'),
				('expr_rep', [
					('symbol', 'rule'),
					('repeat', '+')
				])
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'rule'),
				('terms', [
					('expr_opt', [
						('symbol', 'expand')
					]),
					('symbol', 'symbol'),
					('string', '":="'),
					('symbol', 'expr'),
					('string', '"\n"')
				])
			]),
			('rule', [
				('expand', '?'),
				('symbol', 'expr'),
				('symbol', 'terms_or')
			]),
			('rule', [
				('expand', '?'),
				('symbol', 'terms_or'),
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
				('expand', '?'),
				('symbol', 'terms'),
				('terms', [
					('expr_rep', [
						('symbol', 'term'),
						('repeat', '*')
					]),
					('symbol', 'term')
				])
			]),
			('rule', [
				('expand', '?'),
				('symbol', 'term'),
				('terms_or', [
					('symbol', 'symbol'),
					('symbol', 'string'),
					('symbol', 'regexp'),
					('symbol', 'expr_opt'),
					('symbol', 'expr_rep')
				])
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'expr_opt'),
				('terms', [
					('string', '"["'),
					('symbol', 'expr'),
					('string', '"]"')
				])
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'expr_rep'),
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
				('__empty__', ''),
				('symbol', 'symbol'),
				('regexp', '/[a-zA-Z_][0-9a-zA-Z_]*/')
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'string'),
				('regexp', '/"[^"]+"/')
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'regexp'),
				('regexp', '/[\\/].+[\\/]/')
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'repeat'),
				('regexp', '/[*+?]/')
			]),
			('rule', [
				('__empty__', ''),
				('symbol', 'expand'),
				('string', '"?"')
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
	definition.pre_filters['comment_spaces'] = r'[ \t\f]*//.*$'
	return Tokenizer(definition=definition)
