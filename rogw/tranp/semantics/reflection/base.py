from abc import ABCMeta, abstractmethod
from types import FunctionType
from typing import Any, Callable, Iterator, Literal, Protocol, Self, TypeVar

from rogw.tranp.lang.annotation import injectable
from rogw.tranp.semantics.errors import SemanticsLogicError
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node

T_Ref = TypeVar('T_Ref', bound='IReflection')


class IReflection(metaclass=ABCMeta):
	"""シンボル

	Attributes:
		types (ClassDef): 型を表すノード
		decl (DeclAll): 定義元のノード
		node (Node): ノード
		origin (IReflection): 型のシンボル
		via (IReflection): スタックシンボル
		context (IReflection| None): コンテキストのシンボル
		attrs (list[IReflection]): 属性シンボルリスト
	Note:
		# contextのユースケース
		* Relay/Indexerのreceiverを設定。on_func_call等で実行時型の補完に使用
	"""

	@property
	@abstractmethod
	def types(self) -> defs.ClassDef:
		"""ClassDef: 型を表すノード"""
		...

	@property
	@abstractmethod
	def decl(self) -> defs.DeclAll:
		"""DeclAll: 定義元のノード"""
		...

	@property
	@abstractmethod
	def node(self) -> Node:
		"""Node: ノード"""
		...

	@property
	@abstractmethod
	def origin(self) -> 'IReflection':
		"""IReflection: 型のシンボル"""
		...

	@property
	@abstractmethod
	def via(self) -> 'IReflection':
		"""IReflection: スタックシンボル"""
		...

	@property
	@abstractmethod
	def context(self) -> 'IReflection':
		"""IReflection: コンテキストを取得 Raises: SemanticsLogicError: コンテキストが無い状態で使用"""
		...

	@property
	@abstractmethod
	def attrs(self) -> list['IReflection']:
		"""list[IReflection]: 属性シンボルリスト"""
		...

	@property
	@abstractmethod
	def _traits(self) -> 'Traits':
		"""Traits: トレイトマネージャー"""
		...

	@abstractmethod
	def declare(self, decl: defs.DeclVars, origin: 'IReflection | None' = None) -> 'IReflection':
		"""定義ノードをスタックし、型のシンボルを移行。型のシンボル省略時はそのまま引き継ぐ

		Args:
			decl (DeclVars): 定義元のノード
			origin (IReflection | None): 型のシンボル (default = None)
		Returns:
			IReflection: リフレクション
		"""
		...

	@abstractmethod
	def stack(self, node: Node | None = None) -> 'IReflection':
		"""ノードをスタック。ノード省略時は自分自身をスタック

		Args:
			node (Node | None): ノード (default = None)
		Returns:
			IReflection: リフレクション
		"""
		...

	@abstractmethod
	def to(self, node: Node, origin: 'IReflection') -> 'IReflection':
		"""ノードをスタックし、型のシンボルを移行

		Args:
			node (Node): ノード
			origin (IReflection): 型のシンボル
		Returns:
			IReflection: リフレクション
		"""
		...

	@property
	@abstractmethod
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		...

	@abstractmethod
	def stacktrace(self) -> Iterator['IReflection']:
		"""スタックシンボルを辿るイテレーターを取得

		Returns:
			Iterator[IReflection]: イテレーター
		"""
		...

	@abstractmethod
	def extends(self: Self, *attrs: 'IReflection') -> Self:
		"""シンボルが保有する型を拡張情報として属性に取り込む

		Args:
			*attrs (IReflection): 属性シンボルリスト
		Returns:
			Self: インスタンス
		Raises:
			SemanticsLogicError: 実体の無いインスタンスに実行 XXX 出力する例外は要件等
			SemanticsLogicError: 拡張済みのインスタンスに再度実行 XXX 出力する例外は要件等
		"""
		...

	@abstractmethod
	def to_temporary(self) -> 'IReflection':
		"""インスタンスをテンプレート用に複製

		Returns:
			IReflection: 複製したインスタンス
		"""
		...

	@abstractmethod
	def add_on(self, key: Literal['origin', 'attrs'], addon: 'Addon') -> None:
		"""アドオンを有効化
		
		Args:
			key (Literal['origin', 'attrs']): キー
			addon (Addon): アドオン
		"""
		...

	@abstractmethod
	def impl(self, expect: type[T_Ref]) -> T_Ref:
		"""期待する型と同じインターフェイスを実装していればキャスト

		Args:
			expect (type[T_Ref]): 期待する型
		Returns:
			T_Ref: インスタンス
		Note:
			SemanticsLogicError: インターフェイスが未実装 XXX 出力する例外は要件等
		"""
		...


