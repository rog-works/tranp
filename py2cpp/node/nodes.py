import re
from typing import Callable

from lark import Tree

from py2cpp.lang.annotation import implements
from py2cpp.node.node import Node
from py2cpp.node.provider import Query, Resolver, Settings
from py2cpp.tp_lark.travarsal import entry_exists, escaped_path, denormalize_tag, find_entries, pluck_entry, tag_by_entry
from py2cpp.tp_lark.types import Entry


class NodeResolver:
	"""ノードリゾルバー。解決したノードとパスをマッピングして管理"""

	@classmethod
	def load(cls, settings: Settings[Node]) -> 'NodeResolver':
		"""設定データを元にインスタンスを生成

		Args:
			settings (Settings[Node]): 設定データ
		Returns:
			NodeResolver: 生成したインスタンス
		"""
		return cls(Resolver[Node].load(settings))


	def __init__(self, resolver: Resolver[Node]) -> None:
		"""インスタンスを生成

		Args:
			resolver (Resolver[Node]): 型リゾルバー
		"""
		self.__resolver = resolver
		self.__insts: dict[str, Node] = {}


	def can_resolve(self, symbol: str) -> bool:
		"""解決出来るか確認

		Args:
			symbol (str): シンボル名
		Returns:
			bool: True = 解決できる
		"""
		return self.__resolver.can_resolve(symbol)


	def resolve(self, symbol: str, full_path: str, factory: Callable[[type[Node]], Node]) -> Node:
		"""ノードのインスタンスを解決

		Args:
			symbol (str): シンボル
			full_path (str): エントリーのフルパス
			factory (Callable[[type[Node]], Node]): インスタンスファクトリー
		Returns:
			Node: 解決したノード
		Raises:
			ValueError: シンボルの解決に失敗
		"""
		if full_path in self.__insts:
			return self.__insts[full_path]

		ctor = self.__resolver.resolve(symbol)
		self.__insts[full_path] = factory(ctor).actual()
		return self.__insts[full_path]


	def clear(self) -> None:
		"""インスタンスのマッピング情報を削除"""
		self.__insts = {}


