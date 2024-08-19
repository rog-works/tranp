from abc import ABCMeta, abstractmethod
from typing import Iterator, NamedTuple, Self, TypeVar

from rogw.tranp.dsn.module import ModuleDSN
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node

T_Ref = TypeVar('T_Ref', bound='IReflection')


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

		return self

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
		types (ClassDef): 型を表すノード
		decl (DeclAll): 定義元のノード
		node (Node): ノード
		origin (IReflection): 型のシンボル
		via (IReflection): スタックシンボル
		context (IReflection| None): コンテキストのシンボル
		attrs (list[IReflection]): 属性シンボルリスト
	Note:
		# contextのユースケース
		* Relay/Indexerのreceiverを設定。on_func_call等で実行時型の補完に使用
	"""

	@property
	@abstractmethod
	def types(self) -> defs.ClassDef:
		"""ClassDef: 型を表すノード"""
		...

	@property
	@abstractmethod
	def decl(self) -> defs.DeclAll:
		"""DeclAll: 定義元のノード"""
		...

	@property
	@abstractmethod
	def node(self) -> Node:
		"""Node: ノード"""
		...

	@property
	@abstractmethod
	def origin(self) -> 'IReflection':
		"""IReflection: 型のシンボル"""
		...

	@property
	@abstractmethod
	def via(self) -> 'IReflection':
		"""IReflection: スタックシンボル"""
		...

	@property
	@abstractmethod
	def context(self) -> 'IReflection':
		"""IReflection: コンテキストを取得 Raises: SemanticsLogicError: コンテキストが無い状態で使用"""
		...

	@property
	@abstractmethod
	def attrs(self) -> list['IReflection']:
		"""list[IReflection]: 属性シンボルリスト"""
		...

	@abstractmethod
	def declare(self, decl: defs.DeclVars, origin: 'IReflection | None' = None) -> 'IReflection':
		"""定義ノードをスタック

		Args:
			decl (DeclVars): 定義元のノード
		Returns:
			IReflection: リフレクション
		"""
		...

	@abstractmethod
	def stack_by(self, node: Node) -> 'IReflection':
		"""ノードをスタック

		Args:
			node (Node): ノード
		Returns:
			IReflection: リフレクション
		"""
		...

	@abstractmethod
	def stack_by_self(self) -> 'IReflection':
		"""自身を参照としてスタック

		Returns:
			IReflection: リフレクション
		"""
		...

	@abstractmethod
	def to(self, node: Node, origin: 'IReflection') -> 'IReflection':
		"""ノードをスタックし、型のシンボルを移行

		Args:
			node (Node): ノード
			origin (IReflection): 型のシンボル
		Returns:
			IReflection: リフレクション
		"""
		...

	@property
	@abstractmethod
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		...

	@abstractmethod
	def stacktrace(self) -> Iterator['IReflection']:
		"""スタックシンボルを辿るイテレーターを取得

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
