from typing import Any, TypeVar

T = TypeVar('T')


def safe_cast(value: T | None) -> T:
	"""安全にNullable型から実体型にキャスト

	Args:
		value: 値
	Returns:
		値
	Raises:
		AssertionError: 値がnull
	"""
	assert value is not None, 'Not allowed convertion. value is null'
	return value

def as_a(expect: type[T], value: Any) -> T:
	"""安全に期待の型へキャスト

	Args:
		expect: 期待の型
		value: 値
	Returns:
		値
	Raises:
		AssertionError: 値の型と期待の型に関連が無い
	"""
	assert isinstance(value, expect), f'Not allowed convertion. value: {type(value)}, expect: {expect}'
	return value
