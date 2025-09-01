from enum import Enum
from typing import ClassVar, NamedTuple, TypedDict


class TokenDomains(Enum):
	"""トークンドメイン"""
	WhiteSpace = 0
	Comment = 1
	Quote = 2
	Number = 3
	Identifier = 4
	Symbol = 5
	# 未分類
	Max = 5
	Unknown = 99


class TokenTypes(Enum):
	"""トークン種別"""
	# 空白(一般文書)
	WhiteSpace = 0x00
	LineBreak = 0x01
	EOF = 0x02
	# 空白(言語構造)
	NewLine = 0x03
	Indent = 0x04
	Dedent = 0x05
	# コメント
	Comment = 0x10
	# 引用符
	String = 0x20
	Regexp = 0x21
	# 数字
	Digit = 0x30
	Decimal = 0x31
	# 識別子
	Name = 0x40
	# 記号
	At = 0x50
	Sharp = 0x51
	Dollar = 0x52
	Dot = 0x53
	Comma = 0x54
	Colon = 0x55
	SemiColon = 0x56
	ParenL = 0x57
	ParenR = 0x58
	BraceL = 0x59
	BraceR = 0x5A
	BracketL = 0x5B
	BracketR = 0x5C
	BackQuote = 0x5D
	# 記号(演算子)
	Equal = 0x5E
	Minus = 0x5F
	Plus = 0x60
	Aster = 0x61
	Slash = 0x62
	Percent = 0x63
	And = 0x64
	Or = 0x65
	Hat = 0x66
	Tilde = 0x67
	Exclamation = 0x68
	Question = 0x69
	Less = 0x6A
	Greater = 0x6B
	# 記号(組)
	MinusEqual = 0x70
	PlusEqual = 0x71
	AsterEqual = 0x72
	SlashEqual = 0x73
	PercentEqual = 0x74
	AndEqual = 0x75
	OrEqual = 0x76
	HatEqual = 0x77
	TildeEqual = 0x78
	DoubleEqual = 0x79
	NotEqual = 0x7A
	LessEqual = 0x7B
	GreaterEqual = 0x7C
	DoubleAnd = 0x7D
	DoubleOr = 0x7E
	ShiftL = 0x7F
	ShiftR = 0x80
	Arrow = 0x81
	DoubleAster = 0x82
	WalrusEqual = 0x83
	Ellipsis = 0x84
	# オフセット
	BeginCombine = 0x70
	# 未分類
	Empty = 0xFE
	Unknown = 0xFF


