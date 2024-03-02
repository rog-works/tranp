from typing import Any, Callable, Iterator, Self, TypeAlias, TypeVar

from rogw.tranp.errors import FatalError, LogicError
from rogw.tranp.lang.implementation import implements, injectable, override
from rogw.tranp.semantics.helper.naming import ClassShorthandNaming
from rogw.tranp.semantics.reflection import DB, IReflection, IWrapper, Roles, SymbolRaws
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node

T_Raw = TypeVar('T_Raw', bound='IReflection')


class Reflection(IReflection):
	"""リフレクション(基底)"""

	@injectable
	def __init__(self, raws: SymbolRaws | None = None) -> None:
		"""インスタンスを生成

		Args:
			raws (SymbolRaws | None): シンボルテーブル (default = None)
		"""
		self.__raws = raws

	@property
	@implements
	def _raws(self) -> SymbolRaws:
		"""SymbolRaws: 所属するシンボルテーブル"""
		if self.__raws is not None:
			return self.__raws

		raise FatalError(f'Unreachable code.')

	@implements
	def set_raws(self, raws: SymbolRaws) -> None:
		"""所属するシンボルテーブルを設定

		Args:
			raws (SymbolRaws): シンボルテーブル
		"""
		self.__raws = raws

	@property
	@implements
	def attrs(self) -> list['IReflection']:
		"""list[IReflection]: 属性シンボルリスト"""
		return []

	@property
	@implements
	def origin(self) -> 'IReflection | None':
		"""IReflection | None: スタックシンボル"""
		return None

	@property
	@implements
	def via(self) -> Node | None:
		"""Node | None: 参照元のノード"""
		return None

	@property
	@implements
	def context(self) -> 'IReflection':
		"""コンテキストを取得

		Returns:
			IReflection: コンテキストのシンボル
		Raises:
			LogicError: コンテキストが無い状態で使用
		"""
		raise LogicError(f'Context is null. symbol: {str(self)}, fullyname: {self.ref_fullyname}')

	@property	
	@implements
	def has_entity(self) -> bool:
		"""bool: True = 実体を持つ"""
		return self.role.has_entity

	def _clone(self: Self, **kwargs: Any) -> Self:
		"""インスタンスを複製

		Args:
			**kwargs (Any): コンストラクターの引数
		Returns:
			Self: 複製したインスタンス
		"""
		new = self.__class__(**kwargs)
		if self.attrs:
			return new.extends(*[attr.clone() for attr in self.attrs])

		return new

	@property
	@implements
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		return ClassShorthandNaming.domain_name(self)

	@implements
	def hierarchy(self) -> Iterator['IReflection']:
		"""参照元を辿るイテレーターを取得

		Returns:
			Iterator[IReflection]: イテレーター
		"""
		curr = self
		while curr:
			yield curr
			curr = curr.origin

	@implements
	def extends(self: Self, *attrs: 'IReflection') -> Self:
		"""シンボルが保有する型を拡張情報として属性に取り込む

		Args:
			*attrs (IReflection): 属性シンボルリスト
		Returns:
			Self: インスタンス
		Raises:
			LogicError: 実体の無いインスタンスに実行 XXX 出力する例外は要件等
			LogicError: 拡張済みのインスタンスに再度実行 XXX 出力する例外は要件等
		"""
		raise LogicError(f'Not allowed extends. symbol: {self.types.fullyname}')

	@property
	@implements
	def to(self) -> 'SymbolWrapper':
		"""ラッパーファクトリーを生成

		Returns:
			IWrapper: ラッパーファクトリー
		"""
		return SymbolWrapper(self)

	@implements
	def one_of(self, expects: type[T_Raw]) -> T_Raw:
		"""期待する型と同種ならキャスト

		Args:
			expects (type[T_Raw]): 期待する型
		Returns:
			T_Raw: インスタンス
		Raises:
			LogicError: 継承関係が無い型を指定 XXX 出力する例外は要件等
		"""
		if isinstance(self, expects):
			return self

		raise LogicError(f'Not allowed conversion. self: {str(self)}, from: {self.__class__.__name__}, to: {expects}')

	@override
	def __eq__(self, other: object) -> bool:
		"""比較演算子のオーバーロード

		Args:
			other (object): 比較対象
		Returns:
			bool: True = 同じ
		Raises:
			LogicError: 継承関係の無いオブジェクトを指定 XXX 出力する例外は要件等
		"""
		if other is None:
			return False

		if not isinstance(other, IReflection):
			raise LogicError(f'Not allowed comparison. other: {type(other)}')

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


