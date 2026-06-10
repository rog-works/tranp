from rogw.tranp.implements.syntax.tranp.token import TokenDefinition
from rogw.tranp.implements.syntax.tranp.tokenizer import Tokenizer


def gram_tokenizer() -> Tokenizer:
	"""トークンパーサーを生成(Grammar用)

	Returns:
		トークンパーサー
	"""
	definition = TokenDefinition()
	definition.comment = [TokenDefinition.build_quote_pair('//', '\n')]
	definition.quote = [TokenDefinition.build_quote_pair(c, c) for c in ['/', '"']]
	definition.symbol = ''.join(definition.symbol.split('/'))
	return Tokenizer(definition=definition)
