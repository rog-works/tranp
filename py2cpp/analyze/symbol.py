from enum import Enum
from typing import Iterator, TypeAlias, cast

from py2cpp.errors import LogicError
from py2cpp.lang.implementation import override
from py2cpp.module.modules import Module
import py2cpp.node.definition as defs
from py2cpp.node.node import Node

SymbolRaws: TypeAlias = dict[str, 'SymbolRaw']


class Roles(Enum):
	"""シンボルの役割

	Attributes:
		Origin: 定義元。クラス定義ノードが対象。ファンクション定義ノードは関数シグネチャーを属性として保持
		Import: Originの複製。属性なし
		Var: Origin/Importを参照。変数宣言ノードが対象。Generic型の属性を保持
		Reference: Varの参照。参照系ノードが対象。属性なし
		Extend: Origin/Importを参照。タイプ/リテラルノードが対象。Generic型の属性を保持
	Note:
		# 参照関係
		* Origin <- Import
		* Origin <- Var
		* Origin <- Extend
		* Import <- Var
		* Import <- Extend
		* Var <- Reference
		* Extend <- Var ※MoveAssign/Forの場合のみ
	"""
	Origin = 'Origin'
	Import = 'Import'
	Var = 'Var'
	Reference = 'Reference'
	Extend = 'Extend'


class SymbolRaw:
	"""シンボル"""

	@classmethod
	def from_types(cls, types: defs.ClassDef) -> 'SymbolRaw':
		"""クラス定義ノードを元にインスタンスを生成

		Args:
			types (ClassDef): クラス定義ノード
		Returns:
			SymbolRaw: シンボル
		"""
		return cls(types.fullyname, types=types, decl=types)

	def __init__(
		self,
		ref_path: str,
		types: defs.ClassDef,
		decl: defs.DeclAll,
		role: Roles = Roles.Origin,
		org: 'SymbolRaw | None' = None,
		via: Node | None = None,
		context: 'SymbolRaw | None' = None
	) -> None:
		"""インスタンスを生成

		Args:
			ref_path (str): 参照パス
			types (ClassDef): クラス定義ノード
			decl (DeclAll): クラス/変数宣言ノード
			role (Roles): シンボルの役割
			org (SymbolRaw | None): スタックシンボル (default = None)
			via (Node | None): 参照元のノード (default = None)
			context (SymbolRaw| None): コンテキストのシンボル (default = None)
		Note:
			# contextのユースケース
			* Relay/Indexerのreceiverを設定。on_func_call等で実行時型の補完に使用
		"""
		self._ref_path = ref_path
		self._types = types
		self._decl = decl
		self._role = role
		self._attrs: list[SymbolRaw] = []
		self._org = org
		self._via = via
		self._context = context

	@property
	def ref_path(self) -> str:
		"""str: 参照パス"""
		return self._ref_path

	@property
	def org_path(self) -> str:
		"""str: 参照パス(オリジナル)"""
		return self.types.fullyname

	@property
	def types(self) -> defs.ClassDef:
		"""ClassDef: クラス定義ノード"""
		return self._types

	@property
	def decl(self) -> defs.DeclAll:
		"""DeclAll: クラス/変数宣言ノード"""
		return self._decl

	@property
	def attrs(self) -> list['SymbolRaw']:
		"""list[SymbolRaw]: 属性シンボルリスト"""
		if self._attrs:
			return self._attrs

		return self._org.attrs if self._org else []

	@property
	def org(self) -> 'SymbolRaw | None':
		"""SymbolRaw | None: スタックシンボル"""
		return self._org

	@property
	def via(self) -> Node | None:
		"""Node | None: 参照元のノード"""
		return self._via

	@property
	def context(self) -> 'SymbolRaw':
		"""コンテキストを取得

		Returns:
			SymbolRaw: コンテキストのシンボル
		Raises:
			LogicError: コンテキストが無いシンボルで使用
		"""
		if self._context is None:
			raise LogicError(f'Context is null. symbol: {str(self)}, ref_path: {self.ref_path}')

		return self._context

	@property
	def has_entity(self) -> bool:
		"""bool: True = 実体を持つ"""
		return self._role in [Roles.Origin, Roles.Var, Roles.Extend]

	@property
	def shorthand(self) -> str:
		"""str: オブジェクトの簡易表現"""
		if len(self.attrs) > 0:
			if self.types.is_a(defs.AltClass):
				attrs = [str(attr) for attr in self.attrs]
				return f'{self.types.domain_name}={attrs[0]}'
			elif self.types.is_a(defs.Function):
				attrs = [str(attr) for attr in self.attrs]
				return f'{self.types.domain_name}({", ".join(attrs[:-1])}) -> {attrs[-1]}'
			elif self._role != Roles.Origin:
				attrs = [str(attr) for attr in self.attrs]
				return f'{self.types.domain_name}<{", ".join(attrs)}>'

		return f'{self.types.domain_name}'

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
		return str(data)

	@override
	def __str__(self) -> str:
		"""str: オブジェクトの文字列表現"""
		return self.shorthand

	def each_via(self) -> Iterator[Node]:
		"""参照元を辿るイテレーターを取得

		Returns:
			Iterator[Node]: イテレーター
		"""
		curr = self
		while curr:
			# XXX whileの判定が反映されずに警告されるためcastで対処
			yield cast(Node, curr.via)
			curr = curr.org

	def safe_get_context(self) -> 'SymbolRaw | None':
		"""コンテキストを取得

		Returns:
			SymbolRaw | None: コンテキストのシンボル
		"""
		return self._context

	def path_to(self, module: Module) -> str:
		"""展開先を変更した参照パスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			str: 展開先の参照パス
		"""
		return self.ref_path.replace(self.types.module_path, module.path)

	def to_import(self, module: Module) -> 'SymbolRaw':
		"""インポート用にラップ

		Args:
			module (Module): 展開先のモジュール
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.path_to(module), types=self.types, decl=self.decl, role=Roles.Import, org=self)

	def to_var(self, decl: defs.DeclVars) -> 'SymbolRaw':
		"""変数宣言用にラップ

		Args:
			decl (DeclVars): 変数宣言ノード
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.ref_path, types=self.types, decl=decl, role=Roles.Var, org=self, via=decl)

	def to_ref(self, node: defs.RefAll, context: 'SymbolRaw | None' = None) -> 'SymbolRaw':
		"""参照用にラップ

		Args:
			node (RefAll): 参照系ノード
			context (SymbolRaw | None): コンテキストのシンボル
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.ref_path, types=self.types, decl=self.decl, role=Roles.Reference, org=self, via=node, context=context)

	def to_generic(self, node: defs.Generized) -> 'SymbolRaw':
		"""ジェネリック用にラップ

		Args:
			node (Generized): ジェネリック化対象ノード
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.ref_path, types=self.types, decl=self.decl, role=Roles.Extend, org=self, via=node)

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
		if not self.has_entity:
			raise LogicError(f'Not allowd extends. symbol: {self.types.fullyname}, role: {self._role}')

		if self._attrs:
			raise LogicError(f'Already set attibutes. symbol: {self.types.fullyname}')

		self._attrs = list(attrs)
		return self