class Symbol(Reflection):
	"""シンボル(クラス定義のオリジナル)"""

	@injectable
	def __init__(self, types: defs.ClassDef) -> None:
		"""インスタンスを生成

		Args:
			types (ClassDef): クラス定義ノード
		"""
		super().__init__()
		self._types = types

	@property
	@implements
	def ref_fullyname(self) -> str:
		"""str: 完全参照名"""
		return self.org_fullyname

	@property
	@implements
	def org_fullyname(self) -> str:
		"""str: 完全参照名(オリジナル)"""
		return self.types.fullyname

	@property
	@implements
	def types(self) -> defs.ClassDef:
		"""ClassDef: クラス定義ノード"""
		return self._types

	@property
	@implements
	def decl(self) -> defs.DeclAll:
		"""DeclAll: クラス/変数宣言ノード"""
		return self.types

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Origin

	@implements
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(types=self.types)


class ReflectionImpl(Reflection):
	"""リフレクションの共通実装(基底)"""

	def __init__(self, origin: 'Symbol | ReflectionImpl') -> None:
		"""インスタンスを生成

		Args:
			origin (Symbol | ReflectionImpl): スタックシンボル
		"""
		super().__init__(origin._raws)
		self._origin = origin
		self._attrs: list[IReflection] = []

	@property
	@implements
	def ref_fullyname(self) -> str:
		"""str: 完全参照名"""
		return self._origin.ref_fullyname

	@property
	@implements
	def org_fullyname(self) -> str:
		"""str: 完全参照名(オリジナル)"""
		return self._origin.org_fullyname

	@property
	@implements
	def types(self) -> defs.ClassDef:
		"""ClassDef: クラス定義ノード"""
		return self._origin.types

	@property
	@implements
	def decl(self) -> defs.DeclAll:
		"""DeclAll: クラス/変数宣言ノード"""
		return self._origin.decl

	@property
	@implements
	def attrs(self) -> list[IReflection]:
		"""属性シンボルリストを取得

		Returns:
			list[IReflection]: 属性シンボルリスト
		Note:
			# 属性の評価順序
			1. 自身に設定された属性
			2. スタックシンボルに設定された属性
			3. シンボルテーブル上の参照元に設定された属性
		"""
		if self._attrs:
			return self._attrs

		if self.origin.attrs:
			return self.origin.attrs

		return self._shared_origin.attrs

	@property
	@override
	def origin(self) -> IReflection:
		"""IReflection: スタックシンボル"""
		return self._origin

	@property
	def _shared_origin(self) -> IReflection:
		"""シンボルテーブル上に存在する共有シンボルを取得

		Returns:
			IReflection: シンボルテーブル上に存在する共有されたシンボル
		Note:
			属性を取得する際にのみ利用 @see attrs
		"""
		if self._origin.org_fullyname in self._raws:
			origin = self._raws[self._origin.org_fullyname]
			if id(origin) != id(self):
				return origin

		return self._origin

	@implements
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin)

	@override
	def extends(self: Self, *attrs: IReflection) -> Self:
		"""シンボルが保持する型を拡張情報として属性に取り込む

		Args:
			*attrs (IReflection): 属性シンボルリスト
		Returns:
			Self: インスタンス
		Raises:
			LogicError: 実体の無いインスタンスに実行
			LogicError: 拡張済みのインスタンスに再度実行
		"""
		if isinstance(self, ReflectionReference):
			raise LogicError(f'Not allowd extends. symbol: {self.types.fullyname}')

		if self._attrs:
			raise LogicError(f'Already set attibutes. symbol: {self.types.fullyname}')
		
		self._attrs = list(attrs)
		return self


