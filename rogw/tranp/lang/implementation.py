from typing import Callable, ParamSpec, TypeVar

T = TypeVar('T')
P = ParamSpec('P')


def override(wrapper_func: Callable[P, T]) -> Callable[P, T]:
	"""メソッドのoverrideアノテーション。特に何も変更せずそのまま元のメソッドを返す

	Args:
		wrapper_func (Callable[..., T]): 対象のメソッド
	Returns:
		Callable[...,  T]: 対象のメソッドを返却
	"""
	return wrapper_func


def implements(wrapper_func: Callable[P, T]) -> Callable[P, T]:
	"""メソッドのimplementsアノテーション。特に何も変更せずそのまま元のメソッドを返す

	Args:
		wrapper_func (Callable[..., T]): 対象のメソッド
	Returns:
		Callable[...,  T]: 対象のメソッドを返却
	"""
	return wrapper_func


def deprecated(wrapper_func: Callable[P, T]) -> Callable[P, T]:
	"""メソッドのdeprecatedアノテーション。特に何も変更せずそのまま元のメソッドを返す

	Args:
		wrapper_func (Callable[..., T]): 対象のメソッド
	Returns:
		Callable[...,  T]: 対象のメソッドを返却
	"""
	return wrapper_func


def injectable(wrapper_func: Callable[P, T]) -> Callable[P, T]:
	"""メソッドのinjectableアノテーション。特に何も変更せずそのまま元のメソッドを返す

	Args:
		wrapper_func (Callable[..., T]): 対象のメソッド
	Returns:
		Callable[...,  T]: 対象のメソッドを返却
	"""
	return wrapper_func
