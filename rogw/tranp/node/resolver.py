from rogw.tranp.ast.resolver import Resolver, SymbolMapping
from rogw.tranp.errors import LogicError
from rogw.tranp.lang.error import raises
from rogw.tranp.lang.implementation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.node.errors import UnresolvedNodeError
from rogw.tranp.node.node import Node


class NodeResolver:
	"""ノードリゾルバー。解決したノードとパスをマッピングして管理"""

	@injectable
	def __init__(self, invoker: Invoker, settings: SymbolMapping) -> None:
		"""インスタンスを生成

		Args:
			invoker (Invoker): ファクトリー関数 @inject
			settings (Settings): マッピング設定データ @inject
		"""
		self.__invoker = invoker
		self.__resolver = Resolver[Node].load(settings)
		self.__insts: dict[str, Node] = {}

	def can_resolve(self, symbol: str) -> bool:
		"""解決出来るか確認

		Args:
			symbol (str): シンボル名
		Returns:
			bool: True = 解決できる
		"""
		return self.__resolver.can_resolve(symbol)

	@raises(UnresolvedNodeError, LogicError)
	def resolve(self, symbol: str, full_path: str) -> Node:
		"""ノードのインスタンスを解決

		Args:
			symbol (str): シンボル
			full_path (str): エントリーのフルパス
		Returns:
			Node: 解決したノード
		Raises:
			UnresolvedNodeError: ノードの解決に失敗
		"""
		if full_path in self.__insts:
			return self.__insts[full_path]

		ctor = self.__resolver.resolve(symbol)
		self.__insts[full_path] = self.__invoker(ctor, full_path).actualize()
		return self.__insts[full_path]

	def clear(self) -> None:
		"""インスタンスのマッピング情報を削除"""
		self.__insts = {}
