from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
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
		self.analyze_order = [
			TokenDomains.WhiteSpace,
			TokenDomains.Comment,
			TokenDomains.Symbol,
			TokenDomains.Quote,
			TokenDomains.Number,
			TokenDomains.Identifier,
		]
		self.white_space = ' \t\n\r\\'
		self.comment = [self.build_quote_pair('#', '\n')]
		self.quote = [self.build_quote_pair(f'{prefix}{quote}', quote) for prefix in ['', 'r', 'f'] for quote in ['"""', "'", '"']]
		self.number = '0123456789.'
		self.identifier = '_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
		self.symbol = '@#$.,:;(){}[]`=-+*/%&|^~!?<>'
		self.combined_symbols = [
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


class Lexer(ITokenizer):
	"""Lexicalパーサー"""

	def __init__(self, definition: TokenDefinition) -> None:
		"""インスタンスを生成

		Args:
			definition: トークン定義
		"""
		self._definition = definition
		self._analyzers = {
			TokenDomains.WhiteSpace: self.analyze_white_spece,
			TokenDomains.Comment: self.analyze_comment,
			TokenDomains.Quote: self.analyze_quote,
			TokenDomains.Number: self.analyze_number,
			TokenDomains.Identifier: self.analyze_identifier,
			TokenDomains.Symbol: self.analyze_symbol,
		}
		self._parsers = {
			TokenDomains.WhiteSpace: self.parse_white_spece,
			TokenDomains.Comment: self.parse_comment,
			TokenDomains.Quote: self.parse_quote,
			TokenDomains.Number: self.parse_number,
			TokenDomains.Identifier: self.parse_identifier,
			TokenDomains.Symbol: self.parse_symbol,
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
		Raises:
			ValueError: 未分類の文字種を処理
		"""
		for token_domain in self._definition.analyze_order:
			analyzer = self._analyzers[token_domain]
			if analyzer(source, begin):
				return token_domain

		raise ValueError(f'Never. Undetermine token domain. with character: {source[begin]}')

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
		Note:
			```
			* WhiteSpace: 改行を含まない空白。単なる区切り文字であり、無視して良い
			* LineBreak: 改行を含む空白。ステートメント、またはブロックの終了を表す
			```
		"""
		end = begin
		while end < len(source):
			if source[end] not in self._definition.white_space:
				break

			end += 1

		string = source[begin:end]
		if string.count('\n') == 0:
			return end, Token(TokenTypes.WhiteSpace, string)

		unespaced = ''.join(string.split('\\\n')) if string.count('\\\n') else string
		if unespaced.count('\n') == 0:
			return end, Token(TokenTypes.WhiteSpace, unespaced)

		line_break = self._format_line_break(unespaced)
		return end, Token(TokenTypes.LineBreak, line_break)

	def _format_line_break(self, string: str) -> str:
		"""改行を含む文字列から不要な要素を除去し、改行とインデント成分のみを残す

		Args:
			string: 元の文字列
		Returns:
			整形後の文字列
		Note:
			```
			先頭は改行。それ以降は同種のインデント
			出力例1: '\\n'
			出力例2: '\\n\\t\\t\\t'
			出力例3: '\\n   '
			### 整形ルール
			* 前方の空白を除去: ' \\t\\n\\t' -> '\\n\\t'
			* 中間の空行を除去: '\\n\\n\\t' -> '\\n\\t'
			* 末尾の空白を除去: '\\n\\t ' -> '\\n\\t'
			```
		"""
		_, *lines = string.split('\n')
		if len(lines) == 0:
			return '\n'

		last_line = lines[-1]
		if len(last_line) == 0:
			return '\n'

		tab = last_line[0]
		indent = ''
		for i in range(len(last_line)):
			if last_line[i] != tab:
				break

			indent += tab

		return f'\n{indent}'

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


class Tokenizer(ITokenizer):
	"""トークンパーサー"""

	def __init__(self, definition: TokenDefinition | None = None, lexer: ITokenizer | None = None) -> None:
		"""インスタンスを生成

		Args:
			definition: トークン定義 (default = None)
			lexer: Lexicalパーサー (default = None)
		"""
		self._definition = definition if definition else TokenDefinition()
		self._lexer = lexer if lexer else Lexer(self._definition)
		self._handlers = {
			TokenDomains.WhiteSpace: self.handle_white_space,
			TokenDomains.Symbol: self.handle_symbol,
		}

	@override
	def parse(self, source: str) -> list[Token]:
		"""ソースコードを解析し、トークンに分割

		Args:
			source: ソースコード
		Returns:
			トークンリスト
		"""
		tokens = self.lex_parse(source)
		return self._rebuild(tokens)

	def lex_parse(self, source: str) -> list[Token]:
		"""ソースコードを解析し、トークンに分割(字句解析のみ)

		Args:
			source: ソースコード
		Returns:
			トークンリスト
		"""
		return self._lexer.parse(source)

	@dataclass
	class Context:
		"""コンテキスト"""
		nest: int = 0
		enclosure: int = 0

	def _rebuild(self, tokens: list[Token]) -> list[Token]:
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
			end, alt_tokens = handler(context, tokens, index)
			index = end
			new_tokens.extend(alt_tokens)

		return new_tokens

	def handle_white_space(self, context: Context, tokens: list[Token], begin: int) -> tuple[int, list[Token]]:
		"""トークンリストを整形(空白)

		Args:
			context: コンテキスト
			tokens: トークンリスト
			begin: 読み取り開始位置
		Returns:
			(次の読み取り開始位置, トークンリスト)
		Note:
			```
			以下の規則に則り、改行/インデント/ディデントを判断する @see Lexer.parse_white_space
			* LineBreak以外は削除 (文法的に無視して良い)
			* LineBreakは先頭が必ず改行。それ以降は全てインデント
			```
		"""
		token = tokens[begin]
		if context.enclosure > 0:
			return begin + 1, []
		elif token.type != TokenTypes.LineBreak:
			return begin + 1, []
		elif context.nest < len(token.string) - 1:
			context.nest = len(token.string) - 1
			return begin + 1, [Token(TokenTypes.NewLine, token.string[0]), Token(TokenTypes.Indent, token.string[1:])]
		elif context.nest > len(token.string) - 1:
			context.nest = len(token.string) - 1
			return begin + 1, [Token(TokenTypes.NewLine, token.string[0]), Token(TokenTypes.Dedent, token.string[1:])]
		else:
			return begin + 1, [Token(TokenTypes.NewLine, token.string)]

	def handle_symbol(self, context: Context, tokens: list[Token], begin: int) -> tuple[int, list[Token]]:
		"""トークンリストを整形(記号)

		Args:
			context: コンテキスト
			tokens: トークンリスト
			begin: 読み取り開始位置
		Returns:
			(次の読み取り開始位置, トークンリスト)
		Note:
			```
			* 括弧のネストをコンテキストに記録
			* 記号トークンの合成
			```
		"""
		token = tokens[begin]
		if token.type in [TokenTypes.ParenL, TokenTypes.BraceL, TokenTypes.BracketL]:
			context.enclosure += 1
		elif token.type in [TokenTypes.ParenR, TokenTypes.BraceR, TokenTypes.BracketR]:
			context.enclosure -= 1

		return self._combine_symbol(tokens, begin)

	def _combine_symbol(self, tokens: list[Token], begin: int) -> tuple[int, list[Token]]:
		"""複数の文字より成り立つ記号(=トークン)の合成を行う

		Args:
			tokens: トークンリスト
			begin: 読み取り開始位置
		Returns:
			(次の読み取り開始位置, トークンリスト)
		"""
		for offset, expected in enumerate(self._definition.combined_symbols):
			if len(tokens) <= begin + len(expected) - 1:
				continue

			combine = ''.join([tokens[begin + i].string[0] for i in range(len(expected))])
			if combine != expected:
				continue

			token_type = TokenTypes(TokenTypes.BeginCombine.value + offset)
			return begin + len(expected), [Token(token_type, combine)]

		return begin + 1, [tokens[begin]]

