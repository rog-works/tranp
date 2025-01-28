from abc import ABCMeta, abstractmethod
from enum import Enum
from io import BytesIO
import token as TokenTypes
from tokenize import tokenize
from typing import TypedDict, override


class TokenClasses(Enum):
	"""トークン種別"""
	WhiteSpace = 'white_space'
	Comment = 'comment'
	Number = 'number'
	Quote = 'quote'
	Identifier = 'identifier'
	Symbol = 'symbol'


QuotePair = TypedDict('QuotePair', {'open': str, 'close': str})


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
		self.comment = [self.build_quote_pair('#', '\n')]
		self.number = '0123456789.'
		self.quote = [self.build_quote_pair(f'{prefix}{quote}', quote) for prefix in ['', 'r', 'f'] for quote in ['"""', "'", '"']]
		self.identifier = '_0123456789abcdefghijklmnopqrstuABCDEFGHIJKLMNOPQRSTU'
		self.symbol = {
			'single': ''.join(symbol for symbol in symbols.values()),
			'pair': ['-=', '+=', '*=', '/=', '%=', '&=', '|=', '^=', '==', '**', ':='],
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


class Tokenizer(ITokenizer):
	"""トークンパーサー"""

	def __init__(self, definition: TokenDefinition | None = None) -> None:
		"""インスタンスを生成

		Args:
			definition: トークン定義 (defaul = None)
		"""
		self._definition = definition if definition else TokenDefinition()
		self._parsers = {
			TokenClasses.WhiteSpace: self.parse_white_spece,
			TokenClasses.Comment: self.parse_comment,
			TokenClasses.Number: self.parse_number,
			TokenClasses.Quote: self.parse_quote,
			TokenClasses.Identifier: self.parse_identifier,
			TokenClasses.Symbol: self.parse_symbol,
		}
		self._analyzers = {
			TokenClasses.WhiteSpace: self.analyze_white_spece,
			TokenClasses.Comment: self.analyze_comment,
			TokenClasses.Number: self.analyze_number,
			TokenClasses.Quote: self.analyze_quote,
			TokenClasses.Identifier: self.analyze_identifier,
			TokenClasses.Symbol: self.analyze_symbol,
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
			parser = self._parsers[self.analyze_class(source, index)]
			end, token = parser(source, index)
			index = end
			if token:
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
		for token_class, analyzer in self._analyzers.items():
			if analyzer(source, begin):
				return token_class

		assert False, f'Never. Unresolved token class. with character: {source[begin]}'

	def analyze_white_spece(self, source: str, begin: int) -> bool:
		"""トークン種別を解析(空白)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return source[begin] in self._definition.white_space

	def analyze_comment(self, source: str, begin: int) -> bool:
		"""トークン種別を解析(コメント)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return len([True for pair in self._definition.comment if source.startswith(pair['open'], begin)]) > 0

	def analyze_number(self, source: str, begin: int) -> bool:
		"""トークン種別を解析(数字)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return source[begin] in self._definition.number

	def analyze_quote(self, source: str, begin: int) -> bool:
		"""トークン種別を解析(引用符)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return len([True for pair in self._definition.quote if source.startswith(pair['open'], begin)]) > 0

	def analyze_identifier(self, source: str, begin: int) -> bool:
		"""トークン種別を解析(識別子)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return source[begin] in self._definition.identifier

	def analyze_symbol(self, source: str, begin: int) -> bool:
		"""トークン種別を解析(記号)

		Args:
			source: ソースコード
			begin: 読み取り開始位置
		Returns:
			True = 一致
		"""
		return source[begin] in self._definition.symbol['single']

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
			if source[end] not in self._definition.white_space:
				break

			end += 1

		return end, ''

	def parse_comment(self, source: str, begin: int) -> tuple[int, str]:
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
		if begin < end:
			end += len(pair['close'])
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
			if source[end] not in self._definition.number:
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
			if source[end] not in self._definition.identifier:
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
		if begin + 2 < len(source) and source[begin:begin + 2] in self._definition.symbol['pair']:
			return begin + 2, source[begin:begin + 2]
		else:
			return begin + 1, source[begin]


class PyTokenizer(ITokenizer):
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
