from typing import TypeVar

T = TypeVar('T')


def override(wrapped: T) -> T:
	"""オーバーライドを表すアノテーション。何も変更せずラップ対象を返す

	Args:
		wrapped (T): ラップ対象
	Returns:
		T: ラップ対象
	"""
	return wrapped


def implements(wrapped: T) -> T:
	"""インターフェイスの実装を表すアノテーション。何も変更せずラップ対象を返す

	Args:
		wrapped (T): ラップ対象
	Returns:
		T: ラップ対象
	"""
	return wrapped


def duck_typed(wrapped: T) -> T:
	"""プロトコルへの準拠を表すアノテーション。何も変更せずラップ対象を返す

	Args:
		wrapped (T): ラップ対象
	Returns:
		T: ラップ対象
	"""
	return wrapped


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
