from enum import Enum
from typing import ClassVar

import rogw.tranp.compatible.cpp.object as cpp
from rogw.tranp.lang.implementation import deprecated
from rogw.tranp.semantics.reflection import IReflection
from rogw.tranp.semantics.reflections import Reflections


class CVars:
	"""C++変数型の操作ユーティリティー

	Attributes:
		relay_key (str): リレー代替メソッドの名前
		allocator_key (str): メモリ生成メソッドの名前
		exchanger_key (str): 属性変換メソッドの名前
	"""

	relay_key: ClassVar[str] = 'on'
	allocator_key: ClassVar[str] = 'new'
	exchanger_keys: ClassVar[list[str]] = ['raw', 'ref', 'addr']

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
	@deprecated
	def analyze_move(cls, reflections: Reflections, accept: IReflection, value: IReflection, value_on_new: bool, declared: bool) -> Moves:
		"""移動操作を解析

		Args:
			reflections (Reflections): シンボルリゾルバー
			accept (IReflection): 受け入れ側
			value (IReflection): 入力側
			value_on_new (bool): True = インスタンス生成
			declared (bool): True = 変数宣言時
		Returns:
			Moves: 移動操作の種別
		Note:
			@deprecated 未使用のため削除を検討
		"""
		accept_key = cls.key_from(reflections, accept)
		value_key = cls.key_from(reflections, value)
		return cls.move_by(accept_key, value_key, value_on_new, declared)

	@classmethod
	@deprecated
	def move_by(cls, accept_key: str, value_key: str, value_on_new: bool, declared: bool) -> Moves:
		"""移動操作を解析

		Args:
			accept_key (str): 受け入れ側
			value_key (str): 入力側
			value_on_new (bool): True = インスタンス生成
			declared (bool): True = 変数宣言時
		Returns:
			Moves: 移動操作の種別
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
	def key_from(cls, reflections: Reflections, symbol: IReflection) -> str:
		"""シンボルからC++変数型の種別キーを取得

		Args:
			reflections (Reflections): シンボルリゾルバー
			symbol (IReflection): シンボル
		Returns:
			str: 種別キー
		Note:
			nullはポインターとして扱う
		"""
		if reflections.is_a(symbol, None):
			return cpp.CP.__name__
		elif symbol.types.domain_name in cls.keys():
			return symbol.types.domain_name
		else:
			return cpp.CRaw.__name__

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

	@classmethod
	def to_move(cls, key: str, method: str) -> Moves:
		moves = {
			'CP.raw': CVars.Moves.ToActual,
			'CP.ref': CVars.Moves.ToActual,
			'CSP.raw': CVars.Moves.ToActual,
			'CSP.ref': CVars.Moves.ToActual,
			'CSP.addr': CVars.Moves.UnpackSp,
			'CRef.raw': CVars.Moves.Copy,
			'CRef.addr': CVars.Moves.ToAddress,
		}
		move_key = f'{key}.{method}'
		if move_key in moves:
			return moves[move_key]

		return CVars.Moves.Deny
