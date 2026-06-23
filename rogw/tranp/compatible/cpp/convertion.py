from typing import Any

from rogw.tranp.compatible.cpp.cvar import CRef, CRefConst


def const_cast[T](entity_type: type[T], value: CRefConst[T]) -> CRef[T]:
	"""不変型参照のconstを解除

	Args:
		entity_type: 値の型
		value: 値
	Returns:
		参照
	Note:
		XXX なるべく使用しないことを推奨
	"""
	return CRef(value.raw)


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
