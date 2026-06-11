from rogw.tranp.implements.syntax.tranp.rule import Rules


def py_rules() -> Rules:
	return Rules.from_ast(
		('entry', [
			('rule', [
				('symbol', 'entry'),
				('__empty__', ''),
				('expr_rep', [
					('symbol', 'statement'),
					('repeat', '+')
				])
			]),
			('rule', [
				('symbol', 'statement'),
				('unwrap', '1'),
				('terms_or', [
					('terms', [
						('symbol', 'line'),
						('string', '"\\n"')
					]),
					('symbol', 'if'),
					('symbol', 'for'),
					('symbol', 'while'),
					('symbol', 'function')
				])
			]),
			('rule', [
				('symbol', 'line'),
				('unwrap', '1'),
				('terms_or', [
					('symbol', 'break'),
					('symbol', 'pass'),
					('symbol', 'return'),
					('symbol', 'move')
				])
			]),
			('rule', [
				('symbol', 'break'),
				('__empty__', ''),
				('string', '"break"')
			]),
			('rule', [
				('symbol', 'pass'),
				('__empty__', ''),
				('string', '"..."')
			]),
			('rule', [
				('symbol', 'return'),
				('__empty__', ''),
				('terms', [
					('string', '"return"'),
					('symbol', 'expr')
				])
			]),
			('rule', [
				('symbol', 'move'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'expr'),
							('string', '"="')
						]),
						('repeat', '?')
					]),
					('symbol', 'expr')
				])
			]),
			('rule', [
				('symbol', 'function'),
				('__empty__', ''),
				('terms', [
					('string', '"def"'),
					('symbol', 'name'),
					('string', '"("'),
					('expr_opt', [
						('symbol', 'params')
					]),
					('string', '")"'),
					('string', '"->"'),
					('expr_opt', [
						('symbol', 'type')
					]),
					('string', '":"'),
					('string', '"\\n"'),
					('symbol', 'block')
				])
			]),
			('rule', [
				('symbol', 'params'),
				('__empty__', ''),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'param'),
							('string', '","')
						]),
						('repeat', '*')
					]),
					('symbol', 'param')
				])
			]),
			('rule', [
				('symbol', 'param'),
				('__empty__', ''),
				('terms', [
					('symbol', 'name'),
					('string', '":"'),
					('symbol', 'type'),
					('expr_opt', [
						('terms', [
							('string', '"="'),
							('symbol', 'expr')
						])
					])
				])
			]),
			('rule', [
				('symbol', 'if'),
				('__empty__', ''),
				('terms', [
					('symbol', 'then'),
					('expr_rep', [
						('symbol', 'elif'),
						('repeat', '*')
					]),
					('expr_opt', [
						('symbol', 'else')
					])
				])
			]),
			('rule', [
				('symbol', 'then'),
				('__empty__', ''),
				('terms', [
					('string', '"if"'),
					('symbol', 'expr'),
					('string', '":"'),
					('string', '"\\n"'),
					('symbol', 'block')
				])
			]),
			('rule', [
				('symbol', 'elif'),
				('__empty__', ''),
				('terms', [
					('string', '"elif"'),
					('symbol', 'expr'),
					('string', '":"'),
					('string', '"\\n"'),
					('symbol', 'block')
				])
			]),
			('rule', [
				('symbol', 'else'),
				('__empty__', ''),
				('terms', [
					('string', '"else"'),
					('string', '":"'),
					('string', '"\\n"'),
					('symbol', 'block')
				])
			]),
			('rule', [
				('symbol', 'for'),
				('__empty__', ''),
				('terms', [
					('string', '"for"'),
					('symbol', 'name'),
					('string', '"in"'),
					('symbol', 'primary'),
					('string', '":"'),
					('string', '"\\n"'),
					('symbol', 'block')
				])
			]),
			('rule', [
				('symbol', 'while'),
				('__empty__', ''),
				('terms', [
					('string', '"while"'),
					('symbol', 'expr'),
					('string', '":"'),
					('string', '"\\n"'),
					('symbol', 'block')
				])
			]),
			('rule', [
				('symbol', 'block'),
				('__empty__', ''),
				('terms', [
					('string', '"\\INDENT"'),
					('expr_rep', [
						('symbol', 'statement'),
						('repeat', '+')
					]),
					('string', '"\\DEDENT"')
				])
			]),
			('rule', [
				('symbol', 'expr'),
				('unwrap', '1'),
				('symbol', 'ternary')
			]),
			('rule', [
				('symbol', 'ternary'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'expr'),
							('string', '"if"'),
							('symbol', 'assign'),
							('string', '"else"')
						]),
						('repeat', '?')
					]),
					('symbol', 'assign')
				])
			]),
			('rule', [
				('symbol', 'assign'),
				('unwrap', '1'),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'expr'),
							('string', '":="')
						]),
						('repeat', '?')
					]),
					('symbol', 'comp_or')
				])
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
					('symbol', 'comp')
				])
			]),
			('rule', [
				('symbol', 'comp'),
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
							('symbol', 'unary'),
							('symbol', 'op_mul')
						]),
						('repeat', '*')
					]),
					('symbol', 'unary')
				])
			]),
			('rule', [
				('symbol', 'unary'),
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
				('regexp', '/<|>|==|<=|>=|!=/')
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
				('symbol', 'op_add'),
				('__empty__', ''),
				('regexp', '/[-+]/')
			]),
			('rule', [
				('symbol', 'op_mul'),
				('__empty__', ''),
				('regexp', '/[*\\/%]/')
			]),
			('rule', [
				('symbol', 'op_unary'),
				('__empty__', ''),
				('string', '"\\OP_UNARY_MINUS"')
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
					('symbol', 'boolean'),
					('symbol', 'none'),
					('symbol', 'var'),
					('symbol', 'string'),
					('symbol', 'digit'),
					('symbol', 'decimal'),
					('symbol', 'list'),
					('symbol', 'dict'),
					('terms', [
						('string', '"("'),
						('symbol', 'expr'),
						('string', '")"')
					])
				])
			]),
			('rule', [
				('symbol', 'var'),
				('__empty__', ''),
				('symbol', 'name')
			]),
			('rule', [
				('symbol', 'type'),
				('unwrap', '1'),
				('terms_or', [
					('symbol', 'type_none'),
					('symbol', 'type_var')
				])
			]),
			('rule', [
				('symbol', 'type_none'),
				('__empty__', ''),
				('symbol', 'none')
			]),
			('rule', [
				('symbol', 'type_var'),
				('__empty__', ''),
				('symbol', 'name')
			]),
			('rule', [
				('symbol', 'args'),
				('unwrap', '*'),
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
				('symbol', 'values'),
				('unwrap', '*'),
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
				('symbol', 'key_values'),
				('unwrap', '*'),
				('terms', [
					('expr_rep', [
						('terms', [
							('symbol', 'key_value'),
							('string', '","')
						]),
						('repeat', '*')
					]),
					('symbol', 'key_value')
				])
			]),
			('rule', [
				('symbol', 'key_value'),
				('__empty__', ''),
				('terms', [
					('symbol', 'string'),
					('string', '":"'),
					('symbol', 'expr')
				])
			]),
			('rule', [
				('symbol', 'list'),
				('__empty__', ''),
				('terms', [
					('string', '"["'),
					('expr_opt', [
						('symbol', 'values')
					]),
					('string', '"]"')
				])
			]),
			('rule', [
				('symbol', 'dict'),
				('__empty__', ''),
				('terms', [
					('string', '"{"'),
					('expr_opt', [
						('symbol', 'key_values')
					]),
					('string', '"}"')
				])
			]),
			('rule', [
				('symbol', 'boolean'),
				('__empty__', ''),
				('regexp', '/False|True/')
			]),
			('rule', [
				('symbol', 'none'),
				('__empty__', ''),
				('string', '"None"')
			]),
			('rule', [
				('symbol', 'name'),
				('__empty__', ''),
				('regexp', '/[a-zA-Z_]\\w*/')
			]),
			('rule', [
				('symbol', 'string'),
				('__empty__', ''),
				('regexp', '/\'([^\'\\\\]*(\\\\\')?)*\'|"([^"\\\\]*(\\\\")?)*"/')
			]),
			('rule', [
				('symbol', 'digit'),
				('__empty__', ''),
				('regexp', '/0|[1-9]\\d*/')
			]),
			('rule', [
				('symbol', 'decimal'),
				('__empty__', ''),
				('regexp', '/(0|[1-9]\\d*)[.]\\d+/')
			])
		])
	)
