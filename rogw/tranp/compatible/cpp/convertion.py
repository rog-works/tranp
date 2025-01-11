from typing import Any, TypeVar

from rogw.tranp.compatible.cpp.classes import void
from rogw.tranp.compatible.cpp.object import CP, CPConst

T = TypeVar('T')


def cast_addr(to_origin: type[T], value_at: CP[Any]) -> CP[T]:
	"""アドレス型を安全に変換。変換先が不正な場合は例外を出力

	Args:
		to_origin: 変換先の実体のクラス
		value_at: 対象のアドレス変数
	Returns:
		変換後のアドレス変数
	Raises:
		ValueError: 不正な変換先を指定
	Note:
		```
		### 変換条件
		* 変換先がvoid
		* 変換先と関連のある型(基底/派生)
		```
	"""
	if to_origin == void:
		return value_at

	if isinstance(value_at.raw, to_origin) or issubclass(to_origin, type(value_at.raw)):
		return value_at

	raise ValueError(f'Not allowed convertion. from: {type(value_at.raw)}, to: {to_origin}')


def const_cast(entity_type: type[CP[T]], value_at: CPConst[T]) -> CP[T]:
	"""アドレス型のconstを解除

	Args:
		entity_type: アドレス型
		value_at: 対象のアドレス変数
	Returns:
		変換後のアドレス変数
	Note:
		XXX なるべく使用しないことを推奨
	"""
	return CP(value_at.raw)


def immutable_const_cast(value_type: type[T], value: T) -> T:
	"""暗黙的不変型のconstを解除

	Args:
		value_type: 値の型
		value: 値 (str/list/dict/lambdaを想定)
	Returns:
		値
	Note:
		```
		XXX なるべく使用しないことを推奨
		期待する型: `const std::string& s`
		```
	"""
	return value


def sizeof(origin: type[Any]) -> int:
	"""クラスのバイナリサイズを取得

	Args:
		origin: クラス
	Returns:
		サイズ
	Note:
		XXX Pythonでは再現が困難なため1を返す
	"""
	return 1
