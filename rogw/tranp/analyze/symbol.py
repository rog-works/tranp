from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, Iterator, TypeVar, cast

from rogw.tranp.errors import LogicError
from rogw.tranp.lang.implementation import implements, injectable, override
import rogw.tranp.node.definition as defs
from rogw.tranp.node.node import Node

T_Raw = TypeVar('T_Raw', bound='SymbolRaw')
T_Sym = TypeVar('T_Sym', bound='Symbol')


class Roles(Enum):
	"""シンボルの役割

	Attributes:
		Origin: 定義元。クラス定義ノードが対象。属性なし
		Import: Originの複製。属性なし
		Class: Origin/Importを参照。クラス定義ノードが対象。クラスはGeneric型、ファンクションは関数シグネチャーを属性として保有
		Var: Origin/Importを参照。変数宣言ノードが対象。Generic型の属性を保有
		Reference: Varを参照。参照系ノードが対象。属性なし
		Generic: Origin/Importを参照。タイプノードが対象。Generic型の属性を保有
		Literal: Origin/Importを参照。リテラルノードが対象。Generic型の属性を保有
	"""
	Origin = 'Origin'
	Import = 'Import'
	Class = 'Class'
	Var = 'Var'
	Reference = 'Reference'
	Generic = 'Generic'
	Literal = 'Literal'

	@property
	def has_entity(self) -> bool:
		"""bool: True = 実体を持つ"""
		return self in [Roles.Origin, Roles.Class, Roles.Var, Roles.Generic, Roles.Literal]

	@property
	def is_temporary(self) -> bool:
		"""bool: True = コンテキストを保有"""
		return self in [Roles.Reference, Roles.Generic, Roles.Literal]


class SymbolRaws(dict[str, T_Raw]):
	"""シンボルテーブル"""

	@classmethod
	def new(cls, *raws: 'SymbolRaws | dict[str, T_Raw]') -> 'SymbolRaws':
		"""シンボルテーブルを結合した新たなインスタンスを生成

		Args:
			*raws (SymbolRaws | dict[str, SymbolRaw]): シンボルテーブルリスト
		Returns:
			SymbolRaws: 生成したインスタンス
		"""
		that = cls()
		for in_raws in raws:
			that.update(**in_raws)

		return that


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

	@property
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		return self.make_shorthand()

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

		if type(other) is not SymbolRaw:
			raise ValueError(f'Not allowed comparison. other: {type(other)}')

		return other.__repr__() == self.__repr__()

	@override
	def __repr__(self) -> str:
		"""str: オブジェクトのシリアライズ表現"""
		data = {
			'types': self.types.fullyname,
			'attrs': [attr.__repr__() for attr in self.attrs],
		}
		return f'<{self.__class__.__name__}: {str(data)}>'

	@override
	def __str__(self) -> str:
		"""str: オブジェクトの文字列表現"""
		return self.shorthand

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
			elif self.role != Roles.Class:
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
	"""シンボル(オリジナル)"""

	@injectable
	def __init__(self, types: defs.ClassDef) -> None:
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

	def __init__(self, origin: SymbolRaw) -> None:
		"""インスタンスを生成"""
		super().__init__()
		self._origin = origin
		self._attrs: list[SymbolRaw] = []

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
		"""list[SymbolRaw]: 属性シンボルリスト"""
		return self._attrs if self._attrs else self._origin.attrs

	@property
	@override
	def origin(self) -> SymbolRaw:
		"""SymbolRaw: スタックシンボル"""
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
	def __init__(self, origin: 'SymbolOrigin | SymbolVar', via: defs.Node) -> None:
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
	def __init__(self, origin: 'SymbolOrigin | SymbolImport', decl: defs.ClassDef) -> None:
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
	def __init__(self, origin: 'SymbolOrigin | SymbolImport | SymbolClass | SymbolGeneric | SymbolReference', decl: defs.DeclAll) -> None:
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
	def __init__(self, origin: 'SymbolOrigin | SymbolImport | SymbolClass | SymbolVar | SymbolGeneric', via: defs.Type) -> None:
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
	def __init__(self, origin: SymbolClass, via: defs.Literal) -> None:
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
	def __init__(self, origin: SymbolClass | SymbolVar | SymbolGeneric | SymbolLiteral, via: defs.Node, context: SymbolRaw | None = None) -> None:
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
	def __init__(self, raw: SymbolRaw) -> None:
		self._raw = raw

	def imports(self, via: defs.Import) -> SymbolImport:
		return SymbolImport(self._raw.as_a(SymbolOrigin | SymbolVar), via)

	def types(self, decl: defs.ClassDef) -> SymbolClass:
		return SymbolClass(self._raw.one_of(SymbolOrigin | SymbolImport), decl)

	def var(self, decl: defs.DeclAll) -> SymbolVar:
		return SymbolVar(self._raw.one_of(SymbolOrigin | SymbolImport | SymbolClass | SymbolGeneric | SymbolReference), decl)

	def generic(self, via: defs.Type) -> SymbolGeneric:
		return SymbolGeneric(self._raw.one_of(SymbolOrigin | SymbolImport | SymbolClass | SymbolVar | SymbolGeneric), via)

	def literal(self, via: defs.Literal) -> SymbolLiteral:
		return SymbolLiteral(self._raw.one_of(SymbolClass), via)

	def ref(self, via: defs.Node, context: SymbolRaw | None = None) -> SymbolReference:
		return SymbolReference(self._raw.one_of(SymbolClass | SymbolVar | SymbolGeneric | SymbolLiteral), via, context)