class ReflectionImport(ReflectionImpl):
	"""シンボル(インポート)"""

	def __init__(self, origin: 'ImportOrigins', via: Node) -> None:
		"""インスタンスを生成

		Args:
			origin (SymbolOrigin | SymbolVar): スタックシンボル
			via (Node): 参照元のノード
		"""
		super().__init__(origin)
		self._via = via

	@property
	@override
	def ref_fullyname(self) -> str:
		"""str: 完全参照名"""
		return self.org_fullyname.replace(self.types.module_path, self.via.module_path)

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Import

	@property
	@override
	def via(self) -> Node:
		"""Node: 参照元のノード"""
		return self._via

	@override
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via)


class ReflectionClass(ReflectionImpl):
	"""シンボル(クラス定義)"""

	def __init__(self, origin: 'ClassOrigins', decl: defs.ClassDef) -> None:
		"""インスタンスを生成

		Args:
			origin (SymbolOrigins): スタックシンボル
			decl (ClassDef): クラス定義ノード
		"""
		super().__init__(origin)
		self._decl = decl

	@property
	@override
	def decl(self) -> defs.DeclAll:
		"""DeclAll: クラス/変数宣言ノード"""
		return self._decl

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Class

	@override
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, decl=self.decl)


class ReflectionVar(ReflectionImpl):
	def __init__(self, origin: 'VarOrigins', decl: defs.DeclAll) -> None:
		"""インスタンスを生成

		Args:
			origin (SymbolOrigin | SymbolImport): スタックシンボル
			decl (DeclAll): クラス/変数宣言ノード
		"""
		super().__init__(origin)
		self._decl = decl

	@property
	@override
	def decl(self) -> defs.DeclAll:
		"""DeclAll: クラス/変数宣言ノード"""
		return self._decl

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Var

	@override
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, decl=self.decl)


class ReflectionGeneric(ReflectionImpl):
	def __init__(self, origin: 'GenericOrigins', via: defs.Type) -> None:
		"""インスタンスを生成

		Args:
			origin (SymbolOrigin | SymbolImport): スタックシンボル
			via (Type): 参照元のノード
		"""
		super().__init__(origin)
		self._via = via

	@property
	@override
	def via(self) -> Node:
		"""Node: 参照元のノード"""
		return self._via

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Generic

	@override
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via)


class ReflectionLiteral(ReflectionImpl):
	def __init__(self, origin: 'LiteralOrigins', via: defs.Literal | defs.Comprehension) -> None:
		"""インスタンスを生成

		Args:
			origin (LiteralOrigins): スタックシンボル
			via (Literal | Comprehension): 参照元のノード
		"""
		super().__init__(origin)
		self._via = via

	@property
	@override
	def via(self) -> Node:
		"""Node: 参照元のノード"""
		return self._via

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Literal

	@override
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via)


class ReflectionReference(ReflectionImpl):
	def __init__(self, origin: 'RefOrigins', via: defs.Reference, context: IReflection | None = None) -> None:
		"""インスタンスを生成

		Args:
			origin (RefOrigins): スタックシンボル
			via (Reference): 参照元のノード
			context (IReflection | None): コンテキストのシンボル (default = None)
		"""
		super().__init__(origin)
		self._via = via
		self._context = context

	@property
	@override
	def via(self) -> Node:
		"""Node: 参照元のノード"""
		return self._via

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Reference

	@property
	@override
	def context(self) -> IReflection:
		"""コンテキストを取得

		Returns:
			IReflection: コンテキストのシンボル
		Raises:
			LogicError: コンテキストが無いシンボルで使用
		"""
		if self._context is not None:
			return self._context

		raise LogicError(f'Context is null. symbol: {str(self)}, fullyname: {self.ref_fullyname}')

	@override
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via, context=self._context)


class ReflectionResult(ReflectionImpl):
	def __init__(self, origin: 'ResultOrigins', via: defs.Operator) -> None:
		"""インスタンスを生成

		Args:
			origin (ResultOrigins): スタックシンボル
			via (Operator): 参照元のノード
		"""
		super().__init__(origin)
		self._via = via

	@property
	@override
	def via(self) -> Node:
		"""Node: 参照元のノード"""
		return self._via

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Result

	@override
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via)