class Nodes(Query[Node]):
	"""ノードクエリーインターフェイス。ASTを元にノードの探索し、リゾルバーを介してインスタンスを解決"""

	def __init__(self, root: Tree, resolver: NodeResolver) -> None:
		"""インスタンスを生成

		Args:
			root (Tree): AST
			resolver (NodeResolver): ノードリゾルバー
		"""
		self.__root = root
		self.__resolver = resolver


	def __resolve(self, entry: Entry, full_path: str) -> Node:
		"""エントリーからノードを解決し、パスとマッピングしてキャッシュ

		Args:
			entry (Entry): エントリー
			full_path (str): エントリーのフルパス
		Returns:
			Node: 解決したノード
		"""
		return self.__resolver.resolve(tag_by_entry(entry), full_path, lambda ctor: ctor(self, entry, full_path))


	@implements
	def exists(self, full_path: str) -> bool:
		"""指定のパスに紐づく一意なノードが存在するか判定

		Args:
			full_path (str): フルパス
		Returns:
			bool: True = 存在
		"""
		return entry_exists(self.__root, full_path)


	@implements
	def at(self, full_path: str) -> Node:
		"""指定のパスに紐づく一意なノードをフェッチ

		Args:
			full_path (str): フルパス
		Returns:
			Node: ノード
		Raises:
			ValueError: ノードが存在しない
		"""
		entry = pluck_entry(self.__root, full_path)
		return self.__resolve(entry, full_path)


	@implements
	def parent(self, via: str) -> Node:
		"""指定のパスを子として親のノードをフェッチ

		Args:
			via (str): 基準のパス
		Returns:
			Node: ノード
		Raises:
			ValueError: 親が存在しない
		"""
		forwards = via.split('.')[:-1]
		while(len(forwards)):
			org_tag = forwards.pop()
			tag = denormalize_tag(org_tag)
			if self.__resolver.can_resolve(tag):
				path = '.'.join([*forwards, org_tag])
				return self.at(path)

		raise ValueError()


	@implements
	def siblings(self, via: str) -> list[Node]:
		"""指定のパスを基準に同階層のノードをフェッチ

		Args:
			via (str): 基準のパス(フルパス)
		Returns:
			list[Node]: ノードリスト
		"""
		uplayer_path = '.'.join(via.split('.')[:-1])
		regular = re.compile(rf'{escaped_path(uplayer_path)}\.[^.]+')
		tester = lambda _, path: regular.fullmatch(path) is not None
		entries = find_entries(self.__root, uplayer_path, tester, depth=1)
		return [self.__resolve(entry, path) for path, entry in entries.items()]


	@implements
	def children(self, via: str) -> list[Node]:
		"""指定のパスを基準に1階層下のノードをフェッチ

		Args:
			via (str): 基準のパス(フルパス)
		Returns:
			list[Node]: ノードリスト
		"""
		regular = re.compile(rf'{escaped_path(via)}\.[^.]+')
		tester = lambda _, path: regular.fullmatch(path) is not None
		entries = find_entries(self.__root, via, tester, depth=1)
		return [self.__resolve(entry, path) for path, entry in entries.items()]


	@implements
	def leafs(self, via: str, leaf_tag: str) -> list[Node]:
		"""指定のパスから下に存在する接尾辞が一致するノードをフェッチ

		Args:
			via (str): 基準のパス(フルパス)
			leaf_name (str): 接尾辞
		Returns:
			list[Node]: ノードリスト
		"""
		regular = re.compile(rf'{escaped_path(via)}\.(.+\.)?{leaf_tag}(\[\d+\])?')
		tester = lambda _, path: regular.fullmatch(path) is not None
		entries = find_entries(self.__root, via, tester)
		return [self.__resolve(entry, path) for path, entry in entries.items()]


	@implements
	def expansion(self, via: str) -> list[Node]:
		"""指定のパスから下に存在する展開が可能なノードをフェッチ

		Args:
			via (str): 基準のパス(フルパス)
		Returns:
			list[Node]: ノードリスト
		"""
		memo: list[str] = []
		def tester(entry: Entry, path: str) -> bool:
			if via == path:
				return False

			# 記録済みの変換対象以降の要素は全て除外
			if len([cached for cached in memo if path.startswith(cached)]):
				return False

			# XXX 変換対象が存在する場合はそちらに対応を任せる(終端記号か否かは問わない)
			entry_tag = denormalize_tag(path.split('.').pop())
			if self.__resolver.can_resolve(entry_tag):
				memo.append(path)
				return True

			if type(entry) is Tree:
				return False

			# 自身を含む配下のエントリーに変換対象のノードがなく、Terminalにフォールバックされる終端記号が対象
			_, remain = path.split(via)
			in_allows = [
				index
				for index, in_org_tag in enumerate(remain.split('.'))
				if self.__resolver.can_resolve(denormalize_tag(in_org_tag))
			]
			return len(in_allows) == 0

		entries = find_entries(self.__root, via, tester)
		return [self.__resolve(entry, path) for path, entry in entries.items()]


	@implements
	def embed(self, via: str, entry_tag: str) -> Node:
		"""指定のパスの下に仮想のノードを生成

		Args:
			via (str): 基準のパス(フルパス)
			entry_tag (str): 仮想エントリーのタグ名前
		Returns:
			Node: 生成した仮想ノード
		Note:
			@deprecated
			理由:
				* 同じパスのノードが存在するとキャッシュが壊れる
				* ASTに存在しないため、既存のパス検索で検索出来ない
		"""
		entry = pluck_entry(self.__root, via)
		full_path = f'{via}.{entry_tag}'
		return self.__resolve(entry, full_path)  # FIXME 同じパスのノードがいた場合に壊れる可能性大
