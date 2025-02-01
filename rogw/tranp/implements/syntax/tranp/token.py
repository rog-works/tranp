from enum import Enum
from typing import NamedTuple, TypedDict


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
	# 空白
	WhiteSpace = 0x00
	LineBreak = 0x01
	# 空白(特殊)
	NewLine = 0x02
	Indent = 0x03
	Dedent = 0x04
	EOF = 0x05
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


class Token(NamedTuple):
	"""トークン"""

	type: TokenTypes
	string: str

	@classmethod
	def new_line(cls) -> 'Token':
		"""インスタンスを生成

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
		return cls(TokenTypes.NewLine, '\n')

	@classmethod
	def indent(cls) -> 'Token':
		"""インスタンスを生成

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
		return cls(TokenTypes.Indent, '\\INDENT')

	@classmethod
	def dedent(cls) -> 'Token':
		"""インスタンスを生成

		Returns:
			インスタンス(ブロック終了)
		Note:
			```
			* 「ブロック開始」と同仕様 @see indent#Note
			* 「ブロック終了」を表す
			```
		"""
		return cls(TokenTypes.Dedent, '\\DEDENT')

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
		return cls(TokenTypes.EOF, '\\EOF')

	@classmethod
	def empty(cls) -> 'Token':
		"""インスタンスを生成

		Returns:
			インスタンス(空)
		Note:
			* 空を表すトークン
			* 主にマッチングの結果が0件の際のエントリーとして用いる
		"""
		return cls(TokenTypes.Empty, '')

	@property
	def domain(self) -> TokenDomains:
		"""Returns: トークンドメイン"""
		d = self.type.value >> 4 & 0xf
		if d == 0xf:
			return TokenDomains.Unknown
		else:
			return TokenDomains(min(d, TokenDomains.Max.value))

	def joined(self, *others: 'Token') -> 'Token':
		"""自身をベースに指定のトークンと合成し、新たにインスタンスを生成

		Args:
			*others: 合成するトークンリスト
		Returns:
			合成後のトークン
		Note:
			自身の種別を引き継ぎ、文字列のみ合成
		"""
		return Token(self.type, ''.join([self.string, *[token.string for token in others]]))


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
		self.pre_filters = {
			'comment_spaces': r'[ \t\f]*#.*$',
			'line_end_spaces': r'[ \t\f\r]+$',
		}
		self.post_filters = [
			(TokenTypes.Comment, '*'),
			(TokenTypes.WhiteSpace, '*'),
			(TokenTypes.LineBreak, '[ \t\f]*\\[ \t\f]*\r?\n'),
			(TokenTypes.LineBreak, 'BEGIN|END'),
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