# class Symbol_(Symbol):
# 	"""シンボル(変数)"""
# 
# 	def __init__(self, types: SymbolOrigin) -> None:
# 		"""インスタンスを生成
# 
# 		Args:
# 			ref_path (str): 参照パス
# 			types (ClassDef): クラス定義ノード
# 			decl (DeclAll): クラス/変数宣言ノード
# 			role (Roles): シンボルの役割
# 			org (SymbolRaw | None): スタックシンボル (default = None)
# 			via (Node | None): 参照元のノード (default = None)
# 			context (SymbolRaw| None): コンテキストのシンボル (default = None)
# 		Note:
# 			# contextのユースケース
# 			* Relay/Indexerのreceiverを設定。on_func_call等で実行時型の補完に使用
# 		"""
# 		org: 'SymbolRaw | None' = None,
# 		via: Node | None = None,
# 		context: 'SymbolRaw | None' = None
# 		self._org = org
# 		self._via = via
# 		self._context = context
# 
# 	@property
# 	@implements
# 	def org_fullyname(self) -> str:
# 		"""str: 完全参照名(オリジナル)"""
# 		return self.types.fullyname
# 
# 	@property
# 	@implements
# 	def types(self) -> defs.ClassDef:
# 		"""ClassDef: クラス定義ノード"""
# 		return self._nodes.by(self._types_path).as_a(defs.ClassDef)
# 
# 	@property
# 	@implements
# 	def decl(self) -> defs.DeclAll:
# 		"""DeclAll: クラス/変数宣言ノード"""
# 		return self._nodes.by(self._decl_path).as_a(defs.DeclAll)
# 
# 	@property
# 	def org(self) -> 'SymbolRaw | None':
# 		"""SymbolRaw | None: スタックシンボル"""
# 		return self._org
# 
# 	@property
# 	def via(self) -> Node | None:
# 		"""Node | None: 参照元のノード"""
# 		return self._via
# 
# 	@property
# 	def context(self) -> 'SymbolRaw':
# 		"""コンテキストを取得
# 
# 		Returns:
# 			SymbolRaw: コンテキストのシンボル
# 		Raises:
# 			LogicError: コンテキストが無いシンボルで使用
# 		"""
# 		if self._context is None:
# 			raise LogicError(f'Context is null. symbol: {str(self)}, ref_path: {self.ref_fullyname}')
# 
# 		return self._context
# 
# 	@property
# 	def has_entity(self) -> bool:
# 		"""bool: True = 実体を持つ"""
# 		return self._role in [Roles.Origin, Roles.Var, Roles.Extend]
# 
# 
# 	def each_via(self) -> Iterator[Node]:
# 		"""参照元を辿るイテレーターを取得
# 
# 		Returns:
# 			Iterator[Node]: イテレーター
# 		"""
# 		curr = self
# 		while curr:
# 			# XXX whileの判定が反映されずに警告されるためcastで対処
# 			yield cast(Node, curr.via)
# 			curr = curr.org
# 
# 	def safe_get_context(self) -> 'SymbolRaw | None':
# 		"""コンテキストを取得
# 
# 		Returns:
# 			SymbolRaw | None: コンテキストのシンボル
# 		"""
# 		return self._context
# 
# 	def path_to(self, module: Module) -> str:
# 		"""展開先を変更した参照パスを生成
# 
# 		Args:
# 			module (Module): 展開先のモジュール
# 		Returns:
# 			str: 展開先の参照パス
# 		"""
# 		return self.ref_fullyname.replace(self.types.module_path, module.path)
# 
# 	def clone(self) -> 'SymbolRaw':
# 		"""複製を作成
# 
# 		Returns:
# 			SymbolRaw: インスタンス
# 		"""
# 		return SymbolRaw(self.ref_fullyname, types=self.types, decl=self.decl, role=self._role, org=self.org, via=self.via, context=self._context).extends(*self.attrs)
# 
# 	def to_import(self, module: Module) -> 'SymbolRaw':
# 		"""インポート用にラップ
# 
# 		Args:
# 			module (Module): 展開先のモジュール
# 		Returns:
# 			SymbolRaw: インスタンス
# 		"""
# 		return SymbolRaw(self.path_to(module), types=self.types, decl=self.decl, role=Roles.Import, org=self)
# 
# 	def to_var(self, decl: defs.DeclVars) -> 'SymbolRaw':
# 		"""変数宣言用にラップ
# 
# 		Args:
# 			decl (DeclVars): 変数宣言ノード
# 		Returns:
# 			SymbolRaw: インスタンス
# 		"""
# 		return SymbolRaw(self.ref_fullyname, types=self.types, decl=decl, role=Roles.Var, org=self, via=decl)
# 
# 	def to_ref(self, node: defs.RefAll, context: 'SymbolRaw | None' = None) -> 'SymbolRaw':
# 		"""参照用にラップ
# 
# 		Args:
# 			node (RefAll): 参照系ノード
# 			context (SymbolRaw | None): コンテキストのシンボル
# 		Returns:
# 			SymbolRaw: インスタンス
# 		"""
# 		return SymbolRaw(self.ref_fullyname, types=self.types, decl=self.decl, role=Roles.Reference, org=self, via=node, context=context)
# 
# 	def to_generic(self, node: defs.Generized) -> 'SymbolRaw':
# 		"""ジェネリック用にラップ
# 
# 		Args:
# 			node (Generized): ジェネリック化対象ノード
# 		Returns:
# 			SymbolRaw: インスタンス
# 		"""
# 		return SymbolRaw(self.ref_fullyname, types=self.types, decl=self.decl, role=Roles.Extend, org=self, via=node)
# 
# 	def extends(self, *attrs: 'SymbolRaw') -> 'SymbolRaw':
# 		"""シンボルが保持する型を拡張情報として属性に取り込む
# 
# 		Args:
# 			*attrs (SymbolRaw): 属性シンボルリスト
# 		Returns:
# 			SymbolRaw: インスタンス
# 		Raises:
# 			LogicError: 実体の無いインスタンスに実行
# 			LogicError: 拡張済みのインスタンスに再度実行
# 		"""
# 		if not self.has_entity:
# 			raise LogicError(f'Not allowd extends. symbol: {self.types.fullyname}, role: {self._role}')
# 
# 		if self._attrs:
# 			raise LogicError(f'Already set attibutes. symbol: {self.types.fullyname}')
# 
# 		self._attrs = list(attrs)
# 		return self
