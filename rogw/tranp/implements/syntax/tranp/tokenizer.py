from abc import ABCMeta, abstractmethod
from io import BytesIO
import token as PyTokenTypes
from tokenize import tokenize
from typing import TypedDict, override

from rogw.tranp.implements.syntax.tranp.token import Token, TokenDomains, TokenTypes

QuotePair = TypedDict('QuotePair', {'open': str, 'close': str})


class TokenDefinition:
	"""トークン定義"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.white_space = ' \t\n\r'
		self.comment = [self.build_quote_pair('#', '\n')]
		self.symbol = '@#$.:;(){}[]`\\'
		self.quote = [self.build_quote_pair(f'{prefix}{quote}', quote) for prefix in ['', 'r', 'f'] for quote in ['"""', "'", '"']]
		self.number = '0123456789.'
		self.identifier = '_0123456789abcdefghijklmnopqrstuABCDEFGHIJKLMNOPQRSTU'
		self.operator = '=-+*/%&|^~!?<>'
		self.operator_compound = [
			'-=', '+=', '*=', '/=', '%=',
			'&=', '|=', '^=', '~=',
			'==', '!=', '<=', '>=', '&&', '||',
			'<<', '>>',
			'->', '**', ':=', '...',
		]

	@classmethod
	def build_quote_pair(cls, open: str, close: str) -> QuotePair:
		"""開始と終了のペアを生成

		Args:
			open: 開始の文字列
			close: 終了の文字列
		Returns:
			開始と終了のペア
		"""
		return {'open': open, 'close': close}


class ITokenizer(metaclass=ABCMeta):
	"""トークンパーサー(インターフェイス)"""

	@abstractmethod
	def parse(self, source: str) -> list[Token]:
		"""ソースコードを解析し、トークンに分割

		Args:
			source: ソースコード
		Returns:
			トークンリスト
		"""
		...


class TokenParser:
	"""トークンパーサー"""

	class Context:
		"""コンテキスト"""
		nest: int
		enclosure: int

	def __init__(self, definition: TokenDefinition) -> None:
		self._definition = definition
		self._handlers = {
			TokenDomains.WhiteSpace: self.handle_white_space,
			TokenDomains.Symbol: self.handle_symbol,
			TokenDomains.Operator: self.handle_operator,
		}

	def tokenize(self, tokens: list[Token]) -> list[Token]:
		"""トークンを解析してプログラムで解釈しやすい形式に整形

		Args:
			tokens: トークンリスト
		Returns:
			トークンリスト
		"""
		context = self.Context()
		index = 0
		new_tokens: list[Token] = []
		while index < len(tokens):
			token = tokens[index]
			if token.domain not in self._handlers:
				index += 1
				new_tokens.append(token)
				continue

			handler = self._handlers[token.domain]
			end, new_token, add_tokens = handler(context, tokens, index)
			index = end
			new_tokens.append(new_token)
			new_tokens.extend(add_tokens)

		return new_tokens

	def handle_white_space(self, context: Context, tokens: list[Token], begin: int) -> tuple[int, Token, list[Token]]:
		token = tokens[begin]
		if context.enclosure > 0:
			return begin + 1, token, []
		elif context.nest < token.string.count('\t'):
			context.nest = token.string.count('\t')
			return begin + 1, Token(TokenTypes.NewLine, token.string[0]), [Token(TokenTypes.Indent, token.string[1:])]
		elif context.nest > token.string.count('\t'):
			context.nest = token.string.count('\t')
			return begin + 1, Token(TokenTypes.NewLine, token.string[0]), [Token(TokenTypes.Dedent, token.string[1:])]
		else:
			return begin + 1, Token(TokenTypes.NewLine, token.string), []

	def handle_symbol(self, context: Context, tokens: list[Token], begin: int) -> tuple[int, Token, list[Token]]:
		token = tokens[begin]
		if token.type in [TokenTypes.ParenL, TokenTypes.BraceL, TokenTypes.BracketL]:
			context.enclosure += 1
		elif token.type in [TokenTypes.ParenR, TokenTypes.BraceR, TokenTypes.BracketR]:
			context.enclosure -= 1

		return begin + 1, token, []

	def handle_operator(self, context: Context, tokens: list[Token], begin: int) -> tuple[int, Token, list[Token]]:
		for index, compound in enumerate(self._definition.operator_compound):
			if len(tokens) <= begin + len(compound):
				continue

			combine = ''.join([tokens[begin + i].string[0] for i in range(len(compound))])
			if combine != compound:
				continue

			base = TokenDomains.Operator.value << 4
			offset = len(self._definition.operator)
			token_type = TokenTypes(base + offset + index)
			return begin + len(compound), Token(token_type, combine), []

		return begin + 1, tokens[begin], []


