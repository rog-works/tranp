import re

from rogw.tranp.io.memo import Memoize
from rogw.tranp.lang.implementation import implements, injectable
from rogw.tranp.syntax.ast.cache import EntryCache
from rogw.tranp.syntax.ast.entry import Entry, SourceMap
from rogw.tranp.syntax.ast.finder import ASTFinder
from rogw.tranp.syntax.ast.path import EntryPath
from rogw.tranp.syntax.ast.query import Query
from rogw.tranp.syntax.errors import NodeNotFoundError
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.syntax.node.resolver import NodeResolver


class Nodes(Query[Node]):
	"""ノードクエリーインターフェイス。ASTを元にノードの探索し、リゾルバーを介してインスタンスを解決"""

	@injectable
	def __init__(self, resolver: NodeResolver, root: Entry) -> None:
		"""インスタンスを生成

		Args:
			resolver (NodeResolver): ノードリゾルバー @inject
			root (Entry): ASTのルート要素 @inject
		"""
		self.__memo = Memoize()
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
			NodeNotFoundError: ノードが存在しない
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
			NodeNotFoundError: 親が存在しない
		"""
		memo = self.__memo.get(self.parent)
		@memo(via)
		def factory() -> Node:
			forwards = EntryPath(via).shift(-1)
			while(forwards.valid):
				if self.__resolver.can_resolve(forwards.last_tag):
					return self.by(forwards.origin)

				forwards = forwards.shift(-1)

			raise NodeNotFoundError(via)

		return factory()

	@implements
	def ancestor(self, via: str, tag: str) -> Node:
		"""指定のエントリータグを持つ直近の親ノードをフェッチ

		Args:
			via (str): 基点のパス
			tag (str): エントリータグ
		Returns:
			Node: ノード
		Raises:
			NodeNotFoundError: 指定のエントリータグを持つ親が存在しない
		"""
		memo = self.__memo.get(self.ancestor)
		@memo(f'{via}#{tag}')
		def factory() -> Node:
			base = EntryPath(via)
			elems = list(reversed(base.de_identify().elements))
			index = elems.index(tag)
			if index == -1:
				raise NodeNotFoundError(via, tag)

			slices = len(elems) - index
			found_path = EntryPath.join(*base.elements[:slices])
			return self.by(found_path.origin)

		return factory()

	@implements
	def siblings(self, via: str) -> list[Node]:
		"""指定のパスを基準に同階層のノードをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[Node]: ノードリスト
		Raises:
			NodeNotFoundError: 基点のノードが存在しない
		"""
		uplayer_path = EntryPath(via).shift(-1)
		if not uplayer_path.valid:
			raise NodeNotFoundError(via)

		regular = re.compile(rf'{uplayer_path.escaped_origin}\.[^.]+')
		tester = lambda _, path: regular.fullmatch(path) is not None
		entries = {path: entry for path, entry in self.__entries.group_by(uplayer_path.origin, depth=1).items() if tester(entry, path)}
		return [self.__resolve(entry, path) for path, entry in entries.items()]

	@implements
	def children(self, via: str) -> list[Node]:
		"""指定のパスを基準に1階層下のノードをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[Node]: ノードリスト
		Raises:
			NodeNotFoundError: 基点のノードが存在しない
		"""
		memo = self.__memo.get(self.children)
		@memo(via)
		def factory() -> list[Node]:
			regular = re.compile(rf'{EntryPath(via).escaped_origin}\.[^.]+')
			tester = lambda _, path: regular.fullmatch(path) is not None
			entries = {path: entry for path, entry in self.__entries.group_by(via, depth=1).items() if tester(entry, path)}
			return [self.__resolve(entry, path) for path, entry in entries.items()]

		return factory()

	@implements
	def expand(self, via: str) -> list[Node]:
		"""指定のパスから下に存在する展開が可能なノードをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[Node]: ノードリスト
		Raises:
			NodeNotFoundError: 基点のノードが存在しない
		"""
		memo = self.__memo.get(self.expand)
		@memo(via)
		def factory() -> list[Node]:
			record: list[str] = []
			def tester(entry: Entry, path: str) -> bool:
				if via == path:
					return False

				# 記録済みの変換対象以降の要素は全て除外
				if len([cached for cached in record if path.startswith(cached)]):
					return False

				entry_path = EntryPath(path)

				# XXX 変換対象が存在する場合はそちらに対応を任せる(終端記号か否かは問わない)
				if self.__resolver.can_resolve(entry_path.last_tag):
					record.append(entry_path.origin)
					return True

				if entry.has_child:
					return False

				# 自身を含む配下のエントリーに変換対象のノードがなく、Terminalにフォールバックされる終端記号が対象
				entry_tags = entry_path.relativefy(via).de_identify().elements
				in_allows = [index for index, in_tag in enumerate(entry_tags) if self.__resolver.can_resolve(in_tag)]
				return len(in_allows) == 0

			# XXX depthの3階層下までと言う指定に根拠はない。影響はないだろうと言う程度なので問題があったら修正
			under_entries = self.__entries.group_by(via, depth=3).items()
			entries = {path: entry for path, entry in under_entries if tester(entry, path)}
			return [self.__resolve(entry, path) for path, entry in entries.items()]

		return factory()

	@implements
	def values(self, via: str) -> list[str]:
		"""指定のパス以下(基点を含む)のエントリーの値を取得

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[str]: 値リスト
		"""
		memo = self.__memo.get(self.values)
		@memo(via)
		def factory() -> list[str]:
			return [entry.value for entry in self.__entries.group_by(via).values() if entry.value]

		return factory()

	@implements
	def id(self, full_path: str) -> int:
		"""指定のパスのエントリーのIDを取得

		Args:
			full_path (str): フルパス
		Returns:
			int: ID
		"""
		return self.__entries.index_of(full_path)

	@implements
	def source_map(self, full_path: str) -> SourceMap:
		"""指定のパスのエントリーのソースマップを取得

		Args:
			full_path (str): フルパス
		Returns:
			SourceMap: ソースマップ
		"""
		return self.__entries.by(full_path).source_map
