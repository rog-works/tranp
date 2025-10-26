from abc import ABCMeta, abstractmethod
from collections.abc import Iterator
from typing import Literal, Protocol, Self, TypeVar

from rogw.tranp.errors import Errors
from rogw.tranp.lang.trait import Traits
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node

T_Ref = TypeVar('T_Ref', bound='IReflection')


class IReflection(metaclass=ABCMeta):
	"""リフレクション

	Attributes:
		types: 型を表すノード
		decl: 定義元のノード
		node: ノード
		origin: 型のシンボル
		via: スタックシンボル
		context: コンテキストのシンボル
		attrs: 属性シンボルリスト
	"""

	@property
	@abstractmethod
	def types(self) -> defs.ClassDef:
		"""Returns: 型を表すノード"""
		...

	@property
	@abstractmethod
	def decl(self) -> defs.DeclAll:
		"""Returns: 定義元のノード"""
		...

	@property
	@abstractmethod
	def node(self) -> Node:
		"""Returns: ノード"""
		...

	@property
	@abstractmethod
	def origin(self) -> 'IReflection':
		"""Returns: 型のシンボル"""
		...

	@property
	@abstractmethod
	def via(self) -> 'IReflection':
		"""Returns: スタックシンボル"""
		...

	@property
	@abstractmethod
	def context(self) -> 'IReflection':
		"""Returns: コンテキストを取得 Raises: Errors.Never: コンテキストが無い状態で使用"""
		...

	@property
	@abstractmethod
	def attrs(self) -> list['IReflection']:
		"""Returns: 属性シンボルリスト"""
		...

	@property
	@abstractmethod
	def _traits(self) -> Traits['IReflection']:
		"""Returns: トレイトマネージャー"""
		...

	@abstractmethod
	def declare(self, decl: defs.DeclVars, origin: 'IReflection | None' = None) -> 'IReflection':
		"""定義ノードをスタックし、型のシンボルを移行。型のシンボル省略時はそのまま引き継ぐ

		Args:
			decl: 定義元のノード
			origin: 型のシンボル (default = None)
		Returns:
			リフレクション
		"""
		...

	@abstractmethod
	def stack(self, node: Node | None = None) -> 'IReflection':
		"""ノードをスタック。ノード省略時は自分自身をスタック

		Args:
			node: ノード (default = None)
		Returns:
			リフレクション
		"""
		...

	@abstractmethod
	def to(self, node: Node, origin: 'IReflection') -> 'IReflection':
		"""ノードをスタックし、型のシンボルを移行

		Args:
			node: ノード
			origin: 型のシンボル
		Returns:
			リフレクション
		"""
		...

	@property
	@abstractmethod
	def _dump(self) -> str:
		"""Returns: 比較用の文字列"""
		...

	@property
	@abstractmethod
	def pretty(self) -> str:
		"""Returns: オブジェクトの短縮表記(装飾) Note: デバッグ用途のため判定に用いるのはNG"""
		...

	@abstractmethod
	def stacktrace(self) -> Iterator['IReflection']:
		"""スタックシンボルを辿るイテレーターを取得

		Returns:
			イテレーター
		"""
		...

	@abstractmethod
	def extends(self: Self, *attrs: 'IReflection') -> Self:
		"""シンボルが保有する型を拡張情報として属性に取り込む

		Args:
			*attrs: 属性シンボルリスト
		Returns:
			インスタンス
		Raises:
			Errors.Never: 実体の無い/拡張済みのインスタンスに実行
		"""
		...

	@abstractmethod
	def to_temporary(self) -> 'IReflection':
		"""インスタンスをテンプレート用に複製

		Returns:
			複製したインスタンス
		"""
		...

	@abstractmethod
	def mod_on(self, key: Literal['origin', 'attrs'], mod: 'Mod') -> None:
		"""モッドを有効化
		
		Args:
			key: キー
			mod: モッド
		"""
		...

	@abstractmethod
	def impl(self, expect: type[T_Ref]) -> T_Ref:
		"""期待する型と同じインターフェイスを実装していればキャスト

		Args:
			expect: 期待する型
		Returns:
			インスタンス
		Raises:
			Errors.MustBeImplemented: トレイトのメソッドが未実装
		"""
		...


class Mod(Protocol):
	"""モッドプロトコル"""

	def __call__(self) -> list[IReflection]:
		"""Returns: シンボルリスト"""
		...


class Mods:
	"""モッドマネージャー"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self._mods: dict[str, Mod] = {}
		self._cache: dict[str, list[IReflection]] = {}

	@property
	def origin(self) -> IReflection:
		"""Returns: 型のシンボル Raises: Errors.Never: モッドが無効"""
		if not self.active('origin'):
			raise Errors.Never('No origin')

		if 'origin' not in self._cache:
			self._cache['origin'] = self._mods['origin']()

		return self._cache['origin'][0]

	@property
	def attrs(self) -> list[IReflection]:
		"""Returns: 属性シンボルリスト Raises: Errors.Never: モッドが無効"""
		if not self.active('attrs'):
			raise Errors.Never('No attrs')

		if 'attrs' not in self._cache:
			self._cache['attrs'] = self._mods['attrs']()

		return self._cache['attrs']

	def active(self, key: Literal['origin', 'attrs']) -> bool:
		"""モッドが有効か判定

		Args:
			key: キー
		Returns:
			True = 有効
		"""
		return key in self._mods

	def activate(self, key: Literal['origin', 'attrs'], mod: Mod) -> None:
		"""モッドを有効化

		Args:
			key: キー
			mod: モッド
		"""
		if key in self._cache:
			del self._cache[key]

		self._mods[key] = mod
