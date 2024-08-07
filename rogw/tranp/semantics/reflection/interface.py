from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Iterator, NamedTuple, Self, TypeVar

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.lang.annotation import override
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
	def new(cls, *dbs: Self | dict[str, 'IReflection']) -> Self:
		"""シンボルテーブルを結合した新たなインスタンスを生成

		Args:
			*dbs (Self | dict[str, IReflection]): シンボルテーブルリスト
		Returns:
			Self: 生成したインスタンス
		"""
		return cls().merge(*dbs)

	def merge(self, *dbs: Self | dict[str, 'IReflection']) -> Self:
		"""指定のシンボルテーブルと結合

		Args:
			*dbs (Self | dict[str, IReflection]): シンボルテーブルリスト
		Returns:
			Self: 自己参照
		"""
		for in_db in dbs:
			self.update(**in_db)

		for raw in self.values():
			raw.set_db(self)

		return self

	@override
	def __setitem__(self, key: str, raw: 'IReflection') -> None:
		"""配列要素設定のオーバーロード

		Args:
			key (str): 要素名
			raw (IReflection): シンボル
		"""
		raw.set_db(self)
		super().__setitem__(key, raw)

	def sorted(self, module_orders: list[str]) -> Self:
		"""モジュールのロード順に並び替えた新しいインスタンスを生成

		Args:
			module_orders (list[str]): ロード順のモジュール名リスト
		Returns:
			Self: 生成したインスタンス
		"""
		orders = {key: index for index, key in enumerate(module_orders)}
		def order(entry: tuple[str, IReflection]) -> int:
			in_module_path, _ = ModuleDSN.parsed(entry[0])
			return orders.get(in_module_path, -1)

		return self.__class__(dict(sorted(self.items(), key=order)))

	def items_in_preprocess(self) -> Iterator[tuple[str, 'IReflection']]:
		"""プリプロセッサー専用のアイテムイテレーター

		Returns:
			Iterator[tuple[str, 'IReflection']]: イテレーター
		Note:
			XXX * プリプロセッサー内ではSymbolProxyのオリジナルを参照することで無限ループを防止する @seeを参照
			XXX * それ以外の目的で使用するのはNG
			@see semantics.processors.symbol_extends.SymbolExtends
			@see semantics.processors.resolve_unknown.ResolveUnknown
		"""
		for key, raw in self.items():
			org_raw = raw.org_raw if isinstance(raw, ISymbolProxy) else raw
			yield (key, org_raw)


class SymbolDBProvider(NamedTuple):
	"""シンボルテーブルプロバイダー

	Attributes:
		db: シンボルテーブル
	"""

	db: SymbolDB


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
	def _db(self) -> SymbolDB:
		"""SymbolDB: 所属するシンボルテーブル"""
		...

	@abstractmethod
	def set_db(self, db: SymbolDB) -> None:
		"""所属するシンボルテーブルを設定

		Args:
			db (SymbolDB): シンボルテーブル
		"""
		...

	@property
	@abstractmethod
	def _actual_addr(self) -> int:
		"""実体のアドレス(ID)を取得

		Returns:
			int: アドレス(ID)
		Note:
			XXX * このメソッドはSymbolProxyによる無限ループを防ぐ目的で実装 @seeを参照
			XXX * 上記以外の目的で使用することはNG
			@see semantics.reflection.implements.Reflection._shared_origin
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
	def origin(self) -> 'IReflection':
		"""スタックシンボルを取得

		Returns:
			IReflection: スタックシンボル
		Raises:
			SemanticsLogicError: roleがOriginのインスタンスで使用
		"""
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
			SemanticsLogicError: コンテキストが無い状態で使用
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
			SemanticsLogicError: 実体の無いインスタンスに実行 XXX 出力する例外は要件等
			SemanticsLogicError: 拡張済みのインスタンスに再度実行 XXX 出力する例外は要件等
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
	def one_of(self, *expects: type[T_Ref]) -> T_Ref:
		"""期待する型と同種ならキャスト

		Args:
			*expects (type[T_Ref]): 期待する型
		Returns:
			T_Ref: インスタンス
		Raises:
			SemanticsLogicError: 継承関係が無い型を指定 XXX 出力する例外は要件等
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
	def imports(self, via: defs.ImportAsName) -> IReflection:
		"""ラップしたシンボルを生成(インポート)

		Args:
			via (ImportAsName): インポート名ノード
		Returns:
			IReflection: シンボル
		"""
		...

	@abstractmethod
	def proxy(self, via: defs.Reference) -> IReflection:
		"""ラップしたシンボルを生成(タイプ擬態)

		Args:
			via (Reference): 参照系ノード
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


class ISymbolProxy(metaclass=ABCMeta):
	"""シンボルプロクシー専用のインターフェイス"""

	@property
	@abstractmethod
	def org_raw(self) -> 'IReflection':
		"""オリジナルのシンボルを取得

		Returns:
			IReflection: オリジナルのシンボル
		Note:
			XXX * プリプロセッサー内で無限ループを防ぐ目的で実装
			XXX * それ以外の目的で使用するのはNG
			@see semantics.reflection.interface.SymbolDB.items_in_preprocess
		"""
		...