class Token:
	"""トークン"""

	def __init__(self, type: TokenTypes, string: str, source_map: 'SourceMap | None' = None) -> None:
		"""インスタンスを生成

		Args:
			type: トークン種別
			string: 文字列
			source_map: ソースマップ (default = None)
		"""
		self._type = type
		self._string = string
		self.source_map = source_map if source_map else self.SourceMap.empty()

	@property
	def type(self) -> TokenTypes:
		"""Returns: トークン種別"""
		return self._type

	@property
	def string(self) -> str:
		"""Returns: 文字列"""
		return self._string

	@property
	def string_of_unescaped(self) -> str:
		"""Returns: 文字列(エスケープ解除)"""
		return self._string.encode().decode('unicode_escape') if self._string.find('\\') != -1 else self._string

	@property
	def domain(self) -> TokenDomains:
		"""Returns: トークンドメイン"""
		d = self.type.value >> 4 & 0xf
		if d == 0xf:
			return TokenDomains.Unknown
		else:
			return TokenDomains(min(d, TokenDomains.Max.value))

	def simplify(self) -> tuple[TokenTypes, str]:
		"""Returns: 簡易書式"""
		return (self.type, self.string)

	def joined(self, *others: 'Token') -> 'Token':
		"""自身をベースに指定のトークンと合成し、新たにインスタンスを生成

		Args:
			*others: 合成するトークンリスト
		Returns:
			合成後のトークン
		"""
		new_string = ''.join([self.string, *[token.string for token in others]])
		new_map = self.SourceMap(
			min([token.source_map.begin_line for token in others]),
			min([token.source_map.begin_column for token in others]),
			max([token.source_map.end_line for token in others]),
			max([token.source_map.end_column for token in others]),
		)
		return Token(self.type, new_string, new_map)

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		begin = f'({self.source_map.begin_line}, {self.source_map.begin_column})'
		end = f'({self.source_map.end_line}, {self.source_map.end_column})'
		return f'<{self.__class__.__name__}[{self.type.name}]: {repr(self.string)} {begin}..{end}>'

	def __hash__(self) -> int:
		"""Returns: ハッシュ値"""
		return hash(self.__repr__())

	def __eq__(self, other: 'Token | tuple[TokenTypes, str]') -> bool:
		"""Args: other: 比較対象 Returns: True = 一致"""
		if isinstance(other, Token):
			return self.type == other.type and self.string == other.string
		else:
			return self.type == other[0] and self.string == other[1]

	def __ne__(self, other: 'Token | tuple[TokenTypes, str]') -> bool:
		"""Args: other: 比較対象 Returns: True = 不一致"""
		return not self.__eq__(other)

	def to_new_line(self) -> 'Token':
		"""インスタンスを変換

		Returns:
			インスタンス(改行)
		Note:
			```
			* 「改行(=ステートメントの終了)」を表す
			* 最終的に「改行」を表すトークンはこれ1種となる
			### 置き換え・削除
			* 削除: 文法上不要な改行
			* 置換: 環境依存の改行('\\r\\n')
			* 置換: 言語依存のステートメント終了(';')
			```
		"""
		assert self.domain == TokenDomains.WhiteSpace, f'Must be WhiteSpace domain. from: {self.type}'
		return Token(TokenTypes.NewLine, '\n', self.source_map)

	def to_indent(self) -> 'Token':
		"""インスタンスを変換

		Returns:
			インスタンス(ブロック開始)
		Note:
			```
			* 言語の仕様により実際に対応する文字種が変化する
			* 論理ブロックの言語ではスペース(' ')、またはタブ('\t')
			* 物理ブロックの言語では主に中括弧('{')
			* このトークンは言語の仕様に依存せず、いずれの場合でも「ブロック開始」を表す
			```
		"""
		assert self.domain == TokenDomains.WhiteSpace, f'Must be WhiteSpace domain. from: {self.type}'
		return Token(TokenTypes.Indent, '\\INDENT', self.source_map)

	def to_dedent(self) -> 'Token':
		"""インスタンスを変換

		Returns:
			インスタンス(ブロック終了)
		Note:
			```
			* 「ブロック開始」と同仕様 @see indent#Note
			* 「ブロック終了」を表す
			```
		"""
		assert self.domain == TokenDomains.WhiteSpace, f'Must be WhiteSpace domain. from: {self.type}'
		return Token(TokenTypes.Dedent, '\\DEDENT', self.source_map)

	@classmethod
	def EOF(cls) -> 'Token':
		"""インスタンスを生成

		Returns:
			インスタンス(ファイル終了)
		Note:
			```
			* 字句解析中にのみ存在
			* 最終的に改行のトークンに置き換えられる
			```
		"""
		return cls(TokenTypes.EOF, '\\EOF', cls.SourceMap.EOF())

	@classmethod
	def empty(cls) -> 'Token':
		"""インスタンスを生成

		Returns:
			インスタンス(空)
		Note:
			```
			* 空を表すトークン
			* 主にマッチングの結果が0件の際のエントリーとして用いる
			```
		"""
		return cls(TokenTypes.Empty, '')

	class SourceMap(NamedTuple):
		"""ソースマップ"""

		begin_line: int
		begin_column: int
		end_line: int
		end_column: int

		@classmethod
		def make(cls, source: str, begin: int, end: int) -> 'Token.SourceMap':
			"""インスタンスを生成

			Args:
				source: ソースコード
				begin: 開始位置
				end: 終了位置
			Returns:
				ソースマップ
			"""
			begin_line = source.count('\n', 0, begin)
			begin_ln_index = source.rfind('\n', 0, begin)
			begin_line_start = begin_ln_index + 1 if begin_ln_index != -1 else 0
			begin_column = begin - begin_line_start
			between_line_num = source.count('\n', begin, end)
			end_line = begin_line + between_line_num
			end_ln_index = source.rfind('\n', begin_line_start, end)
			end_line_start = end_ln_index + 1 if end_ln_index != -1 else begin_line_start
			end_column = end - end_line_start
			return cls(begin_line, begin_column, end_line, end_column)

		@classmethod
		def EOF(cls) -> 'Token.SourceMap':
			"""Returns: インスタンス(EOF) Note: XXX 実在がない、且つ特別なコードと言う意味で-1を設定"""
			return cls(-1, -1, -1, -1)

		@classmethod
		def empty(cls) -> 'Token.SourceMap':
			"""Returns: インスタンス(空)"""
			return cls(0, 0, 0, 0)


QuotePair = TypedDict('QuotePair', {'open': str, 'close': str})


class TokenDefinition:
	"""トークン定義"""

	MatchBeginOrEnd: ClassVar = 'BEGIN|END'

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
		self.white_space = '\\ \t\f\n\r'
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
		self.post_filters = [
			(TokenTypes.Comment, '*'),
			(TokenTypes.WhiteSpace, '*'),
			(TokenTypes.LineBreak, '[ \t\f]*\\[ \t\f]*\r?\n'),
			# XXX 1行目と最終行の空行は固有のマッチパターンで削除
			(TokenTypes.LineBreak, self.MatchBeginOrEnd),
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