class SymbolProxy(IReflection):
	"""シンボルプロクシー
	* 拡張設定を遅延処理
	* 参照順序の自動的な解決
	* 不必要な拡張設定を省略

	Note:
		シンボルの登録順序と参照順序が重要なインスタンスに関して使用 ※現状はResolveUnknownでのみ使用
	"""

	def __init__(self, org_raw: IReflection, extender: Callable[[], IReflection]) -> None:
		"""インスタンスを生成

		Args:
			org_raw (IReflection): オリジナル
			extender (Callable[[], IReflection]): シンボル拡張設定ファクトリー
		"""
		self.__org_raw = org_raw
		self.__extender = extender
		self.__new_raw: IReflection | None = None

	@property
	def __new_raw_proxy(self) -> IReflection:
		"""IReflection: 拡張後のシンボル"""
		if self.__new_raw is None:
			self.__new_raw = self.__extender()

		return self.__new_raw

	@property
	@implements
	def _raws(self) -> DB:
		"""DB: 所属するシンボルテーブル"""
		return self.__org_raw._raws

	@implements
	def set_raws(self, raws: DB) -> None:
		"""所属するシンボルテーブルを設定

		Args:
			raws (DB): シンボルテーブル
		"""
		self.__org_raw.set_raws(raws)

	@property
	@implements
	def ref_fullyname(self) -> str:
		"""str: 完全参照名"""
		return self.__new_raw_proxy.ref_fullyname

	@property
	@implements
	def org_fullyname(self) -> str:
		"""str: 完全参照名(オリジナル)"""
		return self.__new_raw_proxy.org_fullyname

	@property
	@implements
	def types(self) -> defs.ClassDef:
		"""ClassDef: クラス定義ノード"""
		return self.__new_raw_proxy.types

	@property
	@implements
	def decl(self) -> defs.DeclAll:
		"""DeclAll: クラス/変数宣言ノード"""
		return self.__new_raw_proxy.decl

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return self.__new_raw_proxy.role

	@property
	@implements
	def attrs(self) -> list[IReflection]:
		"""list[IReflection]: 属性シンボルリスト"""
		return self.__new_raw_proxy.attrs

	@property
	@implements
	def origin(self) -> IReflection | None:
		"""IReflection | None: スタックシンボル"""
		return self.__new_raw_proxy.origin

	@property
	@implements
	def via(self) -> Node | None:
		"""Node | None: 参照元のノード"""
		return self.__new_raw_proxy.via

	@property
	@implements
	def context(self) -> 'IReflection':
		"""コンテキストを取得

		Returns:
			IReflection: コンテキストのシンボル
		Raises:
			LogicError: コンテキストが無い状態で使用
		"""
		return self.__new_raw_proxy.context

	@property	
	@implements
	def has_entity(self) -> bool:
		"""bool: True = 実体を持つ"""
		return self.__new_raw_proxy.has_entity

	@implements
	def clone(self) -> IReflection:
		"""インスタンスを複製

		Returns:
			IReflection: 複製したインスタンス
		"""
		return self.__new_raw_proxy.clone()

	@property
	@implements
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		return self.__new_raw_proxy.shorthand

	@implements
	def hierarchy(self) -> Iterator[IReflection]:
		"""参照元を辿るイテレーターを取得

		Returns:
			Iterator[IReflection]: イテレーター
		"""
		return self.__new_raw_proxy.hierarchy()

	@implements
	def extends(self, *attrs: IReflection) -> IReflection:
		"""シンボルが保有する型を拡張情報として属性に取り込む

		Args:
			*attrs (IReflection): 属性シンボルリスト
		Returns:
			T_Ref: インスタンス
		Raises:
			LogicError: 実体の無いインスタンスに実行 XXX 出力する例外は要件等
			LogicError: 拡張済みのインスタンスに再度実行 XXX 出力する例外は要件等
		"""
		return self.__new_raw_proxy.extends(*attrs)

	@property
	@implements
	def to(self) -> 'IWrapper':
		"""ラッパーファクトリーを生成

		Returns:
			SymbolWrapper: ラッパーファクトリー
		"""
		return self.__new_raw_proxy.to

	@implements
	def one_of(self, expects: type[T_Raw]) -> T_Raw:
		"""期待する型と同種ならキャスト

		Args:
			expects (type[T_Ref]): 期待する型
		Returns:
			T_Raw: インスタンス
		Raises:
			LogicError: 継承関係が無い型を指定 XXX 出力する例外は要件等
		"""
		return self.__new_raw_proxy.one_of(expects)

	@override
	def __eq__(self, other: object) -> bool:
		"""比較演算子のオーバーロード

		Args:
			other (object): 比較対象
		Returns:
			bool: True = 同じ
		"""
		return self.__new_raw_proxy.__eq__(other)

	@override
	def __repr__(self) -> str:
		"""str: オブジェクトのシリアライズ表現"""
		return self.__new_raw_proxy.__repr__()


	@override
	def __str__(self) -> str:
		"""str: オブジェクトの文字列表現"""
		return self.__new_raw_proxy.__str__()


