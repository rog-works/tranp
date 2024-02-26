from enum import Enum
from types import UnionType

from rogw.tranp.analyze.symbol import SymbolRaw
from rogw.tranp.analyze.symbols import Symbols
import rogw.tranp.compatible.cpp.object as cpp
import rogw.tranp.compatible.python.embed as __alias__


class CVars:
	"""C++変数型の操作ユーティリティー"""

	class Moves(Enum):
		"""移動操作の種別

		Attributes:
			Copy: 同種のコピー(実体 = 実体、アドレス = アドレス)
			New: メモリ確保(生ポインター)
			MakeSp: メモリ確保(スマートポインター)
			ToActual: アドレス変数を実体参照
			ToAddress: 実体/参照から生ポインターに変換
			UnpackSp: スマートポインターから生ポインターに変換
			Deny: 不正な移動操作
		"""

		Copy = 0
		New = 1
		MakeSp = 2
		ToActual = 3
		ToAddress = 4
		UnpackSp = 5
		Deny = 6

	class Accessors(Enum):
		"""アクセス修飾子の種別

		Attributes:
			Raw: 実体/参照
			Address: ポインター/スマートポインター
			Static: クラス
		"""

		Raw = 0
		Address = 1
		Static = 2

	@classmethod
	def analyze_move(cls, symbols: Symbols, accept: SymbolRaw, value: SymbolRaw, value_on_new: bool, declared: bool) -> Moves:
		"""移動操作を解析

		Args:
			symbols (Symbols): シンボルリゾルバー
			accept (SymbolRaw): 受け入れ側
			value (SymbolRaw): 入力側
			value_on_new (bool): True = インスタンス生成
			declared (bool): True = 変数宣言時
		Returns:
			Moves: 移動操作の種別
		"""
		accept_key = cls.key_from(symbols, accept)
		value_key = cls.key_from(symbols, value)
		return cls.move_by(accept_key, value_key, value_on_new, declared)

	@classmethod
	def move_by(cls, accept_key: str, value_key: str, value_on_new: bool, declared: bool) -> Moves:
		"""移動操作を解析

		Args:
			accept_key (str): 受け入れ側
			value_key (str): 入力側
			value_on_new (bool): True = インスタンス生成
			declared (bool): True = 変数宣言時
		Returns:
			Moves: 移動操作の種別
		"""
		if cls.is_raw_ref(accept_key) and not declared:
			return cls.Moves.Deny

		if cls.is_addr_sp(accept_key) and cls.is_raw(value_key) and value_on_new:
			return cls.Moves.MakeSp
		elif cls.is_addr_p(accept_key) and cls.is_raw(value_key) and value_on_new:
			return cls.Moves.New
		elif cls.is_addr_p(accept_key) and cls.is_raw(value_key):
			return cls.Moves.ToAddress
		elif cls.is_raw(accept_key) and cls.is_addr(value_key):
			return cls.Moves.ToActual
		elif cls.is_addr_p(accept_key) and cls.is_addr_sp(value_key):
			return cls.Moves.UnpackSp
		elif cls.is_addr_p(accept_key) and cls.is_addr_p(value_key):
			return cls.Moves.Copy
		elif cls.is_addr_sp(accept_key) and cls.is_addr_sp(value_key):
			return cls.Moves.Copy
		elif cls.is_raw(accept_key) and cls.is_raw(value_key):
			return cls.Moves.Copy
		else:
			return cls.Moves.Deny

	@classmethod
	def is_raw(cls, key: str) -> bool:
		"""実体か判定

		Args:
			key (str): C++変数型の種別キー
		Returns:
			bool: True = 実体/参照
		"""
		return key in [cpp.CRaw.__name__, cpp.CRef.__name__]

	@classmethod
	def is_addr(cls, key: str) -> bool:
		"""アドレスか判定

		Args:
			key (str): C++変数型の種別キー
		Returns:
			bool: True = ポインター/スマートポインター
		"""
		return key in [cpp.CP.__name__, cpp.CSP.__name__]

	@classmethod
	def is_raw_raw(cls, key: str) -> bool:
		"""実体か判定

		Args:
			key (str): C++変数型の種別キー
		Returns:
			bool: True = 実体
		"""
		return key == cpp.CRaw.__name__

	@classmethod
	def is_raw_ref(cls, key: str) -> bool:
		"""参照か判定

		Args:
			key (str): C++変数型の種別キー
		Returns:
			bool: True = 参照
		"""
		return key == cpp.CRef.__name__

	@classmethod
	def is_addr_p(cls, key: str) -> bool:
		"""ポインターか判定

		Args:
			key (str): C++変数型の種別キー
		Returns:
			bool: True = ポインター
		"""
		return key == cpp.CP.__name__

	@classmethod
	def is_addr_sp(cls, key: str) -> bool:
		"""スマートポインターか判定

		Args:
			key (str): C++変数型の種別キー
		Returns:
			bool: True = スマートポインター
		"""
		return key == cpp.CSP.__name__

	@classmethod
	def keys(cls) -> list[str]:
		"""C++変数型の種別キー一覧を生成

		Returns:
			list[str]: 種別キー一覧
		"""
		return [cvar.__name__ for cvar in [cpp.CP, cpp.CSP, cpp.CRef, cpp.CRaw]]

	@classmethod
	def key_from(cls, symbols: Symbols, symbol: SymbolRaw) -> str:
		"""シンボルからC++変数型の種別キーを取得

		Args:
			symbols (Symbols): シンボルリゾルバー
			symbol (SymbolRaw): シンボル
		Returns:
			str: 種別キー
		Note:
			nullはポインターとして扱う
		"""
		if symbols.is_a(symbol, None):
			return cpp.CP.__name__

		var_type = cls.unpack_with_nullable(symbols, symbol)
		if var_type.types.domain_name in cls.keys():
			return var_type.types.domain_name

		return cpp.CRaw.__name__

	@classmethod
	def unpack_with_nullable(cls, symbols: Symbols, symbol: SymbolRaw) -> SymbolRaw:
		"""Nullableのシンボルの変数の型をアンパック。Nullable以外の型はそのまま返却

		Args:
			symbols (Symbols): シンボルリゾルバー
			symbol (SymbolRaw): シンボル
		Returns:
			SymbolRaw: 変数の型
		Note:
			許容するNullableの書式 (例: 'CP[Class] | None')
			@see Py2Cpp.on_union_type
		"""
		if symbols.is_a(symbol, UnionType) and len(symbol.attrs) == 2:
			is_0_null = symbols.is_a(symbol.attrs[0], None)
			is_1_null = symbols.is_a(symbol.attrs[1], None)
			if is_0_null != is_1_null:
				return symbol.attrs[1 if is_0_null else 0]

		return symbol

	@classmethod
	def to_accessor(cls, key: str) -> Accessors:
		"""C++変数型に応じたアクセス修飾子に変換

		Args:
			key (str): C++変数型の種別キー
		Returns:
			Accessors: アクセス修飾子種別
		"""
		accessors = {
			cpp.CRaw.__name__: cls.Accessors.Raw,
			cpp.CRef.__name__: cls.Accessors.Raw,
			cpp.CP.__name__: cls.Accessors.Address,
			cpp.CSP.__name__: cls.Accessors.Address,
		}
		return accessors[key]
