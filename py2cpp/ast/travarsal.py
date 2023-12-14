from abc import ABCMeta, abstractmethod
import re
from typing import Callable, Generic, TypeVar

from py2cpp.errors import LogicError, NotFoundError

T = TypeVar('T')


class EntryPath:
	@classmethod
	def join(cls, *paths: str) -> 'EntryPath':
		return cls('.'.join([*paths]))


	@classmethod
	def identify(cls, origin: str, entry_tag: str, index: int) -> 'EntryPath':
		return cls('.'.join([origin, f'{entry_tag}[{index}]']))


	def __init__(self, origin: str) -> None:
		self.origin = origin


	@property
	def valid(self) -> bool:
		return len(self.elements) > 0


	@property
	def elements(self) -> list[str]:
		return self.origin.split('.') if len(self.origin) > 0 else []


	@property
	def escaped_origin(self) -> str:
		"""パスを正規表現用にエスケープ

		Args:
			pash (str): パス
		Returns:
			str: エスケープ後のパス
		"""
		return re.sub(r'([.\[\]])', r'\\\1', self.origin)


	def first(self) -> tuple[str, int]:
		return self.__break_tag(self.elements[0])


	def last(self) -> tuple[str, int]:
		return self.__break_tag(self.elements[-1])


	def __break_tag(self, entry_tag: str) -> tuple[str, int]:
		"""タグ名から元のタグ名と付与されたインデックスに分解。インデックスがない場合は-1とする

		Args:
			entry_tag (str): エントリータグ名
		Returns:
			tuple[str, int]: (エントリータグ名, インデックス)
		"""
		matches = re.fullmatch(r'(\w+)\[(\d+)\]', entry_tag)
		return (matches[1], int(matches[2])) if matches else (entry_tag, -1)


	def shift(self, skip: int) -> 'EntryPath':
		elems = self.elements
		if skip > 0:
			elems = elems[skip:]
		elif skip < 1:
			elems = elems[:skip]

		return self.join(*elems)


	def contains(self, entry_tag: str) -> bool:
		return entry_tag in self.de_identify().elements


	def consists_of_only(self, *entry_tags: str) -> bool:
		return len([entry_tag for entry_tag in self.de_identify().elements if entry_tag not in entry_tags]) == 0


	def de_identify(self) -> 'EntryPath':
		return EntryPath(re.sub(r'\[\d+\]', '', self.origin))


	def relativefy(self, before: str) -> 'EntryPath':
		if not self.origin.startswith(before):
			raise LogicError(self, before)

		elems = [elem for elem in self.origin.split(before)[1].split('.') if len(elem)]
		return EntryPath('.'.join(elems))


class EntryProxy(Generic[T], metaclass=ABCMeta):
	"""エントリーへの要素アクセスを代替するプロクシー"""

	@abstractmethod
	def name(self, entry: T) -> str:
		"""名前を取得

		Args:
			entry (T): エントリー
		Returns:
			str: エントリーの名前
		Note:
			エントリーが空の場合を考慮すること
			@see is_empty
		"""
		raise NotImplementedError()


	@abstractmethod
	def has_child(self, entry: T) -> bool:
		"""子を持つエントリーか判定

		Args:
			entry (T): エントリー
		Returns:
			bool: True = 子を持つエントリー
		"""
		raise NotImplementedError()


	@abstractmethod
	def children(self, entry: T) -> list[T]:
		"""配下のエントリーを取得

		Args:
			entry (T): エントリー
		Returns:
			list[T]: 配下のエントリーリスト
		Raise:
			LogicError: 子を持たないエントリーで使用
		"""
		raise NotImplementedError()


	@abstractmethod
	def is_terminal(self, entry: T) -> bool:
		"""終端記号か判定

		Args:
			entry (T): エントリー
		Returns:
			bool: True = 終端記号
		"""
		raise NotImplementedError()


	@abstractmethod
	def value(self, entry: T) -> str:
		"""終端記号の値を取得

		Args:
			entry (T): エントリー
		Returns:
			str: 終端記号の値
		Raise:
			LogicError: 終端記号ではないエントリーで使用
		"""
		raise NotImplementedError()


	@abstractmethod
	def is_empty(self, entry: T) -> bool:
		"""エントリーが空か判定

		Returns:
			bool: True = 空
		Note:
			Grammarの定義上存在するが、構文解析の結果で空になったエントリー
			例えば以下の様な関数の定義の場合[parameters]が対象となり、引数がない関数の場合、エントリーとしては存在するが内容は空になる
			例) function_def: "def" name "(" [parameters] ")" "->" ":" block
		"""
		raise NotImplementedError()


	@property
	def empty_name(self) -> str:
		"""str: 空のエントリー名"""
		return '__empty__'


