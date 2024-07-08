from typing import Any, Iterator, Self

from rogw.tranp.errors import FatalError, LogicError
from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.semantics.reflection.helper.naming import ClassShorthandNaming
from rogw.tranp.semantics.reflection.interface import IReflection, IWrapper, Roles, SymbolDB, T_Ref
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node


class ReflectionBase(IReflection):
	"""リフレクション(基底)"""

	def __init__(self, db: SymbolDB | None) -> None:
		"""インスタンスを生成

		Args:
			db (SymbolDB | None): シンボルテーブル
		"""
		self.__db = db

	@property
	@implements
	def _db(self) -> SymbolDB:
		"""SymbolDB: 所属するシンボルテーブル"""
		if self.__db is not None:
			return self.__db

		raise FatalError(f'Unreachable code.')

	@implements
	def set_db(self, db: SymbolDB) -> None:
		"""所属するシンボルテーブルを設定

		Args:
			db (SymbolDB): シンボルテーブル
		"""
		self.__db = db

	@property
	@implements
	def _actual_addr(self) -> int:
		"""実体のアドレス(ID)を取得

		Returns:
			int: アドレス(ID)
		Note:
			* XXX このメソッドはSymbolProxyによる無限ループを防ぐ目的で実装 @seeを参照
			* XXX 上記以外の目的で使用することは無い
			@see semantics.reflection.implements.Reflection._shared_origin
		"""
		return id(self)

	# @property
	# @implements
	# def ref_fullyname(self) -> str:
	# 	"""str: 完全参照名"""
	# 	return ''

	# @property
	# @implements
	# def org_fullyname(self) -> str:
	# 	"""str: 完全参照名(オリジナル)"""
	# 	return ''

	# @property
	# @abstractmethod
	# def types(self) -> defs.ClassDef:
	# 	"""ClassDef: クラス定義ノード"""
	# 	...

	# @property
	# @abstractmethod
	# def decl(self) -> defs.DeclAll:
	# 	"""DeclAll: クラス/変数宣言ノード"""
	# 	...

	# @property
	# @abstractmethod
	# def role(self) -> Roles:
	# 	"""Roles: シンボルの役割"""
	# 	...

	@property
	@implements
	def attrs(self) -> list[IReflection]:
		"""list[IReflection]: 属性シンボルリスト"""
		return []

	@property
	@implements
	def origin(self) -> IReflection:
		"""スタックシンボルを取得

		Returns:
			IReflection: スタックシンボル
		Raises:
			LogicError: roleがOriginのインスタンスで使用
		"""
		raise LogicError(f'Origin is null. symbol: {str(self)}, fullyname: {self.ref_fullyname}')

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

	# @abstractmethod
	# def clone(self: Self) -> Self:
	# 	"""インスタンスを複製

	# 	Returns:
	# 		Self: 複製したインスタンス
	# 	"""
	# 	...

	def _clone(self: Self, **kwargs: Any) -> Self:
		"""インスタンスを複製

		Args:
			**kwargs (Any): コンストラクターの引数
		Returns:
			Self: 複製したインスタンス
		"""
		new = self.__class__(**kwargs)
		# XXX 念のため明示的にコピー
		if self.__db and new.__db is None:
			new.__db = self.__db

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
			curr = curr.origin if curr.role != Roles.Origin else None

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
	def to(self) -> IWrapper:
		"""ラッパーファクトリーを生成

		Returns:
			IWrapper: ラッパーファクトリー
		"""
		return SymbolWrapper(self)

	@implements
	def one_of(self, *expects: type[T_Ref]) -> T_Ref:
		"""期待する型と同種ならキャスト

		Args:
			*expects (type[T_Ref]): 期待する型
		Returns:
			T_Ref: インスタンス
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


class Symbol(ReflectionBase):
	"""シンボル(クラス定義のオリジナル)"""

	def __init__(self, types: defs.ClassDef) -> None:
		"""インスタンスを生成

		Args:
			types (ClassDef): クラス定義ノード
		"""
		super().__init__(db=None)
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


class Reflection(ReflectionBase):
	"""リフレクションの共通実装(基底)"""

	def __init__(self, origin: 'Symbol | Reflection') -> None:
		"""インスタンスを生成

		Args:
			origin (Symbol | Reflection): スタックシンボル
		"""
		super().__init__(origin._db)
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
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return self._origin.role

	@property
	@override
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
		if self._origin.org_fullyname in self._db:
			origin = self._db[self._origin.org_fullyname]
			# XXX 実体のアドレス同士で比較することで無限ループを防止
			if origin._actual_addr != self._actual_addr:
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
		if self._attrs:
			raise LogicError(f'Already set attibutes. symbol: {self.types.fullyname}')
		
		self._attrs = list(attrs)
		return self


class Class(Reflection):
	"""シンボル(クラス)"""

	def __init__(self, origin: Symbol) -> None:
		"""インスタンスを生成

		Args:
			origin (Symbol): スタックシンボル
		"""
		super().__init__(origin)

	@property
	@override
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Class


class Var(Reflection):
	"""シンボル(変数)"""

	def __init__(self, origin: Reflection, decl: defs.DeclVars) -> None:
		"""インスタンスを生成

		Args:
			origin (Reflection): スタックシンボル
			decl (DeclVars): 変数宣言ノード
		"""
		super().__init__(origin)
		self._decl = decl

	@property
	@override
	def decl(self) -> defs.DeclVars:
		"""DeclVars: 変数宣言ノード"""
		return self._decl

	@property
	@override
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


class Import(Reflection):
	"""シンボル(インポート)"""

	def __init__(self, origin: Class | Var, via: defs.ImportAsName) -> None:
		"""インスタンスを生成

		Args:
			origin (Class | Var): スタックシンボル
			via (ImportAsName): 参照元のノード
		"""
		super().__init__(origin)
		self._via = via

	@property
	@override
	def ref_fullyname(self) -> str:
		"""str: 完全参照名"""
		return self._via.fullyname

	@property
	@override
	def via(self) -> defs.ImportAsName:
		"""Import: 参照元のノード"""
		return self._via

	@override
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via)


class Extend(Reflection):
	"""シンボル(タイプ拡張)"""

	def __init__(self, origin: Class | Import | Var, via: defs.Type) -> None:
		"""インスタンスを生成

		Args:
			origin (Class | Import | Var): スタックシンボル
			via (Type): 参照元のノード
		"""
		super().__init__(origin)
		self._via = via

	@property
	@override
	def via(self) -> defs.Type:
		"""Type: 参照元のノード"""
		return self._via

	@override
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via)


class Proxy(Reflection):
	"""シンボル(タイプ擬態)"""

	def __init__(self, origin: Class | Import, via: defs.Reference) -> None:
		"""インスタンスを生成

		Args:
			origin (Class | Import): スタックシンボル
			via (Reference): 参照元のノード
		"""
		super().__init__(origin)
		self._via = via

	@property
	@override
	def via(self) -> defs.Reference:
		"""Type: 参照元のノード"""
		return self._via

	@override
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via)


class Temporary(Reflection):
	"""シンボル(テンポラリー)"""

	def __init__(self, origin: 'Class | Extend | Context', via: defs.Literal | defs.Comprehension | defs.Operator) -> None:
		"""インスタンスを生成

		Args:
			origin (Class | Extend | Context): スタックシンボル
			via (Literal | Comprehension | Operator): テンポラリー系ノード
		"""
		super().__init__(origin)
		self._via = via

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


class Context(Reflection):
	"""シンボル(コンテキスト)"""

	def __init__(self, origin: Reflection, via: defs.Relay | defs.Indexer | defs.FuncCall, context: IReflection) -> None:
		"""インスタンスを生成

		Args:
			origin (Reflection): スタックシンボル
			via (defs.Relay | defs.Indexer | defs.FuncCall): 参照元のノード
			context (IReflection): コンテキストのシンボル
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
	@override
	def context(self) -> IReflection:
		"""コンテキストを取得

		Returns:
			IReflection: コンテキストのシンボル
		Raises:
			LogicError: コンテキストが無いシンボルで使用
		"""
		return self._context

	@override
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via, context=self._context)


