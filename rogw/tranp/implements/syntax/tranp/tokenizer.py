from abc import ABCMeta, abstractmethod
from enum import Enum
from io import BytesIO
import token as TokenTypes
from tokenize import tokenize
from typing import override


class TokenClasses(Enum):
	"""トークン種別"""
	WhiteSpace = 'white_space'
	Comment = 'comment'
	Number = 'number'
	Quote = 'quote'
	Identifier = 'identifier'
	Symbol = 'symbol'


class TokenDefinition:
	"""トークン定義"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		symbols = {
			'other': '@#$',  # '_' は識別子なので除外
			'delimiter': '.:;',
			'operator': '=-+*/%&|^~!?',
			'bracket': '(){}<>[]',
			'quate': '`\\',  # ["'", '"'] は文字列の引用符なので除外
		}
		self.white_space = ' \t\n\r'
		self.comment = [{'open': '#', 'close': '\n'}]
		self.number = '0123456789.'
		self.quote = '\'"'
		self.identifier = '_0123456789abcdefghijklmnopqrstuABCDEFGHIJKLMNOPQRSTU'
		self.symbol = {
			'single': ''.join(symbol for symbol in symbols.values()),
			'pair': ['-=', '+=', '*=', '/=', '%=', '&=', '|=', '^=', '==', '**', ':='],
		}


class ITokenizer(metaclass=ABCMeta):
	"""トークンパーサー(インターフェイス)"""

	@abstractmethod
	def parse(self, source: str) -> list[str]:
		"""ソースコードを解析し、トークンに分割

		Args:
			source: ソースコード
		Returns:
			トークンリスト
		"""
		...


class TokenParser2(ITokenizer):
	"""トークンパーサー"""

	def __init__(self, definition: TokenDefinition | None = None) -> None:
		"""インスタンスを生成

		Args:
			definition: トークン定義 (defaul = None)
		"""
		self.definition = definition if definition else TokenDefinition()
		self.parsers = {
			TokenClasses.WhiteSpace: self.parse_white_spece,
			TokenClasses.Comment: self.parse_comment,
			TokenClasses.Number: self.parse_number,
			TokenClasses.Quote: self.parse_quote,
			TokenClasses.Identifier: self.parse_identifier,
			TokenClasses.Symbol: self.parse_symbol,
		}

	@override
	def parse(self, source: str) -> list[str]:
		"""ソースコードを解析し、トークンに分割

		Args:
			source: ソースコード
		Returns:
			トークンリスト
		"""
		index = 0
		tokens: list[str] = []
		while index < len(source):
			parser = self.parsers[self.analyze_class(source, index)]
			end, token = parser(source, index)
			index = end
			tokens.append(token)

		return tokens

	def analyze_class(self, source: str, begin: int) -> TokenClasses:
		"""トークン種別を解析

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			トークン種別
		Note:
			XXX 先頭1文字で解決できると言う前提で処理
		"""
		c = source[begin]
		if c in self.definition.white_space:
			return TokenClasses.WhiteSpace
		elif len([True for comment_pair in self.definition.comment if c == comment_pair['open'][0]]) > 0:
			return TokenClasses.Comment
		elif c in self.definition.number:
			return TokenClasses.Number
		elif c in self.definition.quote:
			return TokenClasses.Quote
		elif c in self.definition.identifier:
			return TokenClasses.Identifier
		elif c in self.definition.symbol['single']:
			return TokenClasses.Symbol

		assert False, f'Never. Unexpected begining character. c: {c}'

	def parse_white_spece(self, source: str, begin: int) -> tuple[int, str]:
		"""トークンを解析(空白)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		end = begin
		while end < len(source):
			if source[end] not in self.definition.white_space:
				break

			end += 1

		return end, source[begin:end]

	def parse_comment(self, source: str, begin: int) -> tuple[int, str]:
		"""トークンを解析(コメント)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		found_pair = [comment_pair for comment_pair in self.definition.comment if source[begin] == comment_pair['open'][0]]
		comment_pair = found_pair[0]
		end = source.find(comment_pair['close'], begin + len(comment_pair))
		if begin < end:
			end += len(comment_pair['close'])
			return end, source[begin:end]
		else:
			return len(source), source[begin:]

	def parse_number(self, source: str, begin: int) -> tuple[int, str]:
		"""トークンを解析(数字)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		end = begin
		while end < len(source):
			if source[end] not in self.definition.number:
				break

			end += 1

		return end, source[begin:end]

	def parse_quote(self, source: str, begin: int) -> tuple[int, str]:
		"""トークンを解析(引用符)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		quote = source[begin]
		end = begin + 1
		while end < len(source):
			index = source.find(quote, end)
			if index == -1:
				break

			end = index + 1
			if not (end < len(source) and source[end] == '\\'):
				break

		return end, source[begin:end]

	def parse_identifier(self, source: str, begin: int) -> tuple[int, str]:
		"""トークンを解析(識別子)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		end = begin
		while end < len(source):
			if source[end] not in self.definition.identifier:
				break

			end += 1

		return end, source[begin:end]

	def parse_symbol(self, source: str, begin: int) -> tuple[int, str]:
		"""トークンを解析(記号)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			(次の読み取り位置, トークン)
		"""
		if begin + 2 < len(source) and source[begin:begin + 2] in self.definition.symbol['pair']:
			return begin + 2, source[begin:begin + 2]
		else:
			return begin + 1, source[begin]


class TokenParser(ITokenizer):
	"""トークンパーサー(Python専用)"""

	@override
	def parse(self, source: str) -> list[str]:
		"""ソースコードを解析し、トークンに分割

		Args:
			source: ソースコード
		Returns:
			トークンリスト
		"""
		# 先頭のENCODING、末尾のENDMARKERを除外
		exclude_types = [TokenTypes.ENCODING, TokenTypes.ENDMARKER]
		tokens = [token for token in tokenize(BytesIO(source.encode('utf-8')).readline) if token.type not in exclude_types]
		# 存在しない末尾の空行を削除 ※実際に改行が存在する場合は'\n'になる
		if tokens[-1].type == TokenTypes.NEWLINE and len(tokens[-1].string) == 0:
			tokens.pop()

		return [token.string for token in tokens]
