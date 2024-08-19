from typing import Iterator, Self

from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.semantics.errors import SemanticsLogicError
from rogw.tranp.semantics.reflection.helper.naming import ClassShorthandNaming
from rogw.tranp.semantics.reflection.interface import IReflection, T_Ref
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node


class ReflectionBase(IReflection):
	"""リフレクション(基底)"""

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
	def via(self) -> 'IReflection':
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

	@implements
	def declare(self, decl: defs.DeclVars, origin: 'IReflection | None' = None) -> 'IReflection':
		"""定義ノードをスタック

		Args:
			decl (DeclVars): 定義元のノード
		Returns:
			IReflection: リフレクション
		"""
		return Reflection(decl, origin=origin if origin else self, decl=decl)

	@implements
	def stack_by(self, node: Node) -> 'IReflection':
		"""ノードをスタック

		Args:
			node (Node): ノード
		Returns:
			IReflection: リフレクション
		"""
		return Reflection(node, origin=self)

	@implements
	def stack_by_self(self) -> 'IReflection':
		"""自身を参照としてスタック

		Returns:
			IReflection: リフレクション
		"""
		return Reflection(self.node, origin=self)

	@implements
	def to(self, node: Node, origin: 'IReflection') -> 'IReflection':
		"""ノードをスタックし、型のシンボルを移行

		Args:
			node (Node): ノード
			origin (IReflection): 型のシンボル
		Returns:
			IReflection: リフレクション
		"""
		return Reflection(node, origin=origin, via=self)

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
		raise SemanticsLogicError(f'Not allowed extends. symbol: {self.types.fullyname}')

	@implements
	def one_of(self, *expects: type[T_Ref]) -> T_Ref:
		"""期待する型と同種ならキャスト

		Args:
			*expects (type[T_Ref]): 期待する型
		Returns:
			T_Ref: インスタンス
		Raises:
			SemanticsLogicError: 継承関係が無い型を指定 XXX 出力する例外は要件等
		"""
		if isinstance(self, expects):
			return self

		raise SemanticsLogicError(f'Not allowed conversion. self: {str(self)}, from: {self.__class__.__name__}, to: {expects}')

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

		__debug = False
		if __debug:
			return f'{self.__class__.__name__}({id(self)}): {str(data)}'

		return str(data)

	@override
	def __str__(self) -> str:
		"""str: オブジェクトの文字列表現"""
		return self.shorthand

	@override
	def __hash__(self) -> int:
		"""int: オブジェクトのハッシュ値"""
		return hash(self.__repr__())


class Symbol(ReflectionBase):
	"""シンボル(クラス定義のオリジナル)"""

	def __init__(self, types: defs.ClassDef) -> None:
		"""インスタンスを生成

		Args:
			types (ClassDef): クラス定義ノード
		"""
		super().__init__()
		self._types = types

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

	def __init__(self, node: Node, origin: IReflection, via: IReflection | None = None, decl: defs.DeclVars | None = None) -> None:
		"""インスタンスを生成

		Args:
			node (Node): ノード
			origin (IReflection): 型のシンボル
			via (IReflection | None): スタックシンボル (default = None)
			decl (DeclVars | None): 定義元のノード (default = None)
		"""
		super().__init__()
		self._node = node
		self._decl = decl if decl else origin.decl
		self._origin = origin
		self._via = via if via else origin.via
		self._attrs: list[IReflection] = []

	@property
	@implements
	def types(self) -> defs.ClassDef:
		"""ClassDef: 型を表すノード"""
		return self._origin.types

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
		return self._origin

	@property
	@override
	def via(self) -> 'IReflection':
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
			1. 自身に設定された属性
			2. 型のシンボルチェーンに設定された属性
		"""
		if self._attrs:
			return self._attrs

		curr = self.origin
		index = 0
		while curr:
			attrs = curr.attrs
			if attrs:
				return attrs

			curr = curr.origin if curr.origin != curr or id(curr.origin) != id(curr) else None

			index += 1

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
