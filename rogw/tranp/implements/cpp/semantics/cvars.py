from collections.abc import Iterator
from enum import Enum
from typing import ClassVar

import rogw.tranp.compatible.cpp.object as cpp
import rogw.tranp.semantics.reflection.definition as refs
from rogw.tranp.semantics.reflection.base import IReflection


class CVars:
	"""C++型変数の操作ユーティリティー"""

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
		"""操作メソッド Note: @see rogw.tranp.compatible.cpp.object"""
		ToAddrId = 'to_addr_id'
		ToAddrHex = 'to_addr_hex'
		On = 'on'
		Emtpy = 'empty'
		New = 'new'
		CopyProxy = 'copy_proxy'

	class Casts(Enum):
		"""型変換メソッド Note: @see rogw.tranp.compatible.cpp.object"""
		Raw = 'raw'
		Ref = 'ref'
		Addr = 'addr'
		Const = 'const'

		@classmethod
		def in_value(cls, key: str) -> bool:
			"""型変換メソッド名が存在するか判定

			Args:
				key: キー
			Returns:
				True = 存在
			"""
			for value in cls:
				if value.value == key:
					return True

			return False

		@classmethod
		def values(cls) -> Iterator[str]:
			"""全ての型変換メソッド名を取得

			Returns:
				型変換メソッドのイテレーター
			"""
			for value in cls:
				yield value.value

	RawKeys: ClassVar[list[str]] = [cpp.CRaw.__name__, cpp.CRef.__name__, cpp.CRawConst.__name__, cpp.CRefConst.__name__]
	RawRawKeys: ClassVar[list[str]] = [cpp.CRaw.__name__, cpp.CRawConst.__name__]
	RawRefKeys: ClassVar[list[str]] = [cpp.CRef.__name__, cpp.CRefConst.__name__]
	AddrKeys: ClassVar[list[str]] = [cpp.CP.__name__, cpp.CSP.__name__, cpp.CPConst.__name__, cpp.CSPConst.__name__]
	AddrPKeys: ClassVar[list[str]] = [cpp.CP.__name__, cpp.CPConst.__name__]
	AddrSPKeys: ClassVar[list[str]] = [cpp.CSP.__name__, cpp.CSPConst.__name__]
	ConstKeys: ClassVar[list[str]] = [cpp.CPConst.__name__, cpp.CSPConst.__name__, cpp.CRefConst.__name__, cpp.CRawConst.__name__]	
	Keys: ClassVar[list[str]] = [cpp.CP.__name__, cpp.CSP.__name__, cpp.CRef.__name__, cpp.CRaw.__name__, cpp.CPConst.__name__, cpp.CSPConst.__name__, cpp.CRefConst.__name__, cpp.CRawConst.__name__]

	KeyToOperator: ClassVar[dict[str, RelayOperators]] = {
		cpp.CP.__name__: RelayOperators.Address,
		cpp.CSP.__name__: RelayOperators.Address,
		cpp.CRef.__name__: RelayOperators.Raw,
		cpp.CPConst.__name__: RelayOperators.Address,
		cpp.CSPConst.__name__: RelayOperators.Address,
		cpp.CRefConst.__name__: RelayOperators.Raw,
		cpp.CRawConst.__name__: RelayOperators.Raw,
		cpp.CRaw.__name__: RelayOperators.Raw,
	}
	CastToMove: ClassVar[dict[str, Moves]] = {
		f'{cpp.CP.__name__}.{Casts.Raw.value}': Moves.ToActual,
		f'{cpp.CP.__name__}.{Casts.Ref.value}': Moves.ToActual,
		f'{cpp.CP.__name__}.{Casts.Const.value}': Moves.Copy,
		f'{cpp.CSP.__name__}.{Casts.Raw.value}': Moves.ToActual,
		f'{cpp.CSP.__name__}.{Casts.Ref.value}': Moves.ToActual,
		f'{cpp.CSP.__name__}.{Casts.Addr.value}': Moves.UnpackSp,
		f'{cpp.CSP.__name__}.{Casts.Const.value}': Moves.Copy,
		f'{cpp.CRef.__name__}.{Casts.Raw.value}': Moves.Copy,
		f'{cpp.CRef.__name__}.{Casts.Addr.value}': Moves.ToAddress,
		f'{cpp.CRef.__name__}.{Casts.Const.value}': Moves.Copy,
		f'{cpp.CPConst.__name__}.{Casts.Raw.value}': Moves.ToActual,
		f'{cpp.CPConst.__name__}.{Casts.Ref.value}': Moves.ToActual,
		f'{cpp.CSPConst.__name__}.{Casts.Raw.value}': Moves.ToActual,
		f'{cpp.CSPConst.__name__}.{Casts.Ref.value}': Moves.ToActual,
		f'{cpp.CSPConst.__name__}.{Casts.Addr.value}': Moves.UnpackSp,
		f'{cpp.CRefConst.__name__}.{Casts.Raw.value}': Moves.Copy,
		f'{cpp.CRefConst.__name__}.{Casts.Addr.value}': Moves.ToAddress,
		f'{cpp.CRawConst.__name__}.{Casts.Raw.value}': Moves.Copy,
		f'{cpp.CRawConst.__name__}.{Casts.Ref.value}': Moves.Copy,
		f'{cpp.CRawConst.__name__}.{Casts.Addr.value}': Moves.ToAddress,
	}

	def __init__(self, var_name_to_key: dict[str, str]) -> None:
		"""インスタンスを生成

		Args:
			var_name_to_key: 変数型名とC++変数型のキーマップ
		"""
		self._var_name_to_key = {
			cpp.CP.__name__: cpp.CP.__name__,
			cpp.CSP.__name__: cpp.CSP.__name__,
			cpp.CRef.__name__: cpp.CRef.__name__,
			cpp.CRaw.__name__: cpp.CRaw.__name__,
			cpp.CPConst.__name__: cpp.CPConst.__name__,
			cpp.CSPConst.__name__: cpp.CSPConst.__name__,
			cpp.CRefConst.__name__: cpp.CRefConst.__name__,
			cpp.CRawConst.__name__: cpp.CRawConst.__name__,
		}
		for symbol, key in var_name_to_key.items():
			self._var_name_to_key[symbol] = key

	def is_entity(self, var_name: str) -> bool:
		"""実体か判定(Constは除外)

		Args:
			var_name: 変数型名
		Returns:
			True = 実体
		"""
		return self._var_name_to_key[var_name] == cpp.CRaw.__name__

	def is_raw(self, var_name: str) -> bool:
		"""実体か判定(Constを含む)

		Args:
			var_name: 変数型名
		Returns:
			True = 実体/参照
		"""
		return self._var_name_to_key[var_name] in CVars.RawKeys

	def is_addr(self, var_name: str) -> bool:
		"""アドレスか判定(Constを含む)

		Args:
			var_name: 変数型名
		Returns:
			True = ポインター/スマートポインター
		"""
		return self._var_name_to_key[var_name] in CVars.AddrKeys

	def is_raw_raw(self, var_name: str) -> bool:
		"""実体か判定(Constを含む)

		Args:
			var_name: 変数型名
		Returns:
			True = 実体
		"""
		return self._var_name_to_key[var_name] in CVars.RawRawKeys

	def is_raw_ref(self, var_name: str) -> bool:
		"""参照か判定(Constを含む)

		Args:
			var_name: 変数型名
		Returns:
			True = 参照
		"""
		return self._var_name_to_key[var_name] in CVars.RawRefKeys

	def is_addr_p(self, var_name: str) -> bool:
		"""ポインターか判定(Constを含む)

		Args:
			var_name: 変数型名
		Returns:
			True = ポインター
		"""
		return self._var_name_to_key[var_name] in CVars.AddrPKeys

	def is_addr_sp(self, var_name: str) -> bool:
		"""スマートポインターか判定(Constを含む)

		Args:
			var_name: 変数型名
		Returns:
			True = スマートポインター
		"""
		return self._var_name_to_key[var_name] in CVars.AddrSPKeys

	def is_const(self, var_name: str) -> bool:
		"""Constか判定

		Args:
			var_name: 変数型名
		Returns:
			True = Const
		"""
		return self._var_name_to_key[var_name] in CVars.ConstKeys

	def var_names(self) -> Iterator[str]:
		"""全ての変数型名を取得

		Returns:
			変数型名のイテレーター
		"""
		for key in self._var_name_to_key.keys():
			yield key

	def var_name_from(self, symbol: IReflection) -> str:
		"""シンボルから変数型名を取得

		Args:
			symbol: シンボル
		Returns:
			変数型名
		Note:
			nullはポインターとして扱う
		"""
		if symbol.types.domain_name in self.var_names():
			return symbol.types.domain_name
		elif symbol.impl(refs.Object).type_is(None):
			return cpp.CP.__name__
		else:
			return cpp.CRaw.__name__

	def to_operator(self, var_name: str) -> RelayOperators:
		"""変数型名に応じたリレー演算子に変換

		Args:
			var_name: 変数型名
		Returns:
			リレー演算子
		"""
		key = self._var_name_to_key[var_name]
		return CVars.KeyToOperator[key]

	def to_move(self, var_name: str, cast_key: str) -> Moves:
		"""変数型名の各メソッドに応じた移動操作の種別に変換

		Args:
			var_name: 変数型名
			cast_key: 型変換メソッド名
		Returns:
			移動操作の種別
		"""
		key = self._var_name_to_key[var_name]
		return CVars.CastToMove.get(f'{key}.{cast_key}', CVars.Moves.Deny)

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

	# 	if cls.is_addr_sp(accept_key) and cls.is_raw(value_key) and value_on_new:
	# 		return cls.Moves.MakeSp
	# 	elif cls.is_addr_p(accept_key) and cls.is_raw(value_key) and value_on_new:
	# 		return cls.Moves.New
	# 	elif cls.is_addr_p(accept_key) and cls.is_raw(value_key):
	# 		return cls.Moves.ToAddress
	# 	elif cls.is_raw(accept_key) and cls.is_addr(value_key):
	# 		return cls.Moves.ToActual
	# 	elif cls.is_addr_p(accept_key) and cls.is_addr_sp(value_key):
	# 		return cls.Moves.UnpackSp
	# 	elif cls.is_addr_p(accept_key) and cls.is_addr_p(value_key):
	# 		return cls.Moves.Copy
	# 	elif cls.is_addr_sp(accept_key) and cls.is_addr_sp(value_key):
	# 		return cls.Moves.Copy
	# 	elif cls.is_raw(accept_key) and cls.is_raw(value_key):
	# 		return cls.Moves.Copy
	# 	else:
	# 		return cls.Moves.Deny
