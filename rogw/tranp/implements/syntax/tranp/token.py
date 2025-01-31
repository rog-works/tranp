from enum import Enum
from typing import NamedTuple


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
	def EOF(cls) -> 'Token':
		"""Returns: ファイルの終端を表すインスタンス"""
		return cls(TokenTypes.EOF, 'EOF')

	@classmethod
	def empty(cls) -> 'Token':
		"""Returns: 空を表すインスタンス"""
		return cls(TokenTypes.Empty, '')

	@property
	def domain(self) -> TokenDomains:
		"""Returns: トークンドメイン"""
		d = self.type.value >> 4 & 0xf
		if d == 0xf:
			return TokenDomains.Unknown
		else:
			return TokenDomains(min(d, TokenDomains.Max.value))
