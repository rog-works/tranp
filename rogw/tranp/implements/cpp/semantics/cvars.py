from collections.abc import Iterator
from enum import Enum
from typing import ClassVar

import rogw.tranp.compatible.cpp.cvar as cpp
import rogw.tranp.semantics.reflection.definition as refs
from rogw.tranp.errors import Errors
from rogw.tranp.semantics.reflection.base import IReflection


class CVars:
	"""C++型変数の操作ユーティリティー"""

	class Moves(Enum):
		"""移動操作の種別

		Attributes:
			Copy: 同種のコピー(実体 = 実体、アドレス = アドレス)
			New: メモリ確保(生ポインター)
			MakeSmart: メモリ確保(スマートポインター)
			ToActual: アドレス変数を実体参照
			ToAddress: 実体/参照から生ポインターに変換
			UnpackSmart: スマートポインターから生ポインターに変換
			Deny: 不正な移動操作
		"""
		Copy = 0
		New = 1
		MakeSmart = 2
		ToActual = 3
		ToAddress = 4
		UnpackSmart = 5
		Deny = 6

	class RelayOperators(Enum):
		"""リレー演算子の種別

		Attributes:
			Raw: 実体/参照
			Address: ポインター/スマートポインター
			Static: クラス
		"""
		Raw = 0
		Address = 1
		Static = 2

	class Verbs(Enum):
		"""操作メソッド Note: @see rogw.tranp.compatible.cpp.cvar"""
		ToAddrId = 'to_addr_id'
		ToAddrHex = 'to_addr_hex'
		ToImmutable = 'to_immutable'
		On = 'on'
		Emtpy = 'empty'
		New = 'new'
		Move = 'move'
		CopyProxy = 'copy_proxy'
		Down = 'down'
		AsA = 'as_a'

	class Casts(Enum):
		"""参照変換メソッド Note: @see rogw.tranp.compatible.cpp.cvar"""
		Raw = 'raw'
		Ref = 'ref'
		Addr = 'addr'
		Const = 'const'

		@classmethod
		def in_value(cls, key: str) -> bool:
			"""Args: key: キー Returns: True = 存在"""
			for value in cls:
				if value.value == key:
					return True

			return False

		@classmethod
		def values(cls) -> Iterator[str]:
			"""Returns: 型変換メソッドのイテレーター"""
			for value in cls:
				yield value.value

	class Types(Enum):
		"""C++型変数種別"""
		CRaw = 0x0001
		CRef = 0x0002
		CP = 0x0010
		CWP = 0x0020
		CUP = 0x0040
		CSP = 0x0080
		# 修飾子
		Const = 0x1000
		# 不変型
		CRawConst = 0x1001
		CRefConst = 0x1002
		CPConst = 0x1010
		CWPConst = 0x1020
		CUPConst = 0x1040
		CSPConst = 0x1080
		# マスク
		RawMask = 0x000f
		AddrMask = 0x00f0
		AddrRawMask = CP | CWP
		AddrSmartMask = CUP | CSP

	TypeToOperator: ClassVar[dict[Types, RelayOperators]] = {
		Types.CP: RelayOperators.Address,
		Types.CWP: RelayOperators.Address,
		Types.CUP: RelayOperators.Address,
		Types.CSP: RelayOperators.Address,
		Types.CRef: RelayOperators.Raw,
		Types.CPConst: RelayOperators.Address,
		Types.CUPConst: RelayOperators.Address,
		Types.CSPConst: RelayOperators.Address,
		Types.CRefConst: RelayOperators.Raw,
		Types.CRawConst: RelayOperators.Raw,
		Types.CRaw: RelayOperators.Raw,
	}
	CastToMove: ClassVar[dict[tuple[Types, str], Moves]] = {
		(Types.CP, Casts.Raw.value): Moves.ToActual,
		(Types.CP, Casts.Ref.value): Moves.ToActual,
		(Types.CP, Casts.Const.value): Moves.Copy,
		(Types.CWP, Casts.Raw.value): Moves.ToActual,
		(Types.CWP, Casts.Addr.value): Moves.Copy,
		(Types.CUP, Casts.Raw.value): Moves.ToActual,
		(Types.CUP, Casts.Ref.value): Moves.ToActual,
		(Types.CUP, Casts.Addr.value): Moves.UnpackSmart,
		(Types.CUP, Casts.Const.value): Moves.Copy,
		(Types.CSP, Casts.Raw.value): Moves.ToActual,
		(Types.CSP, Casts.Ref.value): Moves.ToActual,
		(Types.CSP, Casts.Addr.value): Moves.UnpackSmart,
		(Types.CSP, Casts.Const.value): Moves.Copy,
		(Types.CRef, Casts.Raw.value): Moves.Copy,
		(Types.CRef, Casts.Addr.value): Moves.ToAddress,
		(Types.CRef, Casts.Const.value): Moves.Copy,
		(Types.CPConst, Casts.Raw.value): Moves.ToActual,
		(Types.CPConst, Casts.Ref.value): Moves.ToActual,
		(Types.CUPConst, Casts.Raw.value): Moves.ToActual,
		(Types.CUPConst, Casts.Ref.value): Moves.ToActual,
		(Types.CUPConst, Casts.Addr.value): Moves.UnpackSmart,
		(Types.CSPConst, Casts.Raw.value): Moves.ToActual,
		(Types.CSPConst, Casts.Ref.value): Moves.ToActual,
		(Types.CSPConst, Casts.Addr.value): Moves.UnpackSmart,
		(Types.CRefConst, Casts.Raw.value): Moves.Copy,
		(Types.CRefConst, Casts.Addr.value): Moves.ToAddress,
		(Types.CRawConst, Casts.Raw.value): Moves.Copy,
		(Types.CRawConst, Casts.Ref.value): Moves.Copy,
		(Types.CRawConst, Casts.Addr.value): Moves.ToAddress,
	}

	def __init__(self, name_to_key: dict[str, str] = {}) -> None:
		"""インスタンスを生成

		Args:
			name_to_key: 新規変数型名とC++型変数名のマップ (default = {})
		"""
		self._name_to_type = {
			cpp.CRaw.__name__: CVars.Types.CRaw,
			cpp.CRef.__name__: CVars.Types.CRef,
			cpp.CP.__name__: CVars.Types.CP,
			cpp.CWP.__name__: CVars.Types.CWP,
			cpp.CUP.__name__: CVars.Types.CUP,
			cpp.CSP.__name__: CVars.Types.CSP,
			cpp.CRawConst.__name__: CVars.Types.CRawConst,
			cpp.CRefConst.__name__: CVars.Types.CRefConst,
			cpp.CPConst.__name__: CVars.Types.CPConst,
			cpp.CUPConst.__name__: CVars.Types.CUPConst,
			cpp.CSPConst.__name__: CVars.Types.CSPConst,
		}
		for add_name, org_name in name_to_key.items():
			assert add_name not in self._name_to_type, Errors.InvalidSchema(add_name)
			self._name_to_type[add_name] = self._name_to_type[org_name]

	def to_type(self, symbol: IReflection) -> Types:
		"""Args: symbol: シンボル Returns: C++型変数種別

		Note:
			```
			* nullはポインターとして扱う
			* XXX 返却値を既定のC++変数型のキーに変換するべきでは？(テンプレートの型名変換のため)
			```
		"""
		if symbol.types.domain_name in self._name_to_type:
			return self._name_to_type[symbol.types.domain_name]
		elif symbol.impl(refs.Object).type_is(None):
			return CVars.Types.CP
		else:
			return CVars.Types.CRaw

	def type_to_name(self, var_type: Types) -> str:
		"""Args: var_type: C++型変数種別 Returns: C++型変数名"""
		for var_name, in_var_type in self._name_to_type.items():
			if var_type == in_var_type:
				return var_name

		assert False, Errors.Never

	def name_to_type(self, var_name: str) -> Types:
		"""Args: var_name: C++型変数名 Returns: C++型変数種別"""
		return self._name_to_type[var_name]

	def var_names(self) -> Iterator[str]:
		"""Returns: イテレーター(C++型変数名)"""
		for key in self._name_to_type.keys():
			yield key

	def equals(self, var_type: Types, expect_type: Types) -> bool:
		"""Args: var_type: C++型変数種別, expect_type: C++型変数種別 Returns: True = 同じ"""
		return var_type == expect_type

	def contains(self, var_type: Types, mask: Types) -> bool:
		"""Args: var_type: C++型変数種別, mask: 種別マスク Returns: True = 含む"""
		return (var_type.value & mask.value) != 0

	def to_operator(self, var_type: Types) -> RelayOperators:
		"""Args: var_type: C++型変数種別 Returns: リレー演算子"""
		return CVars.TypeToOperator[var_type]

	def to_move(self, var_type: Types, cast_key: str) -> Moves:
		"""Args: var_type: C++型変数種別, cast_key: 型変換メソッド名 Returns: 移動操作の種別"""
		key = (var_type, cast_key)
		return CVars.CastToMove.get(key, CVars.Moves.Deny)

	# @classmethod
	# @deprecated
	# def analyze_move(cls, accept: IReflection, value: IReflection, value_on_new: bool, declared: bool) -> Moves:
	# 	"""移動操作を解析

	# 	Args:
	# 		accept: 受け入れ側
	# 		value: 入力側
	# 		value_on_new: True = インスタンス生成
	# 		declared: True = 変数宣言時
	# 	Returns:
	# 		移動操作の種別
	# 	Note:
	# 		@deprecated 未使用のため削除を検討
	# 	"""
	# 	accept_key = cls.key_from(accept)
	# 	value_key = cls.key_from(value)
	# 	return cls.move_by(accept_key, value_key, value_on_new, declared)

	# @classmethod
	# @deprecated
	# def move_by(cls, accept_key: str, value_key: str, value_on_new: bool, declared: bool) -> Moves:
	# 	"""移動操作を解析

	# 	Args:
	# 		accept_key: 受け入れ側
	# 		value_key: 入力側
	# 		value_on_new: True = インスタンス生成
	# 		declared: True = 変数宣言時
	# 	Returns:
	# 		移動操作の種別
	# 	Note:
	# 		@deprecated 未使用のため削除を検討
	# 	"""
	# 	if cls.is_raw_ref(accept_key) and not declared:
	# 		return cls.Moves.Deny

	# 	if cls.is_addr_smart(accept_key) and cls.is_raw(value_key) and value_on_new:
	# 		return cls.Moves.MakeSmart
	# 	elif cls.is_addr_raw(accept_key) and cls.is_raw(value_key) and value_on_new:
	# 		return cls.Moves.New
	# 	elif cls.is_addr_raw(accept_key) and cls.is_raw(value_key):
	# 		return cls.Moves.ToAddress
	# 	elif cls.is_raw(accept_key) and cls.is_addr(value_key):
	# 		return cls.Moves.ToActual
	# 	elif cls.is_addr_raw(accept_key) and cls.is_addr_smart(value_key):
	# 		return cls.Moves.UnpackSmart
	# 	elif cls.is_addr_raw(accept_key) and cls.is_addr_raw(value_key):
	# 		return cls.Moves.Copy
	# 	elif cls.is_addr_smart(accept_key) and cls.is_addr_smart(value_key):
	# 		return cls.Moves.Copy
	# 	elif cls.is_raw(accept_key) and cls.is_raw(value_key):
	# 		return cls.Moves.Copy
	# 	else:
	# 		return cls.Moves.Deny
