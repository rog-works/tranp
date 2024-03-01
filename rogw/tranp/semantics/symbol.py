from typing import Any, Callable, Iterator, Self, TypeAlias, TypeVar

from rogw.tranp.errors import FatalError, LogicError
from rogw.tranp.lang.implementation import implements, injectable, override
from rogw.tranp.semantics.reflected import Container, IReflection, IWrapper, Roles, T_Raw
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.semantics.naming import AliasHandler, ClassDomainNaming

T_Sym = TypeVar('T_Sym', bound='Symbol')


class SymbolProxy:
	"""シンボルプロクシー
	* 拡張設定を遅延処理
	* 参照順序の自動的な解決
	* 不必要な拡張設定を省略

	Note:
		シンボルの登録順序と参照順序が重要なインスタンスに関して使用 ※現状はResolveUnknownでのみ使用
	"""

	def __init__(self, org_raw: 'SymbolRaw', extender: Callable[[], 'SymbolRaw']) -> None:
		"""インスタンスを生成

		Args:
			org_raw (SymbolRaw): オリジナル
			extender (Callable[[], SymbolRaw]): シンボル拡張設定ファクトリー
		"""
		super().__setattr__('org_raw', org_raw)
		super().__setattr__('extender', extender)
		super().__setattr__('new_raw', None)

	@override
	def __getattr__(self, key: str) -> Any:
		"""属性を取得

		Args:
			key (str): 属性のキー
		Returns:
			Any: 属性の値
		"""
		if key in ['set_raws', '_raws']:
			return getattr(self.org_raw, key)

		if self.new_raw is None:
			super().__setattr__('new_raw', self.extender())

		return getattr(self.new_raw, key)

	@override
	def __setattr__(self, key: str, value: Any) -> None:
		"""属性を設定

		Args:
			key (str): 属性のキー
			value (Any): 属性の値
		"""
		if key in ['set_raws', '_raws']:
			setattr(self.org_raw, key, value)

		if self.new_raw is None:
			super().__setattr__('new_raw', self.extender())

		setattr(self.new_raw, key, value)

	@override
	def __eq__(self, other: object) -> bool:
		"""比較演算子のオーバーロード

		Args:
			other (object): 比較対象
		Returns:
			bool: True = 同じ
		"""
		if self.new_raw is None:
			super().__setattr__('new_raw', self.extender())

		return self.new_raw == other

	@override
	def __repr__(self) -> str:
		"""str: オブジェクトのシリアライズ表現"""
		if self.new_raw is None:
			super().__setattr__('new_raw', self.extender())

		return self.new_raw.__repr__()


	@override
	def __str__(self) -> str:
		"""str: オブジェクトの文字列表現"""
		if self.new_raw is None:
			super().__setattr__('new_raw', self.extender())

		return self.new_raw.__str__()


class SymbolRaws(Container[T_Raw]):
	"""シンボルテーブル"""

	@classmethod
	@override
	def new(cls, *raws: Self | dict[str, T_Raw]) -> Self:
		"""シンボルテーブルを結合した新たなインスタンスを生成

		Args:
			*raws (Self | dict[str, T_Raw]): シンボルテーブルリスト
		Returns:
			Self: 生成したインスタンス
		"""
		return cls().merge(*raws)

	@override
	def merge(self, *raws: Self | dict[str, T_Raw]) -> Self:
		"""指定のシンボルテーブルと結合

		Args:
			*raws (Self | dict[str, T_Raw]): シンボルテーブルリスト
		Returns:
			Self: 自己参照
		"""
		for in_raws in raws:
			self.update(**in_raws)

		for raw in self.values():
			raw.set_raws(self)

		return self

	@override
	def __setitem__(self, key: str, raw: T_Raw) -> None:
		"""配列要素設定のオーバーロード

		Args:
			key (str): 要素名
			raw (T_Raw): シンボル
		"""
		raw.set_raws(self)
		super().__setitem__(key, raw)


