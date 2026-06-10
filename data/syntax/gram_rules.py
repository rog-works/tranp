from rogw.tranp.implements.syntax.tranp.rule import Rules


def gram_rules() -> Rules:
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
						])
					]),
					('string', '":="'),
					('symbol', 'expr'),
					('string', '"\\n"')
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
					('symbol', 'terms'),
					('expr_rep', [
						('terms', [
							('string', '"|"'),
							('symbol', 'terms')
						]),
						('repeat', '*')
					])
				])
			]),
			('rule', [
				('symbol', 'terms'),
				('unwrap', '1'),
				('expr_rep', [
					('symbol', 'term'),
					('repeat', '+')
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
				('regexp', '/[a-zA-Z_]\\w*/')
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

