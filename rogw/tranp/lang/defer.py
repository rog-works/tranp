from typing import Any, Callable, TypeVar, cast

T = TypeVar('T')


class Difer:
	"""遅延評価プロクシー"""

	@classmethod
	def new(cls, factory: Callable[[], T]) -> T:
		"""インスタンスを生成

		Args:
			factory (Callable[T]): 実体を生成するファクトリー
		Returns:
			T: 擬態インスタンス
		"""
		return cast(T, cls(factory))

	def __init__(self, factory: Callable[[], Any]) -> None:
		"""インスタンスを生成

		Args:
			factory (Callable[T]): 実体を生成するファクトリー
		"""
		super().__setattr__('_factory', factory)
		super().__setattr__('_instance', None)

	def __getattribute__(self, name: str) -> Any:
		"""指定の名前の属性を取得

		Args:
			name (str): 名前
		Returns:
			Any: 値
		"""
		instance = super().__getattribute__('_instance')
		if not instance:
			factory: Callable[[], Any] = super().__getattribute__('_factory')
			instance = factory()
			super().__setattr__('_instance', instance)

		return getattr(instance, name)
