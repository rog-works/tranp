from typing import TypeVar


T = TypeVar('T')

def safe_cast(value: T | None) -> T:
	"""安全にNullable型から実体型にキャスト

	Args:
		value (T | None): 値
	Returns:
		T: 値
	"""
	if value is None:
		raise ValueError('value is null')

	return value