ImportOrigins: TypeAlias = Symbol | ReflectionVar
ClassOrigins: TypeAlias = Symbol | ReflectionImport
VarOrigins: TypeAlias = Symbol | ReflectionImpl
GenericOrigins: TypeAlias = Symbol | ReflectionImpl
RefOrigins: TypeAlias = Symbol | ReflectionImpl
LiteralOrigins: TypeAlias = ReflectionClass
ResultOrigins: TypeAlias = ReflectionClass


class SymbolWrapper(IWrapper):
	"""シンボルラッパーファクトリー"""

	def __init__(self, raw: IReflection) -> None:
		"""インスタンスを生成

		Args:
			raw (IReflection): シンボル
		"""
		self._raw = raw

	@implements
	def imports(self, via: defs.Import) -> IReflection:
		"""ラップしたシンボルを生成(インポートノード用)

		Args:
			via (Import): インポートノード
		Returns:
			IReflection: シンボル
		"""
		return ReflectionImport(self._raw.one_of(ImportOrigins), via)

	@implements
	def types(self, decl: defs.ClassDef) -> IReflection:
		"""ラップしたシンボルを生成(クラス定義ノード用)

		Args:
			decl (ClassDef): クラス定義ノード
		Returns:
			IReflection: シンボル
		"""
		return ReflectionClass(self._raw.one_of(ClassOrigins), decl)

	@implements
	def var(self, decl: defs.DeclAll) -> IReflection:
		"""ラップしたシンボルを生成(変数宣言ノード用)

		Args:
			decl (ClassDef): 変数宣言ノード
		Returns:
			IReflection: シンボル
		"""
		return ReflectionVar(self._raw.one_of(VarOrigins), decl)

	@implements
	def generic(self, via: defs.Type) -> IReflection:
		"""ラップしたシンボルを生成(タイプノード用)

		Args:
			via (Type): タイプノード
		Returns:
			IReflection: シンボル
		"""
		return ReflectionGeneric(self._raw.one_of(GenericOrigins), via)

	@implements
	def literal(self, via: defs.Literal | defs.Comprehension) -> IReflection:
		"""ラップしたシンボルを生成(リテラルノード用)

		Args:
			via (Literal | Comprehension): リテラル/リスト内包表記ノード
		Returns:
			IReflection: シンボル
		"""
		return ReflectionLiteral(self._raw.one_of(LiteralOrigins), via)

	@implements
	def ref(self, via: defs.Reference, context: IReflection | None = None) -> IReflection:
		"""ラップしたシンボルを生成(参照ノード用)

		Args:
			via (Reference): 参照系ノード
			context (IReflection | None): コンテキストのシンボル (default = None)
		Returns:
			IReflection: シンボル
		"""
		return ReflectionReference(self._raw.one_of(RefOrigins), via, context)

	@implements
	def result(self, via: defs.Operator) -> IReflection:
		"""ラップしたシンボルを生成(結果系ノード用)

		Args:
			via (Operator): 結果系ノード ※現状は演算ノードのみ
		Returns:
			IReflection: シンボル
		"""
		return ReflectionResult(self._raw.one_of(ResultOrigins), via)