class Addon(Protocol):
	"""シンボル拡張アドオンプロトコル"""

	def __call__(self) -> list[IReflection]:
		"""list[IReflection]: シンボルリスト"""
		...


class Addons:
	"""アドオンマネージャー"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self._addons: dict[str, Addon] = {}
		self._cache: dict[str, list[IReflection]] = {}

	@property
	def origin(self) -> IReflection:
		"""IReflection: 型のシンボル"""
		if not self.active('origin'):
			raise SemanticsLogicError('Has no origin')

		if 'origin' not in self._cache:
			self._cache['origin'] = self._addons['origin']()

		return self._cache['origin'][0]

	@property
	def attrs(self) -> list[IReflection]:
		"""list[IReflection]: 属性シンボルリスト"""
		if not self.active('attrs'):
			raise SemanticsLogicError('Has no attrs')

		if 'attrs' not in self._cache:
			self._cache['attrs'] = self._addons['attrs']()

		return self._cache['attrs']

	def active(self, key: Literal['origin', 'attrs']) -> bool:
		"""アドオンが有効か判定

		Args:
			key (Literal['origin', 'attrs']): キー
		Returns:
			bool: True = 有効
		"""
		return key in self._addons

	def activate(self, key: Literal['origin', 'attrs'], addon: Addon) -> None:
		"""アドオンを有効化

		Args:
			key (Literal['origin', 'attrs']): キー
			addon (Addon): アドオン
		"""
		if key in self._cache:
			del self._cache[key]

		self._addons[key] = addon


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
			* 以下の様に継承されていると見做し、MROの末尾(-2)から実装インターフェイスを取得する
			* `class TraitImpl(Trait, IInterface): ...` -> (TraitImpl, Trait, IInterface, object)
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


class Traits:
	"""トレイトマネージャー"""

	def __init__(self, provider: TraitProvider) -> None:
		"""インスタンスを生成

		Args:
			provider (TraitProvider): トレイトプロバイダー
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

	def implements(self, expect: type[T_Ref]) -> bool:
		"""指定のクラスが所有するインターフェイスが実装されているか判定

		Args:
			expect (type[T_Ref]): 期待するインターフェイス
		Returns:
			bool: True = 実装
		"""
		if len(self.__interfaces) == 0:
			self.__ensure_traits()

		requirements: list[type[Any]] = [inherit for inherit in expect.mro() if not isinstance(inherit, (IReflection, object))]
		for required in requirements:
			if required not in self.__interfaces:
				return False

		return True

	def get(self, name: str, symbol: IReflection) -> Callable[..., Any]:
		"""トレイトのメソッドを取得

		Args:
			name (str): メソッド名
			symbol (IReflection): 拡張対象のインスタンス
		Returns:
			Callable[..., Any]: メソッドアダプター
		Raises:
			SemanticsLogicError: トレイトのメソッドが未実装
		"""
		if name not in self.__method_on_trait:
			raise SemanticsLogicError(f'Method not defined. symbol: {symbol}, name: {name}')

		trait = self.__method_on_trait[name]
		return lambda *args: getattr(trait, name)(*args, symbol=symbol)
