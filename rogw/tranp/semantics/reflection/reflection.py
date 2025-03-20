from collections.abc import Callable, Iterator
from typing import Any, Literal, Self, cast, override

from rogw.tranp.lang.annotation import implements
from rogw.tranp.lang.convertion import safe_cast
from rogw.tranp.lang.trait import Traits
from rogw.tranp.semantics.errors import MustBeImplementedError, SemanticsLogicError
from rogw.tranp.semantics.reflection.helper.naming import ClassShorthandNaming
from rogw.tranp.semantics.reflection.base import Mods, IReflection, Mod, T_Ref
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node


class Options:
	"""生成オプション"""

	def __init__(self,
		types: defs.ClassDef | None = None,
		decl: defs.DeclAll | None = None,
		node: Node | None = None,
		origin: IReflection | None = None,
		via: IReflection | None = None
	) -> None:
		"""インスタンスを生成

		Args:
			types: 型を表すノード (default = None)
			decl: 定義元のノード (default = None)
			node: ノード (default = None)
			origin: 型のシンボル (default = None)
			via: スタックシンボル (default = None)
		"""
		self.types = types
		self.decl = decl
		self.node = node
		self.origin = origin
		self.via = via


class ReflectionBase(IReflection):
	"""リフレクション(基底)"""

	def __init__(self, traits: Traits[IReflection], options: Options) -> None:
		"""インスタンスを生成

		Args:
			traits: トレイトマネージャー
			options: 生成オプション
		"""
		self.__traits = traits

	# @property
	# @abstractmethod
	# def types(self) -> defs.ClassDef:
	# 	"""Returns: 型を表すノード"""
	# 	...

	# @property
	# @abstractmethod
	# def decl(self) -> defs.DeclAll:
	# 	"""Returns: 定義元のノード"""
	# 	...

	# @property
	# @abstractmethod
	# def node(self) -> Node:
	# 	"""Returns: ノード"""
	# 	...

	@property
	@implements
	def origin(self) -> IReflection:
		"""Returns: 型のシンボル"""
		return self

	@property
	@implements
	def via(self) -> IReflection:
		"""Returns: スタックシンボル"""
		return self

	@property
	@implements
	def context(self) -> IReflection:
		"""Returns: コンテキストを取得 Raises: SemanticsLogicError: コンテキストが無い状態で使用"""
		if self.via == self:
			raise SemanticsLogicError(f'Context is null. symbol: {str(self)}')

		return self.via

	@property
	@implements
	def attrs(self) -> list[IReflection]:
		"""Returns: 属性シンボルリスト"""
		return []

	@property
	@implements
	def _traits(self) -> Traits[IReflection]:
		"""Returns: トレイトマネージャー"""
		return self.__traits

	@implements
	def declare(self, decl: defs.DeclVars, origin: IReflection | None = None) -> IReflection:
		"""定義ノードをスタックし、型のシンボルを移行。型のシンボル省略時はそのまま引き継ぐ

		Args:
			decl: 定義元のノード
			origin: 型のシンボル (default = None)
		Returns:
			リフレクション
		"""
		return Reflection(self.__traits, Options(decl=decl, node=decl, origin=origin if origin else self))

	@implements
	def stack(self, node: Node | None = None) -> IReflection:
		"""ノードをスタック。ノード省略時は自分自身をスタック

		Args:
			node: ノード (default = None)
		Returns:
			リフレクション
		"""
		return Reflection(self.__traits, Options(node=node if node else self.node, origin=self))

	@implements
	def to(self, node: Node, origin: IReflection) -> IReflection:
		"""ノードをスタックし、型のシンボルを移行

		Args:
			node: ノード
			origin: 型のシンボル
		Returns:
			リフレクション
		"""
		return Reflection(self.__traits, Options(decl=self.decl, node=node, origin=origin, via=self))

	@implements
	def pretty(self) -> str:
		"""Returns: オブジェクトの短縮表記(装飾) Note: デバッグ用途のため判定に用いるのはNG"""
		return ClassShorthandNaming.domain_name_for_debug(self)

	@implements
	def stacktrace(self) -> Iterator[IReflection]:
		"""スタックシンボルを辿るイテレーターを取得

		Returns:
			イテレーター
		"""
		curr = self
		while curr:
			yield curr
			curr = curr.via if curr.via != curr else None

	@implements
	def extends(self: Self, *attrs: IReflection) -> Self:
		"""シンボルが保有する型を拡張情報として属性に取り込む

		Args:
			*attrs: 属性シンボルリスト
		Returns:
			インスタンス
		Raises:
			SemanticsLogicError: 実体の無いインスタンスに実行 XXX 出力する例外は要件等
			SemanticsLogicError: 拡張済みのインスタンスに再度実行 XXX 出力する例外は要件等
		"""
		raise SemanticsLogicError(f'Operation not allowed. symbol: {self.types.fullyname}')

	@implements
	def to_temporary(self) -> IReflection:
		"""インスタンスをテンプレート用に複製

		Returns:
			複製したインスタンス
		"""
		new = self.stack()
		new.extends(*[attr.to_temporary() for attr in self.attrs])
		return new

	@implements
	def mod_on(self, key: Literal['origin', 'attrs'], mod: Mod) -> None:
		"""モッドを有効化
		
		Args:
			key: キー
			mod: モッド
		"""
		raise SemanticsLogicError(f'Operation not allowed. symbol: {self.types.fullyname}')

	@implements
	def impl(self, expect: type[T_Ref]) -> T_Ref:
		"""期待する型と同じインターフェイスを実装していればキャスト

		Args:
			expect: 期待する型
		Returns:
			インスタンス
		Raises:
			MustBeImplementedError: トレイトのメソッドが未実装
		"""
		if self._traits.implements(expect):
			return cast(T_Ref, self)

		raise MustBeImplementedError(f'Method not defined. symbol: {self.types.fullyname}, expect: {expect}')

	@override
	def __eq__(self, other: object) -> bool:
		"""比較演算子のオーバーロード

		Args:
			other: 比較対象
		Returns:
			True = 同じ
		Raises:
			SemanticsLogicError: 継承関係の無いオブジェクトを指定 XXX 出力する例外は要件等
		"""
		if other is None:
			return False

		if not isinstance(other, IReflection):
			raise SemanticsLogicError(f'Not allowed comparison. other: {type(other)}')

		return other.__repr__() == self.__repr__()

	@override
	def __repr__(self) -> str:
		"""Returns: オブジェクトのシリアライズ表現"""
		data = {
			'types': self.types.fullyname,
			'attrs': [attr.__repr__() for attr in self.attrs],
		}
		return str(data)

	@override
	def __str__(self) -> str:
		"""Returns: オブジェクトの文字列表現"""
		return self.pretty()

	@override
	def __hash__(self) -> int:
		"""Returns: オブジェクトのハッシュ値"""
		return hash(self.__repr__())
	
	def __getattr__(self, name: str) -> Callable[..., Any]:
		"""トレイトからメソッドを取得

		Args:
			name: メソッド名
		Returns:
			メソッド
		Note:
			XXX このメソッドを実装すると、存在しないプロパティーを誤って参照した際に警告されないため、要検討
		"""
		return self._traits.get(name, self)


