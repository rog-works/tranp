from typing import Any

from rogw.tranp.compatible.cpp.cvar import CP, CPConst


def const_cast[T](entity_type: type[CP[T]], value_at: CPConst[T]) -> CP[T]:
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


def immutable_const_cast[T](value_type: type[T], value: T) -> T:
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
