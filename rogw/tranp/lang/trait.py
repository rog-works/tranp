from collections.abc import Callable
from types import FunctionType
from typing import Any, Generic, Protocol, TypeVar

from rogw.tranp.errors import LogicError
from rogw.tranp.lang.annotation import injectable

T = TypeVar('T')


class Trait:
	"""インターフェイス拡張トレイト(基底)"""

	@injectable
	def __init__(self, *injects: Any) -> None:
		"""インスタンスを生成

		Args:
			*injects (Any): 任意の注入引数 @inject
		"""
		...

	@property
	def implements(self) -> type[Any]:
		"""実装インターフェイスを取得

		Returns:
			type[Any]: クラス
		Note:
			* 以下の様にTraitの実装クラスが宣言されていると見做し、MROの末尾(-2)を実装インターフェイスとして取得する
			* `class TraitImpl(Trait, ITrait): ...` -> MRO(TraitImpl, Trait, ITrait, object) -> ITrait
		"""
		return self.__class__.mro()[-2]

	@property
	def impl_methods(self) -> list[str]:
		"""実装メソッド名リスト

		Returns:
			list[str]: メソッド名リスト
		"""
		return [key for key, value in self.implements.__dict__.items() if not key.startswith('_') and isinstance(value, FunctionType)]


class TraitProvider(Protocol):
	"""トレイトプロバイダープロトコル"""

	def __call__(self) -> list[Trait]:
		"""トレイトリストを取得

		Returns:
			list[Trait]: トレイトリスト
		"""
		...


class Traits(Generic[T]):
	"""トレイトマネージャー"""

	def __init__(self, provider: TraitProvider) -> None:
		"""インスタンスを生成

		Args:
			provider: トレイトプロバイダー
		"""
		self.__provider = provider
		self.__interfaces: list[type[Any]] = []
		self.__method_on_trait: dict[str, Trait] = {}

	def __ensure_traits(self) -> None:
		"""トレイトをインスタンス化

		Note:
			インスタンス生成時にDIを利用するため、トレイト参照時まで生成を遅らせる
		"""
		traits = self.__provider()
		method_on_trait: dict[str, Trait] = {}
		for trait in traits:
			method_on_trait = {**method_on_trait, **{name: trait for name in trait.impl_methods}}

		self.__interfaces = [trait.implements for trait in traits]
		self.__method_on_trait = method_on_trait

	def implements(self, expect: type[T]) -> bool:
		"""指定のクラスが所有するインターフェイスが実装されているか判定

		Args:
			expect: 期待するインターフェイス
		Returns:
			bool: True = 実装
		Note:
			* 以下の様にインターフェイスが宣言されていると見做し、MROの中間層(2 ~ -1)を実装インターフェイスとして取得する
			* `class IAggregation(IMain, ITrait1, ITrait2): ...` -> MRO(IAggregation, IMain, ITrait1, ITrait2, object) -> (ITrait1, ITrait2)
		"""
		if len(self.__interfaces) == 0:
			self.__ensure_traits()

		requirements = expect.mro()[2:-1]
		for required in requirements:
			if required not in self.__interfaces:
				return False

		return True

	def get(self, name: str, instance: T) -> Callable[..., Any]:
		"""トレイトのメソッドを取得

		Args:
			name: メソッド名
			instance: 拡張対象のインスタンス
		Returns:
			Callable[..., Any]: メソッドアダプター
		Raises:
			LogicError: トレイトのメソッドが未実装
		"""
		if name not in self.__method_on_trait:
			raise LogicError(f'Method not defined. class: {type(instance)}, name: {name}')

		trait = self.__method_on_trait[name]
		return lambda *args: getattr(trait, name)(*args, instance=instance)
