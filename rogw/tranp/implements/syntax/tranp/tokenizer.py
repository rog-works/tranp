from abc import ABCMeta, abstractmethod
from enum import Enum
from io import BytesIO
import token as PyTokenTypes
from tokenize import tokenize
from typing import NamedTuple, TypedDict, override


class TokenDomains(Enum):
	"""トークンドメイン"""
	WhiteSpace = 0
	Comment = 1
	Symbol = 2
	Quote = 3
	Number = 4
	Identifier = 5
	Operator = 6


class TokenTypes(Enum):
	"""トークン種別"""
	# 空白
	WhiteSpace = 0x00
	NewLine = 0x01
	Indent = 0x02
	Dedent = 0x03
	# コメント
	Comment = 0x10
	# 記号
	At = 0x20
	Sharp = 0x21
	Dollar = 0x22
	Dot = 0x23
	Colon = 0x24
	SemiColon = 0x25
	ParenL = 0x26
	ParenR = 0x27
	BraceL = 0x28
	BraceR = 0x29
	BracketL = 0x2A
	BracketR = 0x2B
	BackQuote = 0x2C
	BackSlash = 0x2D
	Ellipsis = 0x2E
	# 引用符
	String = 0x30
	Regexp = 0x31
	# 数字
	Digit = 0x40
	Decimal = 0x41
	# 識別子
	Name = 0x50
	Keyword = 0x51
	# 演算子(単)
	Equal = 0x60
	Minus = 0x61
	Plus = 0x62
	Aster = 0x63
	Slash = 0x64
	Percent = 0x65
	And = 0x66
	Or = 0x67
	Hat = 0x68
	Tilde = 0x69
	Exclamation = 0x6A
	Question = 0x6B
	Smaller = 0x6C
	Greater = 0x6D
	# 演算子(6)
	MinusEqual = 0x6E
	PlusEqual = 0x6F
	AsterEqual = 0x70
	SlashEqual = 0x71
	PercentEqual = 0x72
	AndEqual = 0x73
	OrEqual = 0x74
	HatEqual = 0x75
	DoubleEqual = 0x76
	NotEqual = 0x77
	DoubleAnd = 0x78
	DoubleOr = 0x79
	ShiftL = 0x7A
	ShiftR = 0x7B
	Arrow = 0x7C
	DoubleAster = 0x7D
	WalrusEqual = 0x7E
	# 未定義
	Empty = 0xFE
	Unknown = 0xFF


QuotePair = TypedDict('QuotePair', {'open': str, 'close': str})


class TokenDefinition:
	"""トークン定義"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.white_space = ' \t\n\r'
		self.comment = [self.build_quote_pair('#', '\n')]
		self.symbol = '@#$.:;(){}[]`\\'  # ['_', "'", '"'] は別ドメインなので除外
		self.quote = [self.build_quote_pair(f'{prefix}{quote}', quote) for prefix in ['', 'r', 'f'] for quote in ['"""', "'", '"']]
		self.number = '0123456789.'
		self.identifier = '_0123456789abcdefghijklmnopqrstuABCDEFGHIJKLMNOPQRSTU'
		self.operator = {
			'single': '=-+*/%&|^~!?<>',
			'compound': ['-=', '+=', '*=', '/=', '%=', '&=', '|=', '^=', '==', '!=', '&&', '||', '<<', '>>', '->', '**', ':=', '...'],
		}

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


class Token(NamedTuple):
	"""トークン"""

	type: TokenTypes
	string: str

	@classmethod
	def empty(cls) -> 'Token':
		"""Returns: 空を表すインスタンス"""
		return cls(TokenTypes.Empty, '')


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
		nest: int

	def tokenize(self, tokens: list[Token]) -> list[Token]:
		"""トークンを解析してプログラムで解釈しやすい形式に整形

		Args:
			tokens: トークンリスト
		Returns:
			トークンリスト
		"""
		context = self.Context()
		index = 0
		new_tokens = []
		while index < len(tokens):
			end, in_tokens = self.parse_(context, tokens, index)
			index = end
			new_tokens.extend(in_tokens)

		return new_tokens

	def parse_(self, context: Context, tokens: list[Token], begin: int) -> tuple[int, list[Token]]:
		...


class Tokenizer(ITokenizer):
	"""トークンパーサー"""

	def __init__(self, definition: TokenDefinition | None = None) -> None:
		"""インスタンスを生成

		Args:
			definition: トークン定義 (defaul = None)
		"""
		self._definition = definition if definition else TokenDefinition()
		self._parsers = {
			TokenDomains.WhiteSpace: self.parse_white_spece,
			TokenDomains.Comment: self.parse_comment,
			TokenDomains.Symbol: self.parse_symbol,
			TokenDomains.Quote: self.parse_quote,
			TokenDomains.Number: self.parse_number,
			TokenDomains.Identifier: self.parse_identifier,
			TokenDomains.Operator: self.parse_operator,
		}
		self._analyzers = {
			TokenDomains.WhiteSpace: self.analyze_white_spece,
			TokenDomains.Comment: self.analyze_comment,
			TokenDomains.Symbol: self.analyze_symbol,
			TokenDomains.Quote: self.analyze_quote,
			TokenDomains.Number: self.analyze_number,
			TokenDomains.Identifier: self.analyze_identifier,
			TokenDomains.Operator: self.analyze_operator,
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

	def analyze_number(self, source: str, begin: int) -> bool:
		"""トークンドメインを解析(数字)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return source[begin] in self._definition.number

	def analyze_quote(self, source: str, begin: int) -> bool:
		"""トークンドメインを解析(引用符)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return len([True for pair in self._definition.quote if source.startswith(pair['open'], begin)]) > 0

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
		if source[begin] in self._definition.operator['single']:
			return True

		return len([True for operator in self._definition.operator['compound'] if source.startswith(operator, begin)]) > 0

	def analyze_symbol(self, source: str, begin: int) -> bool:
		"""トークンドメインを解析(記号)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return source[begin] in self._definition.symbol

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
		if begin != -1:
			end += len(pair['close'])

		return end, Token(TokenTypes.Comment, source[begin:end])

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
		token_type = TokenTypes.String if value.count('/') > 0 else TokenTypes.Regexp
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
		if begin + 2 < len(source) and source[begin:begin + 2] in self._definition.operator['compound']:
			value = source[begin:begin + 2]
			base = TokenDomains.Operator.value << 4
			offset0 = len(self._definition.operator['single'])
			offset1  = self._definition.operator['compound'].index(value)
			token_type = TokenTypes(base + offset0 + offset1)
			return begin + 2, Token(token_type, value)
		else:
			value = source[begin]
			base = TokenDomains.Operator.value << 4
			offset = self._definition.operator['single'].index(value)
			token_type = TokenTypes(base + offset)
			return begin + 1, Token(token_type, value)

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
