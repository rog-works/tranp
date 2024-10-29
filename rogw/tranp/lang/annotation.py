from typing import Any, Callable, TypeVar

T = TypeVar('T')


def implements(wrapped: T) -> T:
	"""インターフェイスの実装を表すアノテーション。何も変更せずラップ対象を返す

	Args:
		wrapped (T): ラップ対象
	Returns:
		T: ラップ対象
	"""
	return wrapped


def duck_typed(protocol: Any) -> Callable[[T], T]:
	"""プロトコルへの準拠を表すアノテーション。何も変更せずラップ対象を返す

	Args:
		protocol (Any): プロトコル
	Returns:
		Callable: デコレーター
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator


def deprecated(wrapped: T) -> T:
	"""非推奨のアノテーション。何も変更せずラップ対象を返す

	Args:
		wrapped (T): ラップ対象
	Returns:
		T: ラップ対象
	"""
	return wrapped


def injectable(wrapped: T) -> T:
	"""DIよりインジェクションが可能であることを表すアノテーション。何も変更せずラップ対象を返す

	Args:
		wrapped (T): ラップ対象
	Returns:
		T: ラップ対象
	"""
	return wrapped
