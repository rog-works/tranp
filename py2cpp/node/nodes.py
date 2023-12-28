import re
from typing import Callable

from py2cpp.ast.cache import EntryCache
from py2cpp.ast.entry import Entry
from py2cpp.ast.provider import Query, Resolver, Settings
from py2cpp.ast.travarsal import ASTFinder, EntryPath
from py2cpp.errors import NotFoundError
from py2cpp.lang.annotation import implements
from py2cpp.lang.locator import Curry
from py2cpp.node.node import Node


class NodeResolver:
	"""ノードリゾルバー。解決したノードとパスをマッピングして管理"""

	def __init__(self, curry: Curry, settings: Settings) -> None:
		"""インスタンスを生成

		Args:
			curry (Curry): カリー化関数
			settings (Settings): マッピング設定データ
		"""
		self.__curry = curry
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

	def resolve(self, symbol: str, full_path: str) -> Node:
		"""ノードのインスタンスを解決

		Args:
			symbol (str): シンボル
			full_path (str): エントリーのフルパス
		Returns:
			Node: 解決したノード
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		if full_path in self.__insts:
			return self.__insts[full_path]

		ctor = self.__resolver.resolve(symbol)
		factory = self.__curry(ctor, Callable[[str], ctor])
		self.__insts[full_path] = factory(full_path).actualize()
		return self.__insts[full_path]

	def clear(self) -> None:
		"""インスタンスのマッピング情報を削除"""
		self.__insts = {}


class Nodes(Query[Node]):
	"""ノードクエリーインターフェイス。ASTを元にノードの探索し、リゾルバーを介してインスタンスを解決"""

	@classmethod
	def root(cls, that: Query[Node]) -> Node:
		"""ルートノードリゾルバー

		Args:
			that (Query[Node]): 自身のインスタンス @inject
		Returns:
			Node: ルートノード
		Note:
			FIXME 苦し紛れ感があるので、関数に分離しても良さそう
		"""
		return that.by('file_input')

	def __init__(self, resolver: NodeResolver, root: Entry) -> None:
		"""インスタンスを生成

		Args:
			resolver (NodeResolver): ノードリゾルバー
			root (Entry): ASTのルート要素
		"""
		self.__resolver = resolver
		self.__entries = EntryCache[Entry]()
		for full_path, entry in ASTFinder().full_pathfy(root).items():
			self.__entries.add(full_path, entry)

	def __resolve(self, entry: Entry, full_path: str) -> Node:
		"""エントリーからノードを解決し、パスとマッピングしてキャッシュ

		Args:
			entry (Entry): エントリー
			full_path (str): エントリーのフルパス
		Returns:
			Node: 解決したノード
		"""
		return self.__resolver.resolve(entry.name, full_path)

	@implements
	def exists(self, full_path: str) -> bool:
		"""指定のパスに紐づく一意なノードが存在するか判定

		Args:
			full_path (str): フルパス
		Returns:
			bool: True = 存在
		"""
		return self.__entries.exists(full_path)

	@implements
	def by(self, full_path: str) -> Node:
		"""指定のパスに紐づく一意なノードをフェッチ

		Args:
			full_path (str): フルパス
		Returns:
			Node: ノード
		Raises:
			NotFoundError: ノードが存在しない
		"""
		entry = self.__entries.by(full_path)
		return self.__resolve(entry, full_path)

	@implements
	def parent(self, via: str) -> Node:
		"""指定のパスを子として親のノードをフェッチ

		Args:
			via (str): 基点のパス
		Returns:
			Node: ノード
		Raises:
			NotFoundError: 親が存在しない
		"""
		forwards = EntryPath(via).shift(-1)
		while(forwards.valid):
			tag, _ = forwards.last
			if self.__resolver.can_resolve(tag):
				return self.by(forwards.origin)

			forwards = forwards.shift(-1)

		raise NotFoundError(via)

	@implements
	def ancestor(self, via: str, tag: str) -> Node:
		"""指定のエントリータグを持つ直近の親ノードをフェッチ

		Args:
			via (str): 基点のパス
			tag (str): エントリータグ
		Returns:
			Node: ノード
		Raises:
			NotFoundError: 指定のエントリータグを持つ親が存在しない
		"""
		base = EntryPath(via)
		elems = list(reversed(base.de_identify().elements))
		index = elems.index(tag)
		if index == -1:
			raise NotFoundError(via, tag)

		slices = len(elems) - index
		found_path = EntryPath.join(*base.elements[:slices])
		return self.by(found_path.origin)

	@implements
	def siblings(self, via: str) -> list[Node]:
		"""指定のパスを基準に同階層のノードをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[Node]: ノードリスト
		Raises:
			NotFoundError: 基点のノードが存在しない
		"""
		uplayer_path = EntryPath(via).shift(-1)
		if not uplayer_path.valid:
			raise NotFoundError(via)

		regular = re.compile(rf'{uplayer_path.escaped_origin}\.[^.]+')
		tester = lambda _, path: regular.fullmatch(path) is not None
		entries = {path: entry for path, entry in self.__entries.group_by(uplayer_path.origin).items() if tester(entry, path)}
		return [self.__resolve(entry, path) for path, entry in entries.items()]

	@implements
	def children(self, via: str) -> list[Node]:
		"""指定のパスを基準に1階層下のノードをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[Node]: ノードリスト
		Raises:
			NotFoundError: 基点のノードが存在しない
		"""
		regular = re.compile(rf'{EntryPath(via).escaped_origin}\.[^.]+')
		tester = lambda _, path: regular.fullmatch(path) is not None
		entries = {path: entry for path, entry in self.__entries.group_by(via).items() if tester(entry, path)}
		return [self.__resolve(entry, path) for path, entry in entries.items()]

	@implements
	def leafs(self, via: str, leaf_tag: str) -> list[Node]:
		"""指定のパスから下に存在する接尾辞が一致するノードをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
			leaf_name (str): 接尾辞
		Returns:
			list[Node]: ノードリスト
		Raises:
			NotFoundError: 基点のノードが存在しない
		"""
		regular = re.compile(rf'{EntryPath(via).escaped_origin}\.(.+\.)?{leaf_tag}(\[\d+\])?')
		tester = lambda _, path: regular.fullmatch(path) is not None
		entries = {path: entry for path, entry in self.__entries.group_by(via).items() if tester(entry, path)}
		return [self.__resolve(entry, path) for path, entry in entries.items()]

	@implements
	def expand(self, via: str) -> list[Node]:
		"""指定のパスから下に存在する展開が可能なノードをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[Node]: ノードリスト
		Raises:
			NotFoundError: 基点のノードが存在しない
		"""
		memo: list[str] = []
		def tester(entry: Entry, path: str) -> bool:
			if via == path:
				return False

			# 記録済みの変換対象以降の要素は全て除外
			if len([cached for cached in memo if path.startswith(cached)]):
				return False

			entry_path = EntryPath(path)

			# XXX 変換対象が存在する場合はそちらに対応を任せる(終端記号か否かは問わない)
			entry_tag = entry_path.last[0]
			if self.__resolver.can_resolve(entry_tag):
				memo.append(entry_path.origin)
				return True

			if entry.has_child:
				return False

			# 自身を含む配下のエントリーに変換対象のノードがなく、Terminalにフォールバックされる終端記号が対象
			entry_tags = entry_path.relativefy(via).de_identify().elements
			in_allows = [index for index, in_tag in enumerate(entry_tags) if self.__resolver.can_resolve(in_tag)]
			return len(in_allows) == 0

		entries = {path: entry for path, entry in self.__entries.group_by(via).items() if tester(entry, path)}
		return [self.__resolve(entry, path) for path, entry in entries.items()]

	@implements
	def values(self, via: str) -> list[str]:
		"""指定のパス以下(基点を含む)のエントリーの値を取得

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[str]: 値リスト
		"""
		return [entry.value for entry in self.__entries.group_by(via).values() if entry.value]
