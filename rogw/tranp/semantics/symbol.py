from typing import Any, Callable, Iterator, Self, TypeAlias, TypeVar

from rogw.tranp.errors import FatalError, LogicError
from rogw.tranp.lang.implementation import implements, injectable, override
from rogw.tranp.semantics.reflected import DB, IReflection, IWrapper, Roles
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.semantics.naming import AliasHandler, ClassDomainNaming

T_Raw = TypeVar('T_Raw', bound='Reflection')

SymbolRaws: TypeAlias = DB['Reflection']


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
	def attrs(self) -> list['Reflection']:
		"""list[Reflection]: 属性シンボルリスト"""
		return []

	@property
	@implements
	def origin(self) -> 'Reflection | None':
		"""Reflection | None: スタックシンボル"""
		return None

	@property
	@implements
	def via(self) -> Node | None:
		"""Node | None: 参照元のノード"""
		return None

	@property
	@implements
	def context(self) -> 'Reflection':
		"""コンテキストを取得

		Returns:
			Reflection: コンテキストのシンボル
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
	def hierarchy(self) -> Iterator['Reflection']:
		"""参照元を辿るイテレーターを取得

		Returns:
			Iterator[Reflection]: イテレーター
		"""
		curr = self
		while curr:
			yield curr
			curr = curr.origin

	@implements
	def extends(self: Self, *attrs: 'Reflection') -> Self:
		"""シンボルが保有する型を拡張情報として属性に取り込む

		Args:
			*attrs (Reflection): 属性シンボルリスト
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
		self._attrs: list[Reflection] = []

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
	def attrs(self) -> list[Reflection]:
		"""属性シンボルリストを取得

		Returns:
			list[Reflection]: 属性シンボルリスト
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
	def origin(self) -> Reflection:
		"""Reflection: スタックシンボル"""
		return self._origin

	@property
	def _shared_origin(self) -> Reflection:
		"""シンボルテーブル上に存在する共有シンボルを取得

		Returns:
			Reflection: シンボルテーブル上に存在する共有されたシンボル
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
	def extends(self: Self, *attrs: Reflection) -> Self:
		"""シンボルが保持する型を拡張情報として属性に取り込む

		Args:
			*attrs (Reflection): 属性シンボルリスト
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
	def __init__(self, origin: 'RefOrigins', via: defs.Reference, context: Reflection | None = None) -> None:
		"""インスタンスを生成

		Args:
			origin (RefOrigins): スタックシンボル
			via (Reference): 参照元のノード
			context (Reflection | None): コンテキストのシンボル (default = None)
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
	def context(self) -> Reflection:
		"""コンテキストを取得

		Returns:
			Reflection: コンテキストのシンボル
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


class SymbolProxy:
	"""シンボルプロクシー
	* 拡張設定を遅延処理
	* 参照順序の自動的な解決
	* 不必要な拡張設定を省略

	Note:
		シンボルの登録順序と参照順序が重要なインスタンスに関して使用 ※現状はResolveUnknownでのみ使用
	"""

	def __init__(self, org_raw: Reflection, extender: Callable[[], Reflection]) -> None:
		"""インスタンスを生成

		Args:
			org_raw (Reflection): オリジナル
			extender (Callable[[], Reflection]): シンボル拡張設定ファクトリー
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


ImportOrigins: TypeAlias = Symbol | ReflectionVar
ClassOrigins: TypeAlias = Symbol | ReflectionImport
VarOrigins: TypeAlias = Symbol | ReflectionImpl
GenericOrigins: TypeAlias = Symbol | ReflectionImpl
RefOrigins: TypeAlias = Symbol | ReflectionImpl
LiteralOrigins: TypeAlias = ReflectionClass
ResultOrigins: TypeAlias = ReflectionClass


class SymbolWrapper(IWrapper):
	"""シンボルラッパーファクトリー"""

	def __init__(self, raw: Reflection) -> None:
		"""インスタンスを生成

		Args:
			raw (Reflection): シンボル
		"""
		self._raw = raw

	def imports(self, via: defs.Import) -> ReflectionImport:
		"""ラップしたシンボルを生成(インポートノード用)

		Args:
			via (Import): インポートノード
		Returns:
			SymbolImport: シンボル
		"""
		return ReflectionImport(self._raw.one_of(ImportOrigins), via)

	def types(self, decl: defs.ClassDef) -> ReflectionClass:
		"""ラップしたシンボルを生成(クラス定義ノード用)

		Args:
			decl (ClassDef): クラス定義ノード
		Returns:
			SymbolClass: シンボル
		"""
		return ReflectionClass(self._raw.one_of(ClassOrigins), decl)

	def var(self, decl: defs.DeclAll) -> ReflectionVar:
		"""ラップしたシンボルを生成(変数宣言ノード用)

		Args:
			decl (ClassDef): 変数宣言ノード
		Returns:
			SymbolVar: シンボル
		"""
		return ReflectionVar(self._raw.one_of(VarOrigins), decl)

	def generic(self, via: defs.Type) -> ReflectionGeneric:
		"""ラップしたシンボルを生成(タイプノード用)

		Args:
			via (Type): タイプノード
		Returns:
			SymbolGeneric: シンボル
		"""
		return ReflectionGeneric(self._raw.one_of(GenericOrigins), via)

	def literal(self, via: defs.Literal | defs.Comprehension) -> ReflectionLiteral:
		"""ラップしたシンボルを生成(リテラルノード用)

		Args:
			via (Literal | Comprehension): リテラル/リスト内包表記ノード
		Returns:
			SymbolLiteral: シンボル
		"""
		return ReflectionLiteral(self._raw.one_of(LiteralOrigins), via)

	def ref(self, via: defs.Reference, context: Reflection | None = None) -> ReflectionReference:
		"""ラップしたシンボルを生成(参照ノード用)

		Args:
			via (Reference): 参照系ノード
			context (Reflection | None): コンテキストのシンボル (default = None)
		Returns:
			SymbolReference: シンボル
		"""
		return ReflectionReference(self._raw.one_of(RefOrigins), via, context)

	def result(self, via: defs.Operator) -> ReflectionResult:
		"""ラップしたシンボルを生成(結果系ノード用)

		Args:
			via (Operator): 結果系ノード ※現状は演算ノードのみ
		Returns:
			SymbolResult: シンボル
		"""
		return ReflectionResult(self._raw.one_of(ResultOrigins), via)


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
