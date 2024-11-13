from collections.abc import Callable
from typing import Any, Generic, TypeVar, cast

from rogw.tranp.lang.annotation import deprecated

T = TypeVar('T')


@deprecated
class Defer(Generic[T]):
	"""遅延評価プロクシー

	Note:
		### 非推奨に関して
		* XXX スカラー型の完全な置き換えが出来ない
	"""

	@classmethod
	def new(cls, factory: Callable[[], T]) -> T:
		"""インスタンスを生成

		Args:
			factory (Callable[[], T]): 実体を生成するファクトリー
		Returns:
			T: 擬態インスタンス
		"""
		return cast(T, cls(factory))

	@classmethod
	def resolve(cls, instance: T) -> T:
		"""インスタンスから実体を解決

		Args:
			instance (T): Deferのインスタンス
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
			factory (Callable[[], Any]): 実体を生成するファクトリー
		"""
		super().__setattr__('_factory', factory)
		super().__setattr__('_entity', None)

	def __getattribute__(self, name: str) -> Any:
		"""指定の名前の属性を取得

		Args:
			name (str): 名前
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

	def __len__(self) -> int:
		"""Returns: int: 長さ"""
		return getattr(Defer.resolve(self), '__len__')()

	# ----- 2項演算 -----

	def __eq__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 一致"""
		return getattr(Defer.resolve(self), '__eq__')(other)

	def __ne__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 不一致"""
		return getattr(Defer.resolve(self), '__ne__')(other)

	def __lt__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 未満"""
		return getattr(Defer.resolve(self), '__lt__')(other)

	def __gt__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 大きい"""
		return getattr(Defer.resolve(self), '__gt__')(other)

	def __le__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 以下"""
		return getattr(Defer.resolve(self), '__le__')(other)

	def __ge__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 以上"""
		return getattr(Defer.resolve(self), '__ge__')(other)

	# ----- 算術演算 -----

	def __add__(self, value: Any) -> Any:
		"""加算 Args: value (Any): 値 Returns: Any: 値"""
		return getattr(Defer.resolve(self), '__add__')(value)

	# ----- 配列 -----

	def __getitem__(self, slices: Any) -> Any:
		"""配列参照 Args: slices (Any): 添え字, Returns: Any: 値"""
		return getattr(Defer.resolve(self), '__getitem__')(slices)

	def __setitem__(self, key: Any, value: Any) -> None:
		"""配列更新 Args: key (Any): キー, value (Any): 値"""
		getattr(Defer.resolve(self), '__setitem__')(key, value)
