from collections.abc import Callable
from typing import Any, TypeVar, cast

T = TypeVar('T')


class Defer:
	"""遅延評価プロクシー

	Note:
		### 留意事項
		* 不変性を持つスカラー型(int/str等)の置き換えは言語の仕様上不可能なため非対応
		* 特殊メソッドは最低限のメソッドのみ対応 ※必要以上に定義すると想定外の呼び出しが発生することがあるため
		* 上記の制限から一般的なユーザー定義型に対して用いることを想定
	"""

	@classmethod
	def new(cls, factory: Callable[[], T]) -> T:
		"""インスタンスを生成

		Args:
			factory: 実体を生成するファクトリー
		Returns:
			T: 擬態インスタンス
		"""
		return cast(T, cls(factory))

	@classmethod
	def resolve(cls, instance: T) -> T:
		"""インスタンスから実体を解決

		Args:
			instance: Deferのインスタンス
		Returns:
			T: 実体のインスタンス
		Raise:
			ValueError: Defer以外のインスタンスを指定
		"""
		if isinstance(instance, Defer):
			return getattr(instance, '__deferred_entity__')

		raise ValueError(f'Unresolve deferred entity. actual: {instance.__class__}')

	def __init__(self, factory: Callable[[], T]) -> None:
		"""インスタンスを生成

		Args:
			factory: 実体を生成するファクトリー
		"""
		super().__setattr__('_factory', factory)
		super().__setattr__('_entity', None)

	def __getattribute__(self, name: str) -> Any:
		"""指定の名前の属性を取得

		Args:
			name: 名前
		Returns:
			Any: 値
		"""
		entity = super().__getattribute__('_entity')
		if not entity:
			factory: Callable[[], Any] = super().__getattribute__('_factory')
			entity = factory()
			super().__setattr__('_entity', entity)

		if name == '__deferred_entity__':
			return entity

		return getattr(entity, name)

	def __repr__(self) -> str:
		"""Returns: str: シリアライズ表現"""
		entity = Defer.resolve(self)
		return f'<{Defer.__name__}[{entity.__class__.__name__}]: at {hex(id(self)).upper()} with {entity}>'

	def __str__(self) -> str:
		"""Returns: str: 文字列表現"""
		return getattr(Defer.resolve(self), '__str__')()

	def __hash__(self) -> int:
		"""Returns: int: ハッシュ値"""
		return getattr(Defer.resolve(self), '__hash__')()

	def __eq__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 一致"""
		return getattr(Defer.resolve(self), '__eq__')(other)

	def __ne__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 不一致"""
		return getattr(Defer.resolve(self), '__ne__')(other)
