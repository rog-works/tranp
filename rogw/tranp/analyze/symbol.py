from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, Iterator, TypeAlias, TypeVar, cast

from rogw.tranp.errors import LogicError
from rogw.tranp.lang.implementation import implements, injectable, override
import rogw.tranp.node.definition as defs
from rogw.tranp.node.node import Node

T_Raw = TypeVar('T_Raw', bound='SymbolRaw')
T_Sym = TypeVar('T_Sym', bound='Symbol')

ImportOrigins: TypeAlias = 'SymbolOrigin | SymbolVar'
ClassOrigins: TypeAlias = 'SymbolOrigin | SymbolImport'
VarOrigins: TypeAlias = 'SymbolOrigin | SymbolImport | SymbolClass | SymbolVar | SymbolGeneric | SymbolLiteral | SymbolReference'
GenericOrigins: TypeAlias = 'SymbolOrigin | SymbolImport | SymbolClass | SymbolVar | SymbolGeneric'
RefOrigins: TypeAlias = 'SymbolOrigin | SymbolImport | SymbolClass | SymbolVar | SymbolGeneric | SymbolLiteral'
LiteralOrigins: TypeAlias = 'SymbolClass'


class Roles(Enum):
	"""シンボルの役割

	Attributes:
		Origin: 定義元。クラス定義ノードが対象。属性は保有しない
		Import: Originの複製。属性は保有しない
		Class: クラス定義ノードが対象。クラスはGeneric型、ファンクションは関数シグネチャーを属性として保有
		Var: 変数宣言ノードが対象。Generic型の属性を保有
		Generic: タイプノードが対象。Generic型の属性を保有
		Literal: リテラルノードが対象。Generic型の属性を保有
		Reference: 参照系ノードが対象。属性は保有しない
	"""
	Origin = 'Origin'
	Import = 'Import'
	Class = 'Class'
	Var = 'Var'
	Generic = 'Generic'
	Literal = 'Literal'
	Reference = 'Reference'

	@property
	def has_entity(self) -> bool:
		"""bool: True = 実体を持つ"""
		return self in [Roles.Origin, Roles.Class, Roles.Var, Roles.Generic, Roles.Literal]


class SymbolRaws(dict[str, T_Raw]):
	"""シンボルテーブル"""

	@override
	def __setitem__(self, key: str, raw: T_Raw) -> None:
		"""配列要素設定のオーバーロード

		Args:
			key (str): 要素名
			raw (T_Raw): シンボル
		"""
		raw.set_raws(self)
		super().__setitem__(key, raw)

	@classmethod
	def new(cls, *raws: 'SymbolRaws | dict[str, T_Raw]') -> 'SymbolRaws':
		"""シンボルテーブルを結合した新たなインスタンスを生成

		Args:
			*raws (SymbolRaws | dict[str, SymbolRaw]): シンボルテーブルリスト
		Returns:
			SymbolRaws: 生成したインスタンス
		"""
		return cls().merge(*raws)

	def merge(self, *raws: 'SymbolRaws | dict[str, T_Raw]') -> 'SymbolRaws':
		"""指定のシンボルテーブルと結合

		Args:
			*raws (SymbolRaws | dict[str, SymbolRaw]): シンボルテーブルリスト
		Returns:
			SymbolRaws: 自己参照
		"""
		for in_raws in raws:
			self.update(**in_raws)

		for raw in self.values():
			raw.set_raws(self)

		return self


