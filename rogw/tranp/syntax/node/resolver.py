from rogw.tranp.errors import Errors
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.syntax.ast.resolver import Resolver, SymbolMapping
from rogw.tranp.syntax.node.node import Node


class NodeResolver:
	"""ノードリゾルバー。解決したノードとパスをマッピングして管理"""

	@injectable
	def __init__(self, invoker: Invoker, settings: SymbolMapping) -> None:
		"""インスタンスを生成

		Args:
			invoker: ファクトリー関数 @inject
			settings: マッピング設定データ @inject
		"""
		self.__invoker = invoker
		self.__resolver = Resolver[Node].load(settings)
		self.__insts: dict[str, Node] = {}

	def can_resolve(self, symbol: str) -> bool:
		"""解決出来るか確認

		Args:
			symbol: シンボル名
		Returns:
			True = 解決できる
		"""
		return self.__resolver.can_resolve(symbol)

	def resolve(self, symbol: str, full_path: str) -> Node:
		"""ノードのインスタンスを解決

		Args:
			symbol: シンボル
			full_path: エントリーのフルパス
		Returns:
			解決したノード
		Raises:
			Errors.UnresolvedNode: ノードの解決に失敗
		"""
		if full_path in self.__insts:
			return self.__insts[full_path]

		ctors = self.__resolver.resolve(symbol)
		# XXX match_feature用の仮ノードを生成
		dummy = self.__invoker(Node, full_path)
		for ctor in ctors:
			if ctor.match_feature(dummy):
				self.__insts[full_path] = self.__invoker(ctor, full_path)
				return self.__insts[full_path]

		raise Errors.UnresolvedNode(symbol, full_path)

	def clear(self) -> None:
		"""インスタンスのマッピング情報を削除"""
		self.__insts = {}
