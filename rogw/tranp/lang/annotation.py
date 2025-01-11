from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar('T')


def implements(wrapped: T) -> T:
	"""インターフェイスの実装を表すアノテーション。何も変更せずラップ対象を返す

	Args:
		wrapped: ラップ対象
	Returns:
		ラップ対象
	"""
	return wrapped


def duck_typed(protocol: Any) -> Callable[[T], T]:
	"""プロトコルへの準拠を表すアノテーション。何も変更せずラップ対象を返す

	Args:
		protocol: プロトコル
	Returns:
		デコレーター
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator


def deprecated(wrapped: T) -> T:
	"""非推奨のアノテーション。何も変更せずラップ対象を返す

	Args:
		wrapped: ラップ対象
	Returns:
		ラップ対象
	"""
	return wrapped


def injectable(wrapped: T) -> T:
	"""DIよりインジェクションが可能であることを表すアノテーション。何も変更せずラップ対象を返す

	Args:
		wrapped: ラップ対象
	Returns:
		ラップ対象
	"""
	return wrapped
