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

	def __repr__(self) -> str:
		"""Returns: str: シリアライズ表現"""
		instance = super().__getattribute__('_instance')
		return f'<Difer[{instance.__class__.__name__}]: at {hex(id(self)).upper()} with {instance}>'

	def __str__(self) -> str:
		"""Returns: str: 文字列表現"""
		return getattr(super().__getattribute__('_instance'), '__str__')()

	def __hash__(self) -> int:
		"""Returns: int: ハッシュ値"""
		return getattr(super().__getattribute__('_instance'), '__hash__')()

	def __len__(self) -> int:
		"""Returns: int: 長さ"""
		return getattr(super().__getattribute__('_instance'), '__len__')()

	# ----- 2項演算 -----

	def __eq__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 一致"""
		return getattr(super().__getattribute__('_instance'), '__eq__')(other)

	def __ne__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 不一致"""
		return getattr(super().__getattribute__('_instance'), '__ne__')(other)

	def __lt__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 未満"""
		return getattr(super().__getattribute__('_instance'), '__lt__')(other)

	def __gt__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 大きい"""
		return getattr(super().__getattribute__('_instance'), '__gt__')(other)

	def __le__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 以下"""
		return getattr(super().__getattribute__('_instance'), '__le__')(other)

	def __ge__(self, other: Any) -> bool:
		"""Args: other (Any): 対象 Returns: bool: True = 以上"""
		return getattr(super().__getattribute__('_instance'), '__ge__')(other)

	# ----- 算術演算 -----

	def __add__(self, value: Any) -> Any:
		"""加算 Args: value (Any): 値 Returns: Any: 値"""
		return getattr(super().__getattribute__('_instance'), '__add__')(value)

	# ----- 配列 -----

	def __getitem__(self, slices: Any) -> Any:
		"""配列参照 Args: slices (Any): 添え字, Returns: Any: 値"""
		return getattr(super().__getattribute__('_instance'), '__getitem__')(slices)

	def __setitem__(self, key: Any, value: Any) -> None:
		"""配列更新 Args: key (Any): キー, value (Any): 値"""
		getattr(super().__getattribute__('_instance'), '__setitem__')(key, value)
