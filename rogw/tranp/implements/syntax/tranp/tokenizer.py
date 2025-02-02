from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from io import BytesIO
import re
import token as PyTokenTypes
from tokenize import tokenize
from typing import override

from rogw.tranp.implements.syntax.tranp.token import Token, TokenDefinition, TokenDomains, TokenTypes


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
		tokens = self.parse_impl(source)
		tokens = self.post_filter(tokens)
		tokens.append(Token.EOF())
		return tokens

	def parse_impl(self, source: str) -> list[Token]:
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

	def post_filter(self, tokens: list[Token]) -> list[Token]:
		"""トークンリストに事後フィルターを適用

		Args:
			tokens: トークンリスト
		Returns:
			トークンリスト
		Note:
			```
			### 除外ルール
			* フィルター適用後に空になるトークンを除外する
			* 除外したトークンの前後が改行要素の場合は、前後の改行要素を合成
			* 先頭要素を除外する際、次の要素が改行要素の場合は削除
			* 末尾要素を除外する際、前の要素が改行要素の場合は削除
			```
		"""
		def to_empty(post_filter: str, token: Token, index: int, num: int) -> bool:
			"""Returns: True = フィルター後に空になる"""
			if post_filter == '*':
				return True
			elif post_filter == TokenDefinition.MatchBeginOrEnd:
				return index == 0 or index == num - 1

			new_string = ''.join(re.split(post_filter, token.string))
			return len(new_string) == 0

		def line_break_at(tokens: list[Token], index: int) -> bool:
			"""Returns: True = 対象が存在し、且つ改行要素"""
			return index >= 0 and index < len(tokens) and tokens[index].type == TokenTypes.LineBreak

		new_tokens = tokens.copy()
		for token_type, post_filter in self._definition.post_filters:
			index = 0
			while index < len(new_tokens):
				token = new_tokens[index]
				if token.type != token_type or not to_empty(post_filter, token, index, len(new_tokens)):
					index += 1
					continue

				if index == 0 and line_break_at(new_tokens, index + 1):
					del new_tokens[index + 1]
					del new_tokens[index]
				elif index == len(new_tokens) - 1 and line_break_at(new_tokens, index - 1):
					del new_tokens[index]
					del new_tokens[index - 1]
				elif line_break_at(new_tokens, index - 1) and line_break_at(new_tokens, index + 1):
					new_tokens[index - 1] = new_tokens[index - 1].joined(new_tokens[index + 1])
					del new_tokens[index + 1]
					del new_tokens[index]
				else:
					del new_tokens[index]

		return new_tokens

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
			### 前提
			* 事前フィルターによって余分な空白や空行は削除されていると見做して処理
			### 出力のまとめ
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
		if string.count('\\\n'):
			string = ''.join(string.split('\\\n'))

		if string.count('\n') == 0:
			return end, Token(TokenTypes.WhiteSpace, string, Token.SourceMap.make(source, begin, end))
		else:
			return end, Token(TokenTypes.LineBreak, string, Token.SourceMap.make(source, begin, end))

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
			end += 0 if pair['close'] == '\n' else len(pair['close'])
			return end, Token(TokenTypes.Comment, source[begin:end], Token.SourceMap.make(source, begin, end))
		else:
			end = len(source)
			return end, Token(TokenTypes.Comment, source[begin:end], Token.SourceMap.make(source, begin, end))

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

			prev = max(end, index - 1)
			end = index + len(pair['close'])
			if not (source[prev] == '\\'):
				break

		value = source[begin:end]
		token_type = TokenTypes.Regexp if value[0] == '/' else TokenTypes.String
		return end, Token(token_type, value, Token.SourceMap.make(source, begin, end))

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
		return end, Token(token_type, value, Token.SourceMap.make(source, begin, end))

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

		return end, Token(TokenTypes.Name, source[begin:end], Token.SourceMap.make(source, begin, end))

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
		end = begin + 1
		return end, Token(token_type, value, Token.SourceMap.make(source, begin, end))


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
			### 処理ルール
			* WhiteSpace: 削除
			* EOF: 改行, ネスト x ディデント
			* LineBreak:
				* 最終行の文字数をインデントとしてカウント
				* ネストが増加: 改行, インデント
				* ネストが減少: 改行, 減少ネスト x ディデント
				* ネストが同じ: 改行
			```
		"""
		token = tokens[begin]
		if context.enclosure > 0:
			return begin + 1, []
		elif token.type == TokenTypes.WhiteSpace:
			return begin + 1, []
		elif token.type == TokenTypes.EOF:
			dedents = [token.to_dedent()] * context.nest
			context.nest = 0
			return begin + len(token.string), [token.to_new_line(), *dedents]

		assert token.type == TokenTypes.LineBreak, f'Never. token type: {token.type}'

		indent = len(token.string.split('\n')[-1])
		if context.nest < indent:
			context.nest = indent
			return begin + 1, [token.to_new_line(), token.to_indent()]
		elif context.nest > indent:
			next_nest = indent
			dedents = [token.to_dedent()] * (context.nest - next_nest)
			context.nest = next_nest
			return begin + 1, [token.to_new_line(), *dedents]
		else:
			return begin + 1, [token.to_new_line()]

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

		combined = self._try_combine_symbol(tokens, begin)
		if combined.type == TokenTypes.Empty:
			return begin + 1, [tokens[begin]]
		else:
			return begin + len(combined.string), [combined]

	def _try_combine_symbol(self, tokens: list[Token], begin: int) -> Token:
		"""複数の文字より成り立つ記号(=トークン)の合成を試行する

		Args:
			tokens: トークンリスト
			begin: 読み取り開始位置
		Returns:
			トークン
		"""
		end = begin + 1
		while end < len(tokens) and tokens[end].domain == TokenDomains.Symbol:
			end += 1

		if end - begin == 1:
			return Token.empty()

		candidate = ''.join([token.string for token in tokens[begin:end]])
		founds = [index for index, expected in enumerate(self._definition.combined_symbols) if candidate.startswith(expected)]
		if len(founds) == 0:
			return Token.empty()

		offset = founds[0]
		token_type = TokenTypes(TokenTypes.BeginCombine.value + offset)
		combine = self._definition.combined_symbols[offset]
		base = tokens[begin]
		combine_map = Token.SourceMap(base.source_map.begin_line, base.source_map.begin_column, base.source_map.end_line, base.source_map.end_column + len(combine))
		return Token(token_type, combine, combine_map)
