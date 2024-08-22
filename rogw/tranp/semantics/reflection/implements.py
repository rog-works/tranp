from typing import Callable, Iterator, Literal, Self, cast

from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.lang.convertion import safe_cast
from rogw.tranp.semantics.errors import SemanticsLogicError
from rogw.tranp.semantics.reflection.helper.naming import ClassShorthandNaming
from rogw.tranp.semantics.reflection.interface import Addons, IReflection, Addon, T_Ref, Traits
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node


class Options:
	"""生成オプション"""

	def __init__(self,
		types: defs.ClassDef | None = None,
		decl: defs.DeclVars | None = None,
		node: Node | None = None,
		origin: IReflection | None = None,
		via: IReflection | None = None
	) -> None:
		"""インスタンスを生成

		Args:
			types (ClassDef | None): 型を表すノード (default = None)
			decl (DeclVars | None): 定義元のノード (default = None)
			node (Node | None): ノード (default = None)
			origin (IReflection | None): 型のシンボル (default = None)
			via (IReflection | None): スタックシンボル (default = None)
		"""
		self.types = types
		self.decl = decl
		self.node = node
		self.origin = origin
		self.via = via


class ReflectionBase(IReflection):
	"""リフレクション(基底)"""

	def __init__(self, traits: Traits, options: Options) -> None:
		"""インスタンスを生成

		Args:
			traits (Traits): トレイトマネージャー
			options (Options): 生成オプション
		"""
		self.__traits = traits

	# @property
	# @abstractmethod
	# def types(self) -> defs.ClassDef:
	# 	"""ClassDef: 型を表すノード"""
	# 	...

	# @property
	# @abstractmethod
	# def decl(self) -> defs.DeclAll:
	# 	"""DeclAll: 定義元のノード"""
	# 	...

	# @property
	# @abstractmethod
	# def node(self) -> Node:
	# 	"""Node: ノード"""
	# 	...

	@property
	@implements
	def origin(self) -> IReflection:
		"""IReflection: 型のシンボル"""
		return self

	@property
	@implements
	def via(self) -> IReflection:
		"""IReflection: スタックシンボル"""
		return self

	@property
	@implements
	def context(self) -> IReflection:
		"""IReflection: コンテキストを取得 Raises: SemanticsLogicError: コンテキストが無い状態で使用"""
		if self.via == self:
			raise SemanticsLogicError(f'Context is null. symbol: {str(self)}')

		return self.via

	@property
	@implements
	def attrs(self) -> list[IReflection]:
		"""list[IReflection]: 属性シンボルリスト"""
		return []

	@property
	@implements
	def _traits(self) -> Traits:
		"""Traits: トレイトマネージャー"""
		return self.__traits

	@implements
	def declare(self, decl: defs.DeclVars, origin: IReflection | None = None) -> IReflection:
		"""定義ノードをスタックし、型のシンボルを移行。型のシンボル省略時はそのまま引き継ぐ

		Args:
			decl (DeclVars): 定義元のノード
			origin (IReflection | None): 型のシンボル (default = None)
		Returns:
			IReflection: リフレクション
		"""
		return Reflection(self.__traits, Options(decl=decl, node=decl, origin=origin if origin else self))

	@implements
	def stack(self, node: Node | None = None) -> IReflection:
		"""ノードをスタック。ノード省略時は自分自身をスタック

		Args:
			node (Node | None): ノード (default = None)
		Returns:
			IReflection: リフレクション
		"""
		return Reflection(self.__traits, Options(node=node if node else self.node, origin=self))

	@implements
	def to(self, node: Node, origin: IReflection) -> IReflection:
		"""ノードをスタックし、型のシンボルを移行

		Args:
			node (Node): ノード
			origin (IReflection): 型のシンボル
		Returns:
			IReflection: リフレクション
		"""
		return Reflection(self.__traits, Options(node=node, origin=origin, via=self))

	@property
	@implements
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		return ClassShorthandNaming.domain_name(self)

	@implements
	def stacktrace(self) -> Iterator[IReflection]:
		"""スタックシンボルを辿るイテレーターを取得

		Returns:
			Iterator[IReflection]: イテレーター
		"""
		curr = self
		while curr:
			yield curr
			curr = curr.via if curr.via != curr else None

	@implements
	def extends(self: Self, *attrs: IReflection) -> Self:
		"""シンボルが保有する型を拡張情報として属性に取り込む

		Args:
			*attrs (IReflection): 属性シンボルリスト
		Returns:
			Self: インスタンス
		Raises:
			SemanticsLogicError: 実体の無いインスタンスに実行 XXX 出力する例外は要件等
			SemanticsLogicError: 拡張済みのインスタンスに再度実行 XXX 出力する例外は要件等
		"""
		raise SemanticsLogicError(f'Operation not allowed. symbol: {self.types.fullyname}')

	@implements
	def to_temporary(self) -> IReflection:
		"""インスタンスをテンプレート用に複製

		Returns:
			IReflection: 複製したインスタンス
		"""
		new = self.stack()
		new.extends(*[attr.to_temporary() for attr in self.attrs])
		return new

	@implements
	def add_on(self, key: Literal['origin', 'attrs'], addon: Addon) -> None:
		"""アドオンを有効化
		
		Args:
			key (Literal['origin', 'attrs']): キー
			addon (Addon): アドオン
		"""
		raise SemanticsLogicError(f'Operation not allowed. symbol: {self.types.fullyname}')

	@implements
	def impl(self, expect: type[T_Ref]) -> T_Ref:
		"""期待する型と同じインターフェイスを実装していればキャスト

		Args:
			expect (type[T_Ref]): 期待する型
		Returns:
			T_Ref: インスタンス
		Raises:
			SemanticsLogicError: インターフェイスが未実装 XXX 出力する例外は要件等
		"""
		if self._traits.implements(expect):
			return cast(expect, self)

		raise SemanticsLogicError(f'Not allowed conversion. symbol: {self.types.fullyname}, expect: {expect}')

	@override
	def __eq__(self, other: object) -> bool:
		"""比較演算子のオーバーロード

		Args:
			other (object): 比較対象
		Returns:
			bool: True = 同じ
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
		"""str: オブジェクトのシリアライズ表現"""
		data = {
			'types': self.types.fullyname,
			'attrs': [attr.__repr__() for attr in self.attrs],
		}
		return str(data)

	@override
	def __str__(self) -> str:
		"""str: オブジェクトの文字列表現"""
		return self.shorthand

	@override
	def __hash__(self) -> int:
		"""int: オブジェクトのハッシュ値"""
		return hash(self.__repr__())
	
	def __getattr__(self, name: str) -> Callable:
		"""トレイトからメソッドを取得

		Args:
			name (str): メソッド名
		Returns:
			Callable: メソッド
		Note:
			XXX このメソッドを実装すると、存在しないプロパティーを誤って参照した際に警告されなくなる欠点があるため、要検討
		"""
		return self._traits.get(name, self)


class Symbol(ReflectionBase):
	"""シンボル(クラス定義のオリジナル)"""

	@classmethod
	def instantiate(cls, traits: Traits, types: defs.ClassDef) -> 'Symbol':
		"""インスタンスを生成

		Args:
			traits (Traits): トレイトマネージャー
			types (ClassDef): クラス定義ノード
		Returns:
			Symbol: インスタンス
		"""
		return cls(traits, Options(types=types))

	@override
	def __init__(self, traits: Traits, options: Options) -> None:
		"""インスタンスを生成

		Args:
			traits (Traits): トレイトマネージャー
			options (Options): 生成オプション
		"""
		super().__init__(traits, options)
		self._types = safe_cast(options.types)

	@property
	@implements
	def types(self) -> defs.ClassDef:
		"""ClassDef: 型を表すノード"""
		return self._types

	@property
	@implements
	def decl(self) -> defs.DeclAll:
		"""DeclAll: 定義元のノード"""
		return self._types

	@property
	@implements
	def node(self) -> Node:
		"""Node: ノード"""
		return self._types


class Reflection(ReflectionBase):
	"""リフレクションの共通実装(基底)"""

	@override
	def __init__(self, traits: Traits, options: Options) -> None:
		"""インスタンスを生成

		Args:
			traits (Traits): トレイトマネージャー
			options (Options): 生成オプション
		"""
		super().__init__(traits, options)
		self._node = safe_cast(options.node)
		self._origin = safe_cast(options.origin)
		self._decl = options.decl if options.decl else self._origin.decl
		self._via = options.via if options.via else self._origin.via
		self._attrs: list[IReflection] = []
		self._addons = Addons()

	@property
	@implements
	def types(self) -> defs.ClassDef:
		"""ClassDef: 型を表すノード"""
		return self.origin.types

	@property
	@implements
	def decl(self) -> defs.DeclAll:
		"""DeclAll: 定義元のノード"""
		return self._decl

	@property
	@implements
	def node(self) -> Node:
		"""Node: ノード"""
		return self._node

	@property
	@override
	def origin(self) -> IReflection:
		"""IReflection: 型のシンボル"""
		if self._addons.active('origin'):
			return self._addons.origin

		return self._origin

	@property
	@override
	def via(self) -> IReflection:
		"""IReflection: スタックシンボル"""
		return self._via

	@property
	@override
	def attrs(self) -> list[IReflection]:
		"""属性シンボルリストを取得

		Returns:
			list[IReflection]: 属性シンボルリスト
		Note:
			### 属性の評価順序
			1. アドオンから注入された属性
			2. 自身に設定された属性
			3. 型のシンボルに設定された属性
		"""
		if self._addons.active('attrs'):
			return self._addons.attrs

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
			*attrs (IReflection): 属性シンボルリスト
		Returns:
			Self: インスタンス
		Raises:
			SemanticsLogicError: 実体の無いインスタンスに実行
			SemanticsLogicError: 拡張済みのインスタンスに再度実行
		"""
		if self._attrs:
			raise SemanticsLogicError(f'Already set attibutes. symbol: {self.types.fullyname}')
		
		self._attrs = list(attrs)
		return self

	@override
	def add_on(self, key: Literal['origin', 'attrs'], addon: Addon) -> None:
		"""アドオンを有効化
		
		Args:
			key (Literal['origin', 'attrs']): キー
			addon (Addon): アドオン
		"""
		self._addons.activate(key, addon)