class Tokenizer(ITokenizer):
	"""トークンパーサー"""

	def __init__(self, definition: TokenDefinition | None = None) -> None:
		"""インスタンスを生成

		Args:
			definition: トークン定義 (defaul = None)
		"""
		self._definition = definition if definition else TokenDefinition()
		self._analyzers = {
			TokenDomains.WhiteSpace: self.analyze_white_spece,
			TokenDomains.Comment: self.analyze_comment,
			TokenDomains.Symbol: self.analyze_symbol,
			TokenDomains.Quote: self.analyze_quote,
			TokenDomains.Number: self.analyze_number,
			TokenDomains.Identifier: self.analyze_identifier,
			TokenDomains.Operator: self.analyze_operator,
		}
		self._parsers = {
			TokenDomains.WhiteSpace: self.parse_white_spece,
			TokenDomains.Comment: self.parse_comment,
			TokenDomains.Symbol: self.parse_symbol,
			TokenDomains.Quote: self.parse_quote,
			TokenDomains.Number: self.parse_number,
			TokenDomains.Identifier: self.parse_identifier,
			TokenDomains.Operator: self.parse_operator,
		}

	@override
	def parse(self, source: str) -> list[Token]:
		"""ソースコードを解析し、トークンに分割

		Args:
			source: ソースコード
		Returns:
			トークンリスト
		"""
		index = 0
		tokens: list[Token] = []
		while index < len(source):
			parser = self._parsers[self.analyze_domain(source, index)]
			end, token = parser(source, index)
			index = end
			tokens.append(token)

		return tokens

	def analyze_domain(self, source: str, begin: int) -> TokenDomains:
		"""トークンドメインを解析

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			トークンドメイン
		"""
		for token_class, analyzer in self._analyzers.items():
			if analyzer(source, begin):
				return token_class

		assert False, f'Never. Undetermine token domain. with character: {source[begin]}'

	def analyze_white_spece(self, source: str, begin: int) -> bool:
		"""トークンドメインを解析(空白)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return source[begin] in self._definition.white_space

	def analyze_comment(self, source: str, begin: int) -> bool:
		"""トークンドメインを解析(コメント)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return len([True for pair in self._definition.comment if source.startswith(pair['open'], begin)]) > 0

	def analyze_symbol(self, source: str, begin: int) -> bool:
		"""トークンドメインを解析(記号)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return source[begin] in self._definition.symbol

	def analyze_quote(self, source: str, begin: int) -> bool:
		"""トークンドメインを解析(引用符)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return len([True for pair in self._definition.quote if source.startswith(pair['open'], begin)]) > 0

	def analyze_number(self, source: str, begin: int) -> bool:
		"""トークンドメインを解析(数字)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return source[begin] in self._definition.number

	def analyze_identifier(self, source: str, begin: int) -> bool:
		"""トークンドメインを解析(識別子)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return source[begin] in self._definition.identifier

	def analyze_operator(self, source: str, begin: int) -> bool:
		"""トークンドメインを解析(演算子)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return source[begin] in self._definition.operator

	def parse_white_spece(self, source: str, begin: int) -> tuple[int, Token]:
		"""トークンを解析(空白)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		end = begin
		while end < len(source):
			if source[end] not in self._definition.white_space:
				break

			end += 1

		return end, Token(TokenTypes.WhiteSpace, source[begin:end])

	def parse_comment(self, source: str, begin: int) -> tuple[int, Token]:
		"""トークンを解析(コメント)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		found_pair = [pair for pair in self._definition.comment if source.startswith(pair['open'], begin)]
		pair = found_pair[0]
		end = source.find(pair['close'], begin + len(pair['open']))
		if end != -1:
			end += len(pair['close'])
			return end, Token(TokenTypes.Comment, source[begin:end])
		else:
			return len(source), Token(TokenTypes.Comment, source[begin:])

	def parse_symbol(self, source: str, begin: int) -> tuple[int, Token]:
		"""トークンを解析(記号)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		value = source[begin]
		base = TokenDomains.Symbol.value << 4
		offset = self._definition.symbol.index(value)
		token_type = TokenTypes(base + offset)
		return begin + 1, Token(token_type, value)

	def parse_quote(self, source: str, begin: int) -> tuple[int, Token]:
		"""トークンを解析(引用符)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		found_pair = [pair for pair in self._definition.quote if source.startswith(pair['open'], begin)]
		pair = found_pair[0]
		end = begin + len(pair['open'])
		while end < len(source):
			index = source.find(pair['close'], end)
			if index == -1:
				break

			end = index + len(pair['close'])
			if not (end < len(source) and source[end] == '\\'):
				break

		value = source[begin:end]
		token_type = TokenTypes.Regexp if value[0] == '/' else TokenTypes.String
		return end, Token(token_type, value)

	def parse_number(self, source: str, begin: int) -> tuple[int, Token]:
		"""トークンを解析(数字)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		end = begin
		while end < len(source):
			if source[end] not in self._definition.number:
				break

			end += 1

		value = source[begin:end]
		token_type = TokenTypes.Decimal if value.count('.') > 0 else TokenTypes.Digit
		return end, Token(token_type, value)

	def parse_identifier(self, source: str, begin: int) -> tuple[int, Token]:
		"""トークンを解析(識別子)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		end = begin
		while end < len(source):
			if source[end] not in self._definition.identifier:
				break

			end += 1

		return end, Token(TokenTypes.Name, source[begin:end])

	def parse_operator(self, source: str, begin: int) -> tuple[int, Token]:
		"""トークンを解析(演算子)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		value = source[begin]
		base = TokenDomains.Operator.value << 4
		offset = self._definition.operator.index(value)
		token_type = TokenTypes(base + offset)
		return begin + 1, Token(token_type, value)


class PyTokenizer(ITokenizer):
	"""トークンパーサー(Python専用)"""

	@override
	def parse(self, source: str) -> list[Token]:
		"""ソースコードを解析し、トークンに分割

		Args:
			source: ソースコード
		Returns:
			トークンリスト
		"""
		# 先頭のENCODING、末尾のENDMARKERを除外
		exclude_types = [PyTokenTypes.ENCODING, PyTokenTypes.ENDMARKER]
		tokens = [token for token in tokenize(BytesIO(source.encode('utf-8')).readline) if token.type not in exclude_types]
		# 存在しない末尾の空行を削除 ※実際に改行が存在する場合は'\n'になる
		if tokens[-1].type == PyTokenTypes.NEWLINE and len(tokens[-1].string) == 0:
			tokens.pop()

		return [Token(TokenTypes.Unknown, token.string) for token in tokens]