class SymbolRaw(metaclass=ABCMeta):
	"""シンボル

	Attributes:
		ref_fullyname (str): 完全参照名
		org_fullyname (str): 完全参照名(オリジナル)
		types (ClassDef): クラス定義ノード
		decl (DeclAll): クラス/変数宣言ノード
		role (Roles): シンボルの役割
		attrs (list[SymbolRaw]): 属性シンボルリスト
		origin (SymbolRaw | None): スタックシンボル (default = None)
		via (Node | None): 参照元のノード (default = None)
		context (SymbolRaw| None): コンテキストのシンボル (default = None)
	Note:
		# contextのユースケース
		* Relay/Indexerのreceiverを設定。on_func_call等で実行時型の補完に使用
	"""

	@property
	@abstractmethod
	def _raws(self) -> SymbolRaws:
		"""SymbolRaws: 所属するシンボルテーブル"""
		...

	@abstractmethod
	def set_raws(self, raws: SymbolRaws) -> None:
		"""所属するシンボルテーブルを設定

		Args:
			raws (SymbolRaws): シンボルテーブル
		"""
		...

	@property
	@abstractmethod
	def ref_fullyname(self) -> str:
		"""str: 完全参照名"""
		...

	@property
	@abstractmethod
	def org_fullyname(self) -> str:
		"""str: 完全参照名(オリジナル)"""
		...

	@property
	@abstractmethod
	def types(self) -> defs.ClassDef:
		"""ClassDef: クラス定義ノード"""
		...

	@property
	@abstractmethod
	def decl(self) -> defs.DeclAll:
		"""DeclAll: クラス/変数宣言ノード"""
		...

	@property
	@abstractmethod
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		...

	@property
	@abstractmethod
	def attrs(self) -> list['SymbolRaw']:
		"""list[SymbolRaw]: 属性シンボルリスト"""
		...

	@property
	def origin(self) -> 'SymbolRaw | None':
		"""SymbolRaw | None: スタックシンボル"""
		return None

	@property
	def via(self) -> Node | None:
		"""Node | None: 参照元のノード"""
		return None

	@property
	def context(self) -> 'SymbolRaw':
		"""コンテキストを取得

		Returns:
			SymbolRaw: コンテキストのシンボル
		Raises:
			LogicError: コンテキストが無いシンボルで使用
		"""
		raise LogicError(f'Context is null. symbol: {str(self)}, fullyname: {self.ref_fullyname}')

	@abstractmethod
	def clone(self: T_Raw) -> T_Raw:
		"""インスタンスを複製

		Returns:
			T_Raw: 複製したインスタンス
		"""
		...

	def _clone(self: T_Raw, **kwargs: Any) -> T_Raw:
		"""インスタンスを複製

		Args:
			**kwargs (Any): コンストラクター
		Returns:
			T_Raw: 複製したインスタンス
		"""
		new = self.__class__(**kwargs)
		return new.extends(*[attr.clone() for attr in self.attrs])

	@property	
	def has_entity(self) -> bool:
		"""bool: True = 実体を持つ"""
		return self.role.has_entity

	@override
	def __eq__(self, other: object) -> bool:
		"""比較演算子のオーバーロード

		Args:
			other (object): 比較対象
		Returns:
			bool: True = 同じ
		Raises:
			ValueError: Node以外のオブジェクトを指定
		"""
		if other is None:
			return False

		if not isinstance(other, SymbolRaw):
			raise ValueError(f'Not allowed comparison. other: {type(other)}')

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

	@property
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		return self.make_shorthand()

	def make_shorthand(self, use_alias: bool = False) -> str:
		"""オブジェクトの短縮表記を生成

		Args:
			use_alias (bool): True = エイリアスの名前を優先(default = False)
		Returns:
			str: 短縮表記
		Note:
			# 書式
			* types=AltClass: ${alias}=${actual}
			* types=Function: ${domain_name}(...${arguments}) -> ${return}
			* role=Origin: ${domain_name}
			* その他: ${domain_name}<...${attributes}>
		"""
		domain_name = self.types.domain_name
		domain_name = self.types.alias_symbol or domain_name if use_alias else domain_name
		if len(self.attrs) > 0:
			if self.types.is_a(defs.AltClass):
				attrs = [str(attr) for attr in self.attrs]
				return f'{domain_name}={attrs[0]}'
			elif self.types.is_a(defs.Function):
				attrs = [str(attr) for attr in self.attrs]
				return f'{domain_name}({", ".join(attrs[:-1])}) -> {attrs[-1]}'
			elif self.role in [Roles.Var, Roles.Generic, Roles.Literal, Roles.Reference]:
				attrs = [str(attr) for attr in self.attrs]
				return f'{domain_name}<{", ".join(attrs)}>'

		return domain_name
	
	def each_via(self) -> Iterator[Node]:
		"""参照元を辿るイテレーターを取得

		Returns:
			Iterator[Node]: イテレーター
		"""
		curr = self
		while curr:
			# XXX whileの判定が反映されずに警告されるためcastで対処
			yield cast(Node, curr.via)
			curr = curr.origin

	def extends(self, *attrs: 'SymbolRaw') -> 'SymbolRaw':
		"""シンボルが保持する型を拡張情報として属性に取り込む

		Args:
			*attrs (SymbolRaw): 属性シンボルリスト
		Returns:
			SymbolRaw: インスタンス
		Raises:
			LogicError: 実体の無いインスタンスに実行
			LogicError: 拡張済みのインスタンスに再度実行
		"""
		raise LogicError(f'Not allowd extends. symbol: {self.types.fullyname}')

	@property
	def to(self) -> 'SymbolWrapper':  # XXX 前方参照
		"""シンボルラッパーを生成

		Returns:
			SymbolWrapper: シンボルラッパー
		"""
		return SymbolWrapper(self)

	def as_a(self, expect: type[T_Raw]) -> T_Raw:
		"""期待する型と同種ならキャスト

		Args:
			expect (type[T_Raw]): 期待する型
		Returns:
			T_Raw: インスタンス
		Raises:
			LogidError: 継承関係が無い型を指定
		"""
		if isinstance(self, expect):
			return self

		raise LogicError(f'Not allowed conversion. self: {str(self)}, from: {self.__class__.__name__}, to: {expect.__name__}')

	def one_of(self, expects: type[T_Raw]) -> T_Raw:
		"""期待する型と同種ならキャスト

		Args:
			expects (type[T_Raw]): 期待する型
		Returns:
			T_Raw: インスタンス
		Raises:
			LogidError: 継承関係が無い型を指定
		"""
		if isinstance(self, expects):
			return self

		raise LogicError(f'Not allowed conversion. self: {str(self)}, from: {self.__class__.__name__}, to: {expects}')


