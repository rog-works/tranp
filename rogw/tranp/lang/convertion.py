from typing import Any, TypeVar

T = TypeVar('T')


def safe_cast(value: T | None) -> T:
	"""安全にNullable型から実体型にキャスト

	Args:
		value: 値
	Returns:
		T: 値
	Raises:
		ValueError: 値がnull
	"""
	if value is None:
		raise ValueError('Not allowed convertion. value is null')

	return value

def as_a(expect: type[T], value: Any) -> T:
	"""安全に期待の型へキャスト

	Args:
		expect: 期待の型
		value: 値
	Returns:
		T: 値
	Raises:
		ValueError: 値の型と期待の型に関連が無い
	"""
	if not isinstance(value, expect):
		raise ValueError(f'Not allowed convertion. value: {type(value)}, expect: {expect}')

	return value