class Symbol(ReflectionBase):
	"""シンボル

	Note:
		```
		* シリアライザーの実装に強依存しているため、スキーマの変更に注意
		@see rogw.tranp.semantics.reflection.serializer.ReflectionSerializer
		```
	"""

	@classmethod
	def instantiate(cls, traits: Traits[IReflection], types: defs.ClassDef) -> 'Symbol':
		"""インスタンスを生成

		Args:
			traits: トレイトマネージャー
			types: クラス定義ノード
		Returns:
			インスタンス
		"""
		return cls(traits, Options(types=types))

	@override
	def __init__(self, traits: Traits[IReflection], options: Options) -> None:
		"""インスタンスを生成

		Args:
			traits: トレイトマネージャー
			options: 生成オプション
		"""
		super().__init__(traits, options)
		self._types = safe_cast(options.types)

	@property
	@implements
	def types(self) -> defs.ClassDef:
		"""Returns: 型を表すノード"""
		return self._types

	@property
	@implements
	def decl(self) -> defs.DeclAll:
		"""Returns: 定義元のノード"""
		return self._types

	@property
	@implements
	def node(self) -> Node:
		"""Returns: ノード"""
		return self._types


class Reflection(ReflectionBase):
	"""リフレクション

	Note:
		```
		* シリアライザーの実装に強依存しているため、スキーマの変更に注意
		@see rogw.tranp.semantics.reflection.serializer.ReflectionSerializer
		```
	"""

	@override
	def __init__(self, traits: Traits[IReflection], options: Options) -> None:
		"""インスタンスを生成

		Args:
			traits: トレイトマネージャー
			options: 生成オプション
		"""
		super().__init__(traits, options)
		self._node = safe_cast(options.node)
		self._origin = safe_cast(options.origin)
		self._decl = options.decl if options.decl else self._origin.decl
		self._via = options.via if options.via else self._origin.via
		self._attrs: list[IReflection] = []
		self._mods = Mods()

	@property
	@implements
	def types(self) -> defs.ClassDef:
		"""Returns: 型を表すノード"""
		return self.origin.types

	@property
	@implements
	def decl(self) -> defs.DeclAll:
		"""Returns: 定義元のノード"""
		return self._decl

	@property
	@implements
	def node(self) -> Node:
		"""Returns: ノード"""
		return self._node

	@property
	@override
	def origin(self) -> IReflection:
		"""Returns: 型のシンボル"""
		if self._mods.active('origin'):
			return self._mods.origin

		return self._origin

	@property
	@override
	def via(self) -> IReflection:
		"""Returns: スタックシンボル"""
		return self._via

	@property
	@override
	def attrs(self) -> list[IReflection]:
		"""属性シンボルリストを取得

		Returns:
			属性シンボルリスト
		Note:
			```
			### 属性の評価順序
			1. モッドから注入された属性
			2. 自身に設定された属性
			3. 型のシンボルに設定された属性
			```
		"""
		if self._mods.active('attrs'):
			return self._mods.attrs

		if self._attrs:
			return self._attrs

		attrs = self.origin.attrs
		if attrs:
			return attrs

		return []

	@override
	def extends(self: Self, *attrs: IReflection) -> Self:
		"""シンボルが保持する型を拡張情報として属性に取り込む

		Args:
			*attrs: 属性シンボルリスト
		Returns:
			インスタンス
		Raises:
			SemanticsLogicError: 実体の無いインスタンスに実行
			SemanticsLogicError: 拡張済みのインスタンスに再度実行
		"""
		if self._attrs:
			raise SemanticsLogicError(f'Already set attibutes. symbol: {self.types.fullyname}')
		
		self._attrs = list(attrs)
		return self

	@override
	def mod_on(self, key: Literal['origin', 'attrs'], mod: Mod) -> None:
		"""モッドを有効化
		
		Args:
			key: キー
			mod: モッド
		"""
		self._mods.activate(key, mod)
