from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Iterator, NamedTuple, Self, TypeVar

from rogw.tranp.lang.implementation import override
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node

T_Ref = TypeVar('T_Ref', bound='IReflection')


class Roles(Enum):
	"""シンボルの役割

	Attributes:
		Origin: 定義元。クラス定義ノードが対象。属性は保有しない
		Class: クラス定義ノードが対象。クラスはGeneric型、ファンクションは関数シグネチャーを属性として保有
		Var: 変数宣言ノードが対象。Generic型の属性を保有
	"""

	Origin = 'Origin'
	Class = 'Class'
	Var = 'Var'


class SymbolDB(dict[str, 'IReflection']):
	"""シンボルテーブル"""

	@classmethod
	def new(cls, *raws: Self | dict[str, 'IReflection']) -> Self:
		"""シンボルテーブルを結合した新たなインスタンスを生成

		Args:
			*raws (Self | dict[str, IReflection]): シンボルテーブルリスト
		Returns:
			Self: 生成したインスタンス
		"""
		return cls().merge(*raws)

	def merge(self, *raws: Self | dict[str, 'IReflection']) -> Self:
		"""指定のシンボルテーブルと結合

		Args:
			*raws (Self | dict[str, IReflection]): シンボルテーブルリスト
		Returns:
			Self: 自己参照
		"""
		for in_raws in raws:
			self.update(**in_raws)

		for raw in self.values():
			raw.set_raws(self)

		return self

	@override
	def __setitem__(self, key: str, raw: 'IReflection') -> None:
		"""配列要素設定のオーバーロード

		Args:
			key (str): 要素名
			raw (IReflection): シンボル
		"""
		raw.set_raws(self)
		super().__setitem__(key, raw)

	def sorted(self, module_orders: list[str]) -> Self:
		"""モジュールのロード順に並び替えた新しいインスタンスを生成

		Args:
			module_orders (list[str]): ロード順のモジュール名リスト
		Returns:
			Self: 生成したインスタンス
		"""
		orders = {index: key for index, key in enumerate(module_orders)}
		def order(entry: tuple[str, IReflection]) -> int:
			key, _ = entry
			for index, module_path in orders.items():
				if module_path in key:
					return index

			return -1

		return self.__class__(dict(sorted(self.items(), key=order)))


class SymbolDBProvider(NamedTuple):
	"""シンボルテーブルプロバイダー

	Attributes:
		raws: シンボルテーブル
	"""

	raws: SymbolDB


class IReflection(metaclass=ABCMeta):
	"""シンボル

	Attributes:
		ref_fullyname (str): 完全参照名
		org_fullyname (str): 完全参照名(オリジナル)
		types (ClassDef): クラス定義ノード
		decl (DeclAll): クラス/変数宣言ノード
		role (Roles): シンボルの役割
		attrs (list[IReflection]): 属性シンボルリスト
		origin (IReflection | None): スタックシンボル (default = None)
		via (Node | None): 参照元のノード (default = None)
		context (IReflection| None): コンテキストのシンボル (default = None)
	Note:
		# contextのユースケース
		* Relay/Indexerのreceiverを設定。on_func_call等で実行時型の補完に使用
	"""

	@property
	@abstractmethod
	def _raws(self) -> SymbolDB:
		"""SymbolDB: 所属するシンボルテーブル"""
		...

	@abstractmethod
	def set_raws(self, raws: SymbolDB) -> None:
		"""所属するシンボルテーブルを設定

		Args:
			raws (SymbolDB): シンボルテーブル
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
	def attrs(self) -> list['IReflection']:
		"""list[IReflection]: 属性シンボルリスト"""
		...

	@property
	@abstractmethod
	def origin(self) -> 'IReflection | None':
		"""IReflection | None: スタックシンボル"""
		...

	@property
	@abstractmethod
	def via(self) -> Node | None:
		"""Node | None: 参照元のノード"""
		...

	@property
	@abstractmethod
	def context(self) -> 'IReflection':
		"""コンテキストを取得

		Returns:
			IReflection: コンテキストのシンボル
		Raises:
			LogicError: コンテキストが無い状態で使用
		"""
		...

	@abstractmethod
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		...

	@property
	@abstractmethod
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		...

	@abstractmethod
	def hierarchy(self) -> Iterator['IReflection']:
		"""参照元を辿るイテレーターを取得

		Returns:
			Iterator[IReflection]: イテレーター
		"""
		...

	@abstractmethod
	def extends(self: Self, *attrs: 'IReflection') -> Self:
		"""シンボルが保有する型を拡張情報として属性に取り込む

		Args:
			*attrs (IReflection): 属性シンボルリスト
		Returns:
			T_Ref: インスタンス
		Raises:
			LogicError: 実体の無いインスタンスに実行 XXX 出力する例外は要件等
			LogicError: 拡張済みのインスタンスに再度実行 XXX 出力する例外は要件等
		"""
		...

	@property
	@abstractmethod
	def to(self) -> 'IWrapper':
		"""ラッパーファクトリーを生成

		Returns:
			SymbolWrapper: ラッパーファクトリー
		"""
		...

	@abstractmethod
	def one_of(self, expects: type[T_Ref]) -> T_Ref:
		"""期待する型と同種ならキャスト

		Args:
			expects (type[T_Ref]): 期待する型
		Returns:
			T_Ref: インスタンス
		Raises:
			LogicError: 継承関係が無い型を指定 XXX 出力する例外は要件等
		"""
		...


class IWrapper(metaclass=ABCMeta):
	"""ラッパーファクトリー"""

	@abstractmethod
	def types(self) -> IReflection:
		"""ラップしたシンボルを生成(クラス)

		Returns:
			IReflection: シンボル
		"""
		...

	@abstractmethod
	def var(self, decl: defs.DeclVars) -> IReflection:
		"""ラップしたシンボルを生成(変数)

		Args:
			decl (DeclVars): 変数宣言ノード
		Returns:
			IReflection: シンボル
		"""
		...

	@abstractmethod
	def imports(self, via: defs.ImportName) -> IReflection:
		"""ラップしたシンボルを生成(インポート)

		Args:
			via (ImportName): インポート名ノード
		Returns:
			IReflection: シンボル
		"""
		...

	@abstractmethod
	def generic(self, via: defs.Type) -> IReflection:
		"""ラップしたシンボルを生成(タイプ拡張)

		Args:
			via (Type): タイプノード
		Returns:
			IReflection: シンボル
		"""
		...

	@abstractmethod
	def literal(self, via: defs.Literal) -> IReflection:
		"""ラップしたシンボルを生成(リテラル)

		Args:
			via (Literal | Comprehension): リテラルノード
		Returns:
			IReflection: シンボル
		"""
		...

	@abstractmethod
	def result(self, via: defs.Operator | defs.Comprehension) -> IReflection:
		"""ラップしたシンボルを生成(結果)

		Args:
			via (Operator): 結果系ノード 演算/リスト内包表記ノード
		Returns:
			IReflection: シンボル
		"""
		...

	@abstractmethod
	def relay(self, via: defs.Relay | defs.Indexer | defs.FuncCall, context: IReflection) -> IReflection:
		"""ラップしたシンボルを生成(参照リレー)

		Args:
			via (Relay | Indexer | FuncCall): 参照系ノード
			context (IReflection): コンテキストのシンボル
		Returns:
			IReflection: シンボル
		"""
		...