class SymbolWrapper(IWrapper):
	"""シンボルラッパーファクトリー"""

	def __init__(self, raw: IReflection) -> None:
		"""インスタンスを生成

		Args:
			raw (IReflection): シンボル
		"""
		self._raw = raw

	@implements
	def types(self) -> IReflection:
		"""ラップしたシンボルを生成(クラス)

		Returns:
			IReflection: シンボル
		"""
		return Class(self._raw.one_of(Symbol))

	@implements
	def imports(self, via: defs.ImportAsName) -> IReflection:
		"""ラップしたシンボルを生成(インポート)

		Args:
			via (ImportAsName): インポート名ノード
		Returns:
			IReflection: シンボル
		"""
		# XXX indexファイルの場合、必然的に多重importになるためImportはそのまま返却
		if isinstance(self._raw, Import):
			return self._raw

		return Import(self._raw.one_of(Class, Var), via)

	@implements
	def var(self, decl: defs.DeclVars) -> IReflection:
		"""ラップしたシンボルを生成(変数)

		Args:
			decl (DeclVars): 変数宣言ノード
		Returns:
			IReflection: シンボル
		"""
		return Var(self._raw.one_of(Reflection), decl)

	@implements
	def proxy(self, via: defs.Reference) -> IReflection:
		"""ラップしたシンボルを生成(タイプ擬態)

		Args:
			via (Reference): 参照系ノード
		Returns:
			IReflection: シンボル
		"""
		return Proxy(self._raw.one_of(Class, Import), via)

	@implements
	def generic(self, via: defs.Type) -> IReflection:
		"""ラップしたシンボルを生成(タイプ拡張)

		Args:
			via (Type): タイプノード
		Returns:
			IReflection: シンボル
		"""
		return Extend(self._raw.one_of(Class, Import, Var), via)

	@implements
	def literal(self, via: defs.Literal) -> IReflection:
		"""ラップしたシンボルを生成(リテラル)

		Args:
			via (Literal): リテラルノード
		Returns:
			IReflection: シンボル
		"""
		return Temporary(self._raw.one_of(Class), via)

	@implements
	def result(self, via: defs.Operator | defs.Comprehension) -> IReflection:
		"""ラップしたシンボルを生成(結果)

		Args:
			via (Operator | Comprehension): 結果系ノード 演算/リスト内包表記ノードのみ
		Returns:
			IReflection: シンボル
		Note:
			FIXME 「結果」と言う目的から考え得るコンテキストは無数に存在するため、self._rawの型制限は実質的に意味を成さず、
			FIXME 現状テストでエラーが出ないのは、単にテストケースが不足しているだけだと考えられる
		"""
		return Temporary(self._raw.one_of(Class, Extend, Context), via)

	@implements
	def relay(self, via: defs.Relay | defs.Indexer | defs.FuncCall, context: IReflection) -> IReflection:
		"""ラップしたシンボルを生成(参照リレー)

		Args:
			via (Relay | Indexer | FuncCall): 参照系ノード
			context (IReflection): コンテキストのシンボル
		Returns:
			IReflection: シンボル
		"""
		return Context(self._raw.one_of(Reflection), via, context)
