from abc import ABCMeta, abstractmethod
from collections.abc import Iterator
from typing import Literal, Protocol, Self, TypeVar

from rogw.tranp.lang.trait import Traits
from rogw.tranp.semantics.errors import SemanticsLogicError
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node

T_Ref = TypeVar('T_Ref', bound='IReflection')


class IReflection(metaclass=ABCMeta):
	"""リフレクション

	Attributes:
		types (ClassDef): 型を表すノード
		decl (DeclAll): 定義元のノード
		node (Node): ノード
		origin (IReflection): 型のシンボル
		via (IReflection): スタックシンボル
		context (IReflection): コンテキストのシンボル
		attrs (list[IReflection]): 属性シンボルリスト
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
	def _traits(self) -> Traits['IReflection']:
		"""Traits[IReflection]: トレイトマネージャー"""
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
	def mod_on(self, key: Literal['origin', 'attrs'], mod: 'Mod') -> None:
		"""モッドを有効化
		
		Args:
			key (Literal['origin', 'attrs']): キー
			mod (Mod): モッド
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
			MustBeImplementedError: トレイトのメソッドが未実装
		"""
		...


class Mod(Protocol):
	"""モッドプロトコル"""

	def __call__(self) -> list[IReflection]:
		"""list[IReflection]: シンボルリスト"""
		...


class Mods:
	"""モッドマネージャー"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self._mods: dict[str, Mod] = {}
		self._cache: dict[str, list[IReflection]] = {}

	@property
	def origin(self) -> IReflection:
		"""IReflection: 型のシンボル"""
		if not self.active('origin'):
			raise SemanticsLogicError('Has no origin')

		if 'origin' not in self._cache:
			self._cache['origin'] = self._mods['origin']()

		return self._cache['origin'][0]

	@property
	def attrs(self) -> list[IReflection]:
		"""list[IReflection]: 属性シンボルリスト"""
		if not self.active('attrs'):
			raise SemanticsLogicError('Has no attrs')

		if 'attrs' not in self._cache:
			self._cache['attrs'] = self._mods['attrs']()

		return self._cache['attrs']

	def active(self, key: Literal['origin', 'attrs']) -> bool:
		"""モッドが有効か判定

		Args:
			key (Literal['origin', 'attrs']): キー
		Returns:
			bool: True = 有効
		"""
		return key in self._mods

	def activate(self, key: Literal['origin', 'attrs'], mod: Mod) -> None:
		"""モッドを有効化

		Args:
			key (Literal['origin', 'attrs']): キー
			mod (Mod): モッド
		"""
		if key in self._cache:
			del self._cache[key]

		self._mods[key] = mod
