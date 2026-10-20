from typing import Annotated

from example.material.me import ME
from example.material.mfs_00_preview import preview_distance


def op_not(value: Annotated[float, preview_distance()]) -> float:
	"""0と1を反転

	Args:
		value: 値 (0 or 1)
	Returns:
		0 or 1
	Note:
		入力値は0 or 1に限定。それ以外は全てエラーとする
	"""
	assert value in [0.0, 1.0]
	return 1.0 - value


def op_ge(value: Annotated[float, preview_distance()], threshold: Annotated[float, 0.0]) -> float:
	"""value >= threshold = 1

	Args:
		value: 値
		threshold: 閾値 (default = 0.0)
	Returns:
		0 or 1
	"""
	return ME.step(threshold, value)


def op_le(value: Annotated[float, preview_distance()], threshold: Annotated[float, 1.0]) -> float:
	"""value <= threshold = 1

	Args:
		value: 値
		threshold: 閾値 (default = 1.0)
	Returns:
		0 or 1
	"""
	return ME.step(value, threshold)


def op_gt(value: Annotated[float, preview_distance()], threshold: Annotated[float, 0.0]) -> float:
	"""value > threshold = 1

	Args:
		value: 値
		threshold: 閾値 (default = 0.0)
	Returns:
		0 or 1
	"""
	return 1.0 - ME.step(value, threshold)


def op_lt(value: Annotated[float, preview_distance()], threshold: Annotated[float, 1.0]) -> float:
	"""value < threshold = 1

	Args:
		value: 値
		threshold: 閾値 (deafult = 1.0)
	Returns:
		0 or 1
	"""
	return 1.0 - ME.step(threshold, value)


def op_in(value: Annotated[float, preview_distance()], minimum: Annotated[float, 0.0], maximum: Annotated[float, 1.0]) -> float:
	"""min <= value <= max

	Args:
		value: 値
		minimum: 下限 (deafult = 0.0)
		maximum: 上限 (deafult = 1.0)
	Returns:
		0 or 1
	"""
	return op_ge(value, minimum) * op_le(value, maximum)


def op_and(value: Annotated[float, preview_distance()], defaults: Annotated[float, 0.0], is_a: Annotated[bool, False], is_b: Annotated[bool, False]) -> float:
	"""AND条件

	Args:
		value: 値
		defaults: デフォルト値
		is_a: 条件A
		is_b: 条件B
	Returns:
		真の値
	"""
	return (value if is_b else defaults) if is_a else defaults


def op_or(value: Annotated[float, preview_distance()], defaults: Annotated[float, 0.0], is_a: Annotated[bool, False], is_b: Annotated[bool, False]) -> float:
	"""OR条件

	Args:
		value: 値
		defaults: デフォルト値
		is_a: 条件A
		is_b: 条件B
	Returns:
		真の値
	"""
	return value if is_a else (value if is_b else defaults)