class ASTFinder(Generic[T]):
	"""AST探索インターフェイス"""

	def __init__(self, proxy: EntryProxy[T]) -> None:
		"""インスタンスを生成

		Args:
			proxy (EntryProxy): エントリープロクシー
		"""
		self.__proxy = proxy


	@classmethod
	def escaped_path(cls, path: str) -> str:
		"""パスを正規表現用にエスケープ

		Args:
			pash (str): パス
		Returns:
			str: エスケープ後のパス
		"""
		return re.sub(r'([.\[\]])', r'\\\1', path)


	def has_child(self, entry: T) -> bool:
		"""子を持つエントリーか判定

		Args:
			entry (T): エントリー
		Returns:
			bool: True = 子を持つエントリー
		"""
		return self.__proxy.has_child(entry)


	def tag_by(self, entry: T) -> str:
		"""エントリーのタグ名を取得

		Args:
			entry (Entry): エントリー
		Returns:
			str: タグ名
		"""
		return self.__proxy.name(entry)


	def exists(self, root: T, full_path: str) -> bool:
		"""指定のパスに一致するエントリーが存在するか判定

		Args:
			root (Entry): ルートエントリー
			full_path (str): フルパス
		Returns:
			bool: True = 存在
		"""
		try:
			self.pluck(root, full_path)
			return True
		except NotFoundError:
			return False


	def pluck(self, root: T, full_path: str) -> T:
		"""指定のパスに一致するエントリーを抜き出す

		Args:
			root (Entry): ルートエントリー
			full_path (str): 抜き出すエントリーのフルパス
		Returns:
			Entry: エントリー
		Raise:
			NotFoundError: エントリーが存在しない
		"""
		if self.tag_by(root) == full_path:
			return root

		return self.__pluck(root, EntryPath(full_path).shift(1))


	def __pluck(self, entry: T, path: EntryPath) -> T:
		"""配下のエントリーから指定のパスに一致するエントリーを抜き出す

		Args:
			entry (Entry): エントリー
			path (EntryPath): 引数のエントリーからの相対パス
		Returns:
			Entry: エントリー
		Note:
			@see pluck
		Raise:
			NotFoundError: エントリーが存在しない
		"""
		if self.__proxy.has_child(entry) and path.valid:
			tag, index = path.first()
			remain = path.shift(1)
			# @see EntryPath.identify
			if index != -1:
				children = self.__proxy.children(entry)
				if index >= 0 and index < len(children):
					return self.__pluck(children[index], remain)
			else:
				children = self.__proxy.children(entry)
				in_entries = [in_entry for in_entry in children if tag == self.tag_by(in_entry)]
				if len(in_entries):
					return self.__pluck(in_entries.pop(), remain)
		elif not path.valid:
			return entry

		raise NotFoundError(entry, path)


	def find(self, root: T, via: str, tester: Callable[[T, str], bool], depth: int = -1) -> dict[str, T]:
		"""基点のパス以下のエントリーを検索

		Args:
			root (Entry): ルートエントリー
			via (str): 探索基点のフルパス
			tester (Callable[[T, str], bool]): 検索条件
			depth (int): 探索深度(-1: 無制限)
		Returns:
			dict[str, Entry]: フルパスとエントリーのマップ
		Raises:
			NotFoundError: 基点のエントリーが存在しない
		"""
		entry = self.pluck(root, via)
		all = self.full_pathfy(entry, via, depth)
		return {in_path: in_entry for in_path, in_entry in all.items() if tester(in_entry, in_path)}


	def full_pathfy(self, entry: T, path: str = '', depth: int = -1) -> dict[str, T]:
		"""指定のエントリー以下のフルパスとマッピングを生成

		Args:
			entry (entry): エントリー
			path (str): 引数のエントリーのフルパス
			depth (int): 探索深度(-1: 無制限)
		Returns:
			dict[str, Entry]: フルパスとエントリーのマップ
		Note:
			引数のpathには必ずルート要素からのフルパスを指定すること
			相対パスを指定してこの関数を実行すると、本来のフルパスとの整合性が取れなくなる点に注意
			例)
				フルパス時: tree_a.tree_b[1].token
				相対パス時: tree_b.token ※1
				※1 相対の場合、tree_bを基点とすると、インデックスの情報が欠損するため結果が変わる
		"""
		# XXX パスが無い時点はルート要素と見做してパスを設定する
		if not len(path):
			path = self.tag_by(entry)

		in_paths = {path: entry}
		if depth == 0:
			return in_paths

		if self.__proxy.has_child(entry):
			children = self.__proxy.children(entry)
			tag_of_indexs = self.__aligned_children(children)
			for index, in_entry in enumerate(children):
				# 同名の要素が並ぶか否かでパスの書式を変更
				# @see EntryPath.identify
				entry_tag = self.tag_by(in_entry)
				indivisual = len(tag_of_indexs[entry_tag]) == 1
				in_path = EntryPath.join(path, entry_tag) if indivisual else EntryPath.identify(path, entry_tag, index)
				in_paths = {**in_paths, **self.full_pathfy(children[index], in_path.origin, depth - 1)}

		return in_paths


	def __aligned_children(self, children: list[T]) -> dict[str, list[int]]:
		"""子の要素を元にタグ名毎のインデックスリストに整理する

		Args:
			children (list[Entry]): 子の要素リスト
		Returns:
			dict[str, list[int]]: タグ名毎のインデックスリスト
		"""
		index_of_tags = {index: self.tag_by(in_entry) for index, in_entry in enumerate(children)}
		tag_of_indexs: dict[str, list[int]]  = {tag: [] for tag in index_of_tags.values()}
		for tag in tag_of_indexs.keys():
			tag_of_indexs[tag] = [index for index, in_tag in index_of_tags.items() if tag == in_tag]

		return tag_of_indexs
