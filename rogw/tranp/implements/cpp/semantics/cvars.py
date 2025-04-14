from enum import Enum
from typing import ClassVar

import rogw.tranp.compatible.cpp.object as cpp
from rogw.tranp.lang.annotation import deprecated
from rogw.tranp.semantics.reflection.base import IReflection
import rogw.tranp.semantics.reflection.definition as refs


class CVars:
	"""C++型変数の操作ユーティリティー

	Attributes:
		relay_key: リレー代替メソッドの名前
		empty_key: 空のスマートポインター生成代替メソッドの名前
		allocator_key: メモリ生成メソッドの名前
		copy_key: 代入コピー代替メソッドの名前
		exchanger_keys: 属性変換メソッドの名前
	"""

	hex_key: ClassVar[str] = 'hex'
	relay_key: ClassVar[str] = 'on'
	empty_key: ClassVar[str] = 'empty'
	allocator_key: ClassVar[str] = 'new'
	copy_key: ClassVar[str] = 'copy_proxy'
	exchanger_keys: ClassVar[list[str]] = ['raw', 'ref', 'addr', 'const']

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

	@classmethod
	def is_entity(cls, key: str) -> bool:
		"""実体か判定(Constは除外)

		Args:
			key: C++変数型の種別キー
		Returns:
			True = 実体
		"""
		return key == cpp.CRaw.__name__

	@classmethod
	def is_raw(cls, key: str) -> bool:
		"""実体か判定(Constを含む)

		Args:
			key: C++変数型の種別キー
		Returns:
			True = 実体/参照
		"""
		return key in [cpp.CRaw.__name__, cpp.CRef.__name__, cpp.CRawConst.__name__, cpp.CRefConst.__name__]

	@classmethod
	def is_addr(cls, key: str) -> bool:
		"""アドレスか判定(Constを含む)

		Args:
			key: C++変数型の種別キー
		Returns:
			True = ポインター/スマートポインター
		"""
		return key in [cpp.CP.__name__, cpp.CSP.__name__, cpp.CPConst.__name__, cpp.CSPConst.__name__]

	@classmethod
	def is_raw_raw(cls, key: str) -> bool:
		"""実体か判定(Constを含む)

		Args:
			key: C++変数型の種別キー
		Returns:
			True = 実体
		"""
		return key in [cpp.CRaw.__name__, cpp.CRawConst.__name__]

	@classmethod
	def is_raw_ref(cls, key: str) -> bool:
		"""参照か判定(Constを含む)

		Args:
			key: C++変数型の種別キー
		Returns:
			True = 参照
		"""
		return key in [cpp.CRef.__name__, cpp.CRefConst.__name__]

	@classmethod
	def is_addr_p(cls, key: str) -> bool:
		"""ポインターか判定(Constを含む)

		Args:
			key: C++変数型の種別キー
		Returns:
			True = ポインター
		"""
		return key in [cpp.CP.__name__, cpp.CPConst.__name__]

	@classmethod
	def is_addr_sp(cls, key: str) -> bool:
		"""スマートポインターか判定(Constを含む)

		Args:
			key: C++変数型の種別キー
		Returns:
			True = スマートポインター
		"""
		return key in [cpp.CSP.__name__, cpp.CSPConst.__name__]

	@classmethod
	def is_const(cls, key: str) -> bool:
		"""Constか判定

		Args:
			key: C++変数型の種別キー
		Returns:
			True = Const
		"""
		return key in [cpp.CPConst.__name__, cpp.CSPConst.__name__, cpp.CRefConst.__name__, cpp.CRawConst.__name__]

	@classmethod
	def keys(cls) -> list[str]:
		"""C++変数型の種別キー一覧を生成

		Returns:
			種別キー一覧
		"""
		return [cvar.__name__ for cvar in [cpp.CP, cpp.CSP, cpp.CRef, cpp.CPConst, cpp.CSPConst, cpp.CRefConst, cpp.CRawConst, cpp.CRaw]]

	@classmethod
	def key_from(cls, symbol: IReflection) -> str:
		"""シンボルからC++変数型の種別キーを取得

		Args:
			symbol: シンボル
		Returns:
			種別キー
		Note:
			nullはポインターとして扱う
		"""
		if symbol.types.domain_name in cls.keys():
			return symbol.types.domain_name
		elif symbol.impl(refs.Object).type_is(None):
			return cpp.CP.__name__
		else:
			return cpp.CRaw.__name__

	@classmethod
	def to_operator(cls, key: str) -> RelayOperators:
		"""C++変数型に応じたリレー演算子に変換

		Args:
			key: C++変数型の種別キー
		Returns:
			リレー演算子
		"""
		accessors = {
			cpp.CP.__name__: cls.RelayOperators.Address,
			cpp.CSP.__name__: cls.RelayOperators.Address,
			cpp.CRef.__name__: cls.RelayOperators.Raw,
			cpp.CPConst.__name__: cls.RelayOperators.Address,
			cpp.CSPConst.__name__: cls.RelayOperators.Address,
			cpp.CRefConst.__name__: cls.RelayOperators.Raw,
			cpp.CRawConst.__name__: cls.RelayOperators.Raw,
			cpp.CRaw.__name__: cls.RelayOperators.Raw,
		}
		return accessors[key]

	@classmethod
	def to_move(cls, key: str, method: str) -> Moves:
		"""C++変数型の各メソッドに応じた移動操作の種別に変換

		Args:
			key: C++変数型の種別キー
			method: メソッド名
		Returns:
			移動操作の種別
		"""
		moves = {
			f'{cpp.CP.__name__}.raw': CVars.Moves.ToActual,
			f'{cpp.CP.__name__}.ref': CVars.Moves.ToActual,
			f'{cpp.CP.__name__}.const': CVars.Moves.Copy,
			f'{cpp.CSP.__name__}.raw': CVars.Moves.ToActual,
			f'{cpp.CSP.__name__}.ref': CVars.Moves.ToActual,
			f'{cpp.CSP.__name__}.addr': CVars.Moves.UnpackSp,
			f'{cpp.CSP.__name__}.const': CVars.Moves.Copy,
			f'{cpp.CRef.__name__}.raw': CVars.Moves.Copy,
			f'{cpp.CRef.__name__}.addr': CVars.Moves.ToAddress,
			f'{cpp.CRef.__name__}.const': CVars.Moves.Copy,
			f'{cpp.CPConst.__name__}.raw': CVars.Moves.ToActual,
			f'{cpp.CPConst.__name__}.ref': CVars.Moves.ToActual,
			f'{cpp.CSPConst.__name__}.raw': CVars.Moves.ToActual,
			f'{cpp.CSPConst.__name__}.ref': CVars.Moves.ToActual,
			f'{cpp.CSPConst.__name__}.addr': CVars.Moves.UnpackSp,
			f'{cpp.CRefConst.__name__}.raw': CVars.Moves.Copy,
			f'{cpp.CRefConst.__name__}.addr': CVars.Moves.ToAddress,
			f'{cpp.CRawConst.__name__}.raw': CVars.Moves.Copy,
			f'{cpp.CRawConst.__name__}.ref': CVars.Moves.Copy,
			f'{cpp.CRawConst.__name__}.addr': CVars.Moves.ToAddress,
		}
		move_key = f'{key}.{method}'
		if move_key in moves:
			return moves[move_key]

		return CVars.Moves.Deny

	@classmethod
	@deprecated
	def analyze_move(cls, accept: IReflection, value: IReflection, value_on_new: bool, declared: bool) -> Moves:
		"""移動操作を解析

		Args:
			accept: 受け入れ側
			value: 入力側
			value_on_new: True = インスタンス生成
			declared: True = 変数宣言時
		Returns:
			移動操作の種別
		Note:
			@deprecated 未使用のため削除を検討
		"""
		accept_key = cls.key_from(accept)
		value_key = cls.key_from(value)
		return cls.move_by(accept_key, value_key, value_on_new, declared)

	@classmethod
	@deprecated
	def move_by(cls, accept_key: str, value_key: str, value_on_new: bool, declared: bool) -> Moves:
		"""移動操作を解析

		Args:
			accept_key: 受け入れ側
			value_key: 入力側
			value_on_new: True = インスタンス生成
			declared: True = 変数宣言時
		Returns:
			移動操作の種別
		Note:
			@deprecated 未使用のため削除を検討
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
