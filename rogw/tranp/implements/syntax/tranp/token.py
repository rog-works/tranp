from enum import Enum
from typing import NamedTuple


class TokenDomains(Enum):
	"""トークンドメイン"""
	WhiteSpace = 0
	Comment = 1
	Symbol = 2
	Quote = 3
	Number = 4
	Identifier = 5
	Operator = 6
	# 未分類
	Max = 6
	Unknown = 99


class TokenTypes(Enum):
	"""トークン種別"""
	# 空白
	WhiteSpace = 0x00
	LineBreak = 0x01
	NewLine = 0x02
	Indent = 0x03
	Dedent = 0x04
	# コメント
	Comment = 0x10
	# 記号
	At = 0x20
	Sharp = 0x21
	Dollar = 0x22
	Dot = 0x23
	Comma = 0x24
	Colon = 0x25
	SemiColon = 0x26
	ParenL = 0x27
	ParenR = 0x28
	BraceL = 0x29
	BraceR = 0x2A
	BracketL = 0x2B
	BracketR = 0x2C
	BackQuote = 0x2D
	BackSlash = 0x2E
	# 引用符
	String = 0x30
	Regexp = 0x31
	# 数字
	Digit = 0x40
	Decimal = 0x41
	# 識別子
	Name = 0x50
	Keyword = 0x51
	# 演算子
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
	Less = 0x6C
	Greater = 0x6D
	# 演算子(組)
	MinusEqual = 0x6E
	PlusEqual = 0x6F
	AsterEqual = 0x70
	SlashEqual = 0x71
	PercentEqual = 0x72
	AndEqual = 0x73
	OrEqual = 0x74
	HatEqual = 0x75
	TildeEqual = 0x76
	DoubleEqual = 0x77
	NotEqual = 0x78
	LessEqual = 0x79
	GreaterEqual = 0x7A
	DoubleAnd = 0x7B
	DoubleOr = 0x7C
	ShiftL = 0x7D
	ShiftR = 0x7E
	Arrow = 0x7F
	DoubleAster = 0x80
	WalrusEqual = 0x81
	Ellipsis = 0x82  # FIXME シンボルでは？
	# 未分類
	Empty = 0xFE
	Unknown = 0xFF


class Token(NamedTuple):
	"""トークン"""

	type: TokenTypes
	string: str

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