class SymbolOrigin(SymbolRaw):
	"""シンボル(クラス定義のオリジナル)"""

	@injectable
	def __init__(self, types: defs.ClassDef) -> None:
		"""インスタンスを生成

		Args:
			types (ClassDef): クラス定義ノード
		"""
		self.__raws: SymbolRaws | None = None
		self._types = types

	@property
	@implements
	def _raws(self) -> SymbolRaws:
		"""SymbolRaws: 所属するシンボルテーブル"""
		if self.__raws is not None:
			return self.__raws

		raise LogicError(f'Unreachable code.')

	@implements
	def set_raws(self, raws: SymbolRaws) -> None:
		"""所属するシンボルテーブルを設定

		Args:
			raws (SymbolRaws): シンボルテーブル
		"""
		self.__raws = raws

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
	def attrs(self) -> list['SymbolRaw']:
		"""list[SymbolRaw]: 属性シンボルリスト"""
		return []

	@implements
	def clone(self: T_Raw) -> T_Raw:
		"""インスタンスを複製

		Returns:
			T_Raw: 複製したインスタンス
		"""
		return self._clone(types=self.types)


class Symbol(SymbolRaw):
	"""シンボル(基底)"""

	def __init__(self, origin: 'SymbolOrigin | Symbol') -> None:
		"""インスタンスを生成"""
		super().__init__()
		self.__raws = origin._raws
		self._origin = origin
		self._attrs: list[SymbolRaw] = []

	@property
	@implements
	def _raws(self) -> SymbolRaws:
		"""SymbolRaws: 所属するシンボルテーブル"""
		return self.__raws

	@implements
	def set_raws(self, raws: SymbolRaws) -> None:
		"""所属するシンボルテーブルを設定

		Args:
			raws (SymbolRaws): シンボルテーブル
		"""
		self.__raws = raws

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
	def attrs(self) -> list['SymbolRaw']:
		"""属性シンボルリストを取得

		Returns:
			list[SymbolRaw]: 属性シンボルリスト
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
	def origin(self) -> SymbolRaw:
		"""SymbolRaw: スタックシンボル"""
		return self._origin

	@property
	def _shared_origin(self) -> SymbolRaw:
		"""シンボルテーブル上に存在する共有シンボルを取得

		Returns:
			SymbolRaw: シンボルテーブル上に存在する共有されたシンボル
		Note:
			属性を取得する際にのみ利用 @see attrs
		"""
		if self._origin.org_fullyname in self.__raws:
			origin = self.__raws[self._origin.org_fullyname]
			if id(origin) != id(self):
				return origin

		return self._origin

	@implements
	def clone(self: T_Sym) -> T_Sym:
		"""インスタンスを複製

		Returns:
			T_Sym: 複製したインスタンス
		"""
		return self._clone(origin=self.origin)

	@override
	def extends(self: T_Sym, *attrs: 'SymbolRaw') -> T_Sym:
		"""シンボルが保持する型を拡張情報として属性に取り込む

		Args:
			*attrs (SymbolRaw): 属性シンボルリスト
		Returns:
			SymbolRaw: インスタンス
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

	def __init__(self, origin: ImportOrigins, via: defs.Node) -> None:
		"""インスタンスを生成

		Args:
			origin (SymbolOrigin | SymbolVar): スタックシンボル
			via (Node): 参照元のノード
		"""
		super().__init__(origin)
		self._via = via

	@property
	@implements
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
	def via(self) -> defs.Node:
		"""Node: 参照元のノード"""
		return self._via

	@override
	def clone(self: T_Sym) -> T_Sym:
		"""インスタンスを複製

		Returns:
			T_Sym: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via)


class SymbolClass(Symbol):
	"""シンボル(クラス定義)"""

	def __init__(self, origin: ClassOrigins, decl: defs.ClassDef) -> None:
		"""インスタンスを生成

		Args:
			origin (SymbolOrigin | SymbolImport): スタックシンボル
			via (Node): 参照元のノード
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
	def clone(self: T_Sym) -> T_Sym:
		"""インスタンスを複製

		Returns:
			T_Sym: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, decl=self.decl)


class SymbolVar(Symbol):
	def __init__(self, origin: VarOrigins, decl: defs.DeclAll) -> None:
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
	def clone(self: T_Sym) -> T_Sym:
		"""インスタンスを複製

		Returns:
			T_Sym: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, decl=self.decl)


