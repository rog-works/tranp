import re
from typing import Callable

from lark import Token, Tree

from py2cpp.ast.travarsal import ASTFinder, EntryPath, EntryProxy
from py2cpp.errors import NotFoundError
from py2cpp.lang.annotation import implements
from py2cpp.node.node import Node
from py2cpp.node.provider import Query, Resolver, Settings
from py2cpp.tp_lark.types import Entry


class EntryProxyLark(EntryProxy[Entry]):
	"""エントリーへの要素アクセスを代替するプロクシー"""

	@implements
	def name(self, entry: Entry) -> str:
		"""名前を取得

		Args:
			entry (Entry): エントリー
		Returns:
			str: エントリーの名前
		Note:
			エントリーが空の場合を考慮すること
			@see is_empty
		"""
		if type(entry) is Tree:
			return entry.data
		elif type(entry) is Token:
			return entry.type
		else:
			return self.empty_name

	@implements
	def has_child(self, entry: Entry) -> bool:
		"""子を持つエントリーか判定

		Args:
			entry (Entry): エントリー
		Returns:
			bool: True = 子を持つエントリー
		"""
		return type(entry) is Tree

	@implements
	def children(self, entry: Entry) -> list[Entry]:
		"""配下のエントリーを取得

		Args:
			entry (Entry): エントリー
		Returns:
			list[Entry]: 配下のエントリーリスト
		Raise:
			ValueError: 子を持たないエントリーで使用
		"""
		if type(entry) is not Tree:
			raise ValueError()

		return entry.children

	@implements
	def is_terminal(self, entry: Entry) -> bool:
		"""終端記号か判定

		Args:
			entry (Entry): エントリー
		Returns:
			bool: True = 終端記号
		"""
		return type(entry) is Token

	@implements
	def value(self, entry: Entry) -> str:
		"""終端記号の値を取得

		Args:
			entry (T): エントリー
		Returns:
			str: 終端記号の値
		Raise:
			ValueError: 終端記号ではないエントリーで使用
		"""
		if type(entry) is not Token:
			raise ValueError()

		return entry.value

	@implements
	def is_empty(self, entry: Entry) -> bool:
		"""エントリーが空か判定

		Returns:
			bool: True = 空
		Note:
			Grammarの定義上存在するが、構文解析の結果で空になったエントリー
			例えば以下の様な関数の定義の場合[parameters]が対象となり、引数がない関数の場合、エントリーとしては存在するが内容は空になる
			例) function_def: "def" name "(" [parameters] ")" "->" ":" block
		"""
		return entry is None


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
			LogicError: シンボルの解決に失敗
		"""
		if full_path in self.__insts:
			return self.__insts[full_path]

		ctor = self.__resolver.resolve(symbol)
		self.__insts[full_path] = factory(ctor).actualize()
		return self.__insts[full_path]

	def clear(self) -> None:
		"""インスタンスのマッピング情報を削除"""
		self.__insts = {}


class EntryCache:
	"""エントリーキャッシュ

	Note:
		グループ検索用のインデックスは、ツリーの先頭から順序通りに登録することが正常動作の必須要件
		効率よくインデックスを構築出来る反面、シンタックスツリーが静的であることを前提とした実装のため、
		インデックスを作り替えることは出来ず、登録順序にも強い制限がある
	"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__entries: list[Entry] = []
		self.__indexs: dict[str, tuple[int, int]] = {}

	def exists(self, full_path: str) -> bool:
		"""指定のパスのエントリーが存在するか判定

		Args:
			full_path (str): フルパス
		Returns:
			bool: True = 存在する
		"""
		return full_path in self.__indexs

	def by(self, full_path: str) -> Entry:
		"""指定のパスのエントリーをフェッチ

		Args:
			full_path (str): フルパス
		Returns:
			Entry: エントリー
		"""
		if not self.exists(full_path):
			raise NotFoundError(full_path)

		begin, _ = self.__indexs[full_path]
		return self.__entries[begin]

	def group_by(self, via: str) -> dict[str, Entry]:
		"""指定の基準パス以下のエントリーをフェッチ

		Args:
			via (str): 基準のパス(フルパス)
		Returns:
			dict[str, Entry]: (フルパス, エントリー)
		"""
		if not self.exists(via):
			raise NotFoundError(via)

		begin, end = self.__indexs[via]
		items = self.__entries[begin:end + 1]
		keys = list(self.__indexs.keys())[begin:end + 1]
		return {keys[index]: items[index] for index in range((end + 1) - begin)}

	def add(self, full_path: str, entry: Entry) -> None:
		"""指定のパスとエントリーを紐付けてキャッシュに追加

		Args:
			full_path (str): フルパス
			entry (str): フルパス
		"""
		if self.exists(full_path):
			return

		begin = len(self.__entries)
		self.__entries.append(entry)
		self.__indexs[full_path] = (begin, begin)

		remain = full_path.split('.')[:-1]
		while len(remain):
			in_key = '.'.join(remain)
			begin, end = self.__indexs[in_key]
			self.__indexs[in_key] = (begin, end + 1)
			remain.pop()


class Nodes(Query[Node]):
	"""ノードクエリーインターフェイス。ASTを元にノードの探索し、リゾルバーを介してインスタンスを解決"""

	def __init__(self, root: Entry, resolver: NodeResolver) -> None:
		"""インスタンスを生成

		Args:
			root (Entry): ASTのルート要素
			resolver (NodeResolver): ノードリゾルバー
		"""
		self.__resolver = resolver
		self.__proxy = EntryProxyLark()
		self.__entries = EntryCache()
		for full_path, entry in ASTFinder(self.__proxy).full_pathfy(root).items():
			self.__entries.add(full_path, entry)

	def __resolve(self, entry: Entry, full_path: str) -> Node:
		"""エントリーからノードを解決し、パスとマッピングしてキャッシュ

		Args:
			entry (Entry): エントリー
			full_path (str): エントリーのフルパス
		Returns:
			Node: 解決したノード
		"""
		return self.__resolver.resolve(self.__proxy.name(entry), full_path, lambda ctor: ctor(self, full_path))

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
			tag, _ = forwards.last()
			if self.__resolver.can_resolve(tag):
				return self.by(forwards.origin)

			forwards = forwards.shift(-1)

		raise NotFoundError(via)

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
	def expansion(self, via: str) -> list[Node]:
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
			entry_tag = entry_path.last()[0]
			if self.__resolver.can_resolve(entry_tag):
				memo.append(entry_path.origin)
				return True

			if self.__proxy.has_child(entry):
				return False

			# 自身を含む配下のエントリーに変換対象のノードがなく、Terminalにフォールバックされる終端記号が対象
			entry_tags = entry_path.relativefy(via).de_identify().elements
			in_allows = [index for index, in_tag in enumerate(entry_tags) if self.__resolver.can_resolve(in_tag)]
			return len(in_allows) == 0

		entries = {path: entry for path, entry in self.__entries.group_by(via).items() if tester(entry, path)}
		return [self.__resolve(entry, path) for path, entry in entries.items()]

	@implements
	def by_value(self, full_path: str) -> str:
		"""指定のエントリーの値を取得

		Args:
			full_path (str): フルパス
		Returns:
			str: 値
		"""
		entry = self.__entries.by(full_path)
		return self.__proxy.value(entry) if self.__proxy.is_terminal(entry) else ''