class SymbolRaw(IReflection):
	"""シンボル"""

	@injectable
	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__raws: Container | None = None

	@property
	@implements
	def _raws(self) -> Container:
		"""Container: 所属するシンボルテーブル"""
		if self.__raws is not None:
			return self.__raws

		raise FatalError(f'Unreachable code.')

	@implements
	def set_raws(self, raws: Container) -> None:
		"""所属するシンボルテーブルを設定

		Args:
			raws (Container): シンボルテーブル
		"""
		self.__raws = raws

	@property
	@implements
	def origin(self) -> IReflection | None:
		"""SymbolRaw | None: スタックシンボル"""
		return None

	@property
	@implements
	def via(self) -> Node | None:
		"""Node | None: 参照元のノード"""
		return None

	@property
	@implements
	def context(self) -> IReflection:
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
			**kwargs (Any): コンストラクター
		Returns:
			Self: 複製したインスタンス
		"""
		new = self.__class__(**kwargs)
		new.__raws = self.__raws
		if self.attrs:
			return new.extends(*[attr.clone() for attr in self.attrs])

		return new

	@property
	@implements
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		return ClassShorthandNaming.domain_name(self)

	@implements
	def hierarchy(self) -> Iterator[IReflection]:
		"""参照元を辿るイテレーターを取得

		Returns:
			Iterator[IReflection]: イテレーター
		"""
		curr = self
		while curr:
			yield curr
			curr = curr.origin

	@implements
	def extends(self: Self, *attrs: IReflection) -> Self:
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
			LogidError: 継承関係が無い型を指定 XXX 出力する例外は要件等
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


class SymbolOrigin(SymbolRaw):
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

	@property
	@implements
	def attrs(self) -> list[IReflection]:
		"""list[IReflection]: 属性シンボルリスト"""
		return []

	@implements
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(types=self.types)


class Symbol(SymbolRaw):
	"""シンボル(基底)"""

	def __init__(self, origin: 'SymbolOrigin | Symbol') -> None:
		"""インスタンスを生成

		Args:
			origin (SymbolOrigin | Symbol): スタックシンボル
		"""
		super().__init__()
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
		if isinstance(self, SymbolReference):
			raise LogicError(f'Not allowd extends. symbol: {self.types.fullyname}')

		if self._attrs:
			raise LogicError(f'Already set attibutes. symbol: {self.types.fullyname}')
		
		self._attrs = list(attrs)
		return self


class SymbolImport(Symbol):
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


class SymbolClass(Symbol):
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


class SymbolVar(Symbol):
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


class SymbolGeneric(Symbol):
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


class SymbolLiteral(Symbol):
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


class SymbolReference(Symbol):
	def __init__(self, origin: 'RefOrigins', via: defs.Reference, context: SymbolRaw | None = None) -> None:
		"""インスタンスを生成

		Args:
			origin (RefOrigins): スタックシンボル
			via (Reference): 参照元のノード
			context (SymbolRaw | None): コンテキストのシンボル (default = None)
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
	def context(self) -> SymbolRaw:
		"""コンテキストを取得

		Returns:
			SymbolRaw: コンテキストのシンボル
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


class SymbolResult(Symbol):
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


ImportOrigins: TypeAlias = SymbolOrigin | SymbolVar
ClassOrigins: TypeAlias = SymbolOrigin | SymbolImport
VarOrigins: TypeAlias = SymbolOrigin | Symbol
GenericOrigins: TypeAlias = SymbolOrigin | Symbol
RefOrigins: TypeAlias = SymbolOrigin | Symbol
LiteralOrigins: TypeAlias = SymbolClass
ResultOrigins: TypeAlias = SymbolClass


class SymbolWrapper(IWrapper):
	"""シンボルラッパーファクトリー"""

	def __init__(self, raw: SymbolRaw) -> None:
		"""インスタンスを生成

		Args:
			raw (SymbolRaw): シンボル
		"""
		self._raw = raw

	def imports(self, via: defs.Import) -> SymbolImport:
		"""ラップしたシンボルを生成(インポートノード用)

		Args:
			via (Import): インポートノード
		Returns:
			SymbolImport: シンボル
		"""
		return SymbolImport(self._raw.one_of(ImportOrigins), via)

	def types(self, decl: defs.ClassDef) -> SymbolClass:
		"""ラップしたシンボルを生成(クラス定義ノード用)

		Args:
			decl (ClassDef): クラス定義ノード
		Returns:
			SymbolClass: シンボル
		"""
		return SymbolClass(self._raw.one_of(ClassOrigins), decl)

	def var(self, decl: defs.DeclAll) -> SymbolVar:
		"""ラップしたシンボルを生成(変数宣言ノード用)

		Args:
			decl (ClassDef): 変数宣言ノード
		Returns:
			SymbolVar: シンボル
		"""
		return SymbolVar(self._raw.one_of(VarOrigins), decl)

	def generic(self, via: defs.Type) -> SymbolGeneric:
		"""ラップしたシンボルを生成(タイプノード用)

		Args:
			via (Type): タイプノード
		Returns:
			SymbolGeneric: シンボル
		"""
		return SymbolGeneric(self._raw.one_of(GenericOrigins), via)

	def literal(self, via: defs.Literal | defs.Comprehension) -> SymbolLiteral:
		"""ラップしたシンボルを生成(リテラルノード用)

		Args:
			via (Literal | Comprehension): リテラル/リスト内包表記ノード
		Returns:
			SymbolLiteral: シンボル
		"""
		return SymbolLiteral(self._raw.one_of(LiteralOrigins), via)

	def ref(self, via: defs.Reference, context: SymbolRaw | None = None) -> SymbolReference:
		"""ラップしたシンボルを生成(参照ノード用)

		Args:
			via (Reference): 参照系ノード
			context (SymbolRaw | None): コンテキストのシンボル (default = None)
		Returns:
			SymbolReference: シンボル
		"""
		return SymbolReference(self._raw.one_of(RefOrigins), via, context)

	def result(self, via: defs.Operator) -> SymbolResult:
		"""ラップしたシンボルを生成(結果系ノード用)

		Args:
			via (Operator): 結果系ノード ※現状は演算ノードのみ
		Returns:
			SymbolResult: シンボル
		"""
		return SymbolResult(self._raw.one_of(ResultOrigins), via)


class ClassShorthandNaming:
	"""クラスの短縮表記生成モジュール

	Note:
		# 書式
		* types=AltClass: ${alias}=${actual}
		* types=Function: ${domain_name}(...${arguments}) -> ${return}
		* role=Var/Generic/Literal/Reference: ${domain_name}<...${attributes}>
		* その他: ${domain_name}
	"""

	@classmethod
	def domain_name(cls, raw: IReflection, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの短縮表記を生成(ドメイン名)

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 短縮表記
		"""
		return cls.__make_impl(raw, alias_handler, 'domain')

	@classmethod
	def fullyname(cls, raw: IReflection, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの短縮表記を生成(完全参照名)

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 短縮表記
		"""
		return cls.__make_impl(raw, alias_handler, 'fully')

	@classmethod
	def accessible_name(cls, raw: IReflection, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの短縮表記を生成(名前空間上の参照名)

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 短縮表記
		"""
		return cls.__make_impl(raw, alias_handler, 'accessible')

	@classmethod
	def __make_impl(cls, raw: IReflection, alias_handler: AliasHandler | None = None, path_method: str = 'domain') -> str:
		"""クラスの短縮表記を生成

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
			path_method ('domain' | 'fully' | 'namespace'): パス生成方式 (default = 'domain') @see analyze.naming.ClassDomainNaming
		Returns:
			str: 短縮表記
		"""
		symbol_name = ClassDomainNaming.make_manualy(raw.types, alias_handler, path_method)
		if len(raw.attrs) > 0:
			if raw.types.is_a(defs.AltClass):
				attrs = [cls.__make_impl(attr, alias_handler, path_method) for attr in raw.attrs]
				return f'{symbol_name}={attrs[0]}'
			elif raw.types.is_a(defs.Function):
				attrs = [cls.__make_impl(attr, alias_handler, path_method) for attr in raw.attrs]
				return f'{symbol_name}({", ".join(attrs[:-1])}) -> {attrs[-1]}'
			elif raw.role in [Roles.Var, Roles.Generic, Roles.Literal, Roles.Reference]:
				attrs = [cls.__make_impl(attr, alias_handler, path_method) for attr in raw.attrs]
				return f'{symbol_name}<{", ".join(attrs)}>'

		return symbol_name
