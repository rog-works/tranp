from dataclasses import dataclass, field

from typing import NamedTuple, TypeAlias

from py2cpp.lang.implementation import override
from py2cpp.module.modules import Module
import py2cpp.node.definition as defs


class SymbolRaw(NamedTuple):
	"""シンボルデータ

	Attributes:
		ref_path (str): 参照パス
		org_path (str): 参照パス(オリジナル)
		module_path (str): 展開先モジュールのパス
		types (ClassDef): クラス定義ノード
		decl (DeclAll): 宣言ステートメントノード
	"""
	ref_path: str
	org_path: str
	module_path: str
	types: defs.ClassDef
	decl: defs.DeclAll
	via: 'SymbolRaw | None' = None

	def to(self, module: Module) -> 'SymbolRaw':
		"""展開先を変更したインスタンスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.path_to(module), self.org_path, module.path, self.types, self.decl)

	def path_to(self, module: Module) -> str:
		"""展開先を変更した参照パスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			str: 展開先の参照パス
		"""
		return self.ref_path.replace(self.module_path, module.path)

	def varnize(self, var: defs.DeclVars) -> 'SymbolRaw':
		"""変数シンボル用のデータに変換

		Args:
			var (DeclVars): 変数宣言ノード
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.ref_path, self.org_path, var.module_path, self.types, var, self)


SymbolRaws: TypeAlias = dict[str, SymbolRaw]


@dataclass
class Expanded:
	"""展開時のテンポラリーデータ

	Attributes:
		raws (SymbolRaws): シンボルテーブル
		decl_vars (list[DeclVars]): 変数リスト
		import_nodes (list[Import]): インポートリスト
	"""
	raws: SymbolRaws = field(default_factory=dict)
	decl_vars: list[defs.DeclVars] = field(default_factory=list)
	import_nodes: list[defs.Import] = field(default_factory=list)


class Symbol:
	"""シンボル"""

	def __init__(self, raw: SymbolRaw, *attrs: 'Symbol') -> None:
		"""インスタンスを生成

		Args:
			raw (SymbolRaw): 型のシンボルデータ
			*attrs (Symbol): 属性シンボルリスト
		"""
		self.types = raw.types
		self.attrs = list(attrs)
		self.raw = raw

	def extends(self, *attrs: 'Symbol') -> 'Symbol':
		"""既存のスキーマに属性を追加してインスタンスを生成

		Args:
			*attrs (Symbol): 属性シンボルリスト
		Returns:
			Symbol: インスタンス
		"""
		return Symbol(self.raw, *[*self.attrs, *attrs])

	@override
	def __eq__(self, __value: object) -> bool:
		"""比較演算子のオーバーロード

		Args:
			__value (object): 比較対象
		Returns:
			bool: True = 同じ
		"""
		if type(__value) is not Symbol:
			return super().__eq__(__value)

		return __value.__repr__() == self.__repr__()

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
		if len(self.attrs) > 0:
			attrs = [str(attr) for attr in self.attrs]
			return f'{self.types.domain_name}[{', '.join(attrs)}]'
		else:
			return f'{self.types.domain_name}'