class SymbolGeneric(Symbol):
	def __init__(self, origin: GenericOrigins, via: defs.Type) -> None:
		"""インスタンスを生成

		Args:
			origin (SymbolOrigin | SymbolImport): スタックシンボル
			via (Node): 参照元のノード
		"""
		super().__init__(origin)
		self._via = via

	@property
	@override
	def via(self) -> defs.Node:
		"""Node: 参照元のノード"""
		return self._via

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Generic

	@override
	def clone(self: T_Sym) -> T_Sym:
		"""インスタンスを複製

		Returns:
			T_Sym: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via)


class SymbolLiteral(Symbol):
	def __init__(self, origin: LiteralOrigins, via: defs.Literal) -> None:
		"""インスタンスを生成

		Args:
			origin (SymbolOrigin | SymbolImport): スタックシンボル
			via (Node): 参照元のノード
		"""
		super().__init__(origin)
		self._via = via

	@property
	@override
	def via(self) -> defs.Node:
		"""Node: 参照元のノード"""
		return self._via

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Literal

	@override
	def clone(self: T_Sym) -> T_Sym:
		"""インスタンスを複製

		Returns:
			T_Sym: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via)


class SymbolReference(Symbol):
	def __init__(self, origin: RefOrigins, via: defs.Node, context: SymbolRaw | None = None) -> None:
		"""インスタンスを生成

		Args:
			origin (RefOrigins): スタックシンボル
			via (Node): 参照元のノード
		"""
		super().__init__(origin)
		self._via = via
		self._context = context

	@property
	@override
	def via(self) -> defs.Node:
		"""Node: 参照元のノード"""
		return self._via

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return Roles.Reference

	@property
	def context(self) -> SymbolRaw:
		"""コンテキストを取得

		Returns:
			SymbolRaw: コンテキストのシンボル
		Raises:
			LogicError: コンテキストが無いシンボルで使用
		"""
		if self._context is not None:
			return self._context

		return super().context

	@override
	def clone(self) -> 'SymbolReference':
		"""インスタンスを複製

		Returns:
			T_Sym: 複製したインスタンス
		"""
		return self._clone(origin=self.origin, via=self.via, context=self._context)


class SymbolWrapper:
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
		return SymbolImport(self._raw.as_a(ImportOrigins), via)

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

	def literal(self, via: defs.Literal) -> SymbolLiteral:
		"""ラップしたシンボルを生成(リテラルノード用)

		Args:
			via (Literal): リテラルノード
		Returns:
			SymbolLiteral: シンボル
		"""
		return SymbolLiteral(self._raw.one_of(LiteralOrigins), via)

	def ref(self, via: defs.Reference | defs.Indexer, context: SymbolRaw | None = None) -> SymbolReference:
		"""ラップしたシンボルを生成(参照ノード用)

		Args:
			via (Reference | Indexer): 参照系ノード
			context (SymbolRaw): コンテキストのシンボル
		Returns:
			SymbolReference: シンボル
		"""
		return SymbolReference(self._raw.one_of(RefOrigins), via, context)
