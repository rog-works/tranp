from collections.abc import Callable

from rogw.tranp.errors import NotFoundError
from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.path import EntryPath


class ASTFinder:
	"""AST探索インターフェイス"""

	def exists(self, root: Entry, full_path: str) -> bool:
		"""指定のパスに一致するエントリーが存在するか判定

		Args:
			root: ルートエントリー
			full_path: フルパス
		Returns:
			True = 存在
		"""
		try:
			self.pluck(root, full_path)
			return True
		except NotFoundError:
			return False

	def pluck(self, root: Entry, full_path: str) -> Entry:
		"""指定のパスに一致するエントリーを抜き出す

		Args:
			root: ルートエントリー
			full_path: 抜き出すエントリーのフルパス
		Returns:
			エントリー
		Raise:
			NotFoundError: エントリーが存在しない
		"""
		if root.name == full_path:
			return root

		return self.__pluck(root, EntryPath(full_path).shift(1))

	def __pluck(self, entry: Entry, path: EntryPath) -> Entry:
		"""配下のエントリーから指定のパスに一致するエントリーを抜き出す

		Args:
			entry: エントリー
			path: 引数のエントリーからの相対パス
		Returns:
			エントリー
		Note:
			@see pluck
		Raise:
			NotFoundError: エントリーが存在しない
		"""
		if entry.has_child and path.valid:
			tag, index = path.first
			remain = path.shift(1)
			# @see EntryPath.identify
			if index != -1:
				children = entry.children
				if index >= 0 and index < len(children):
					return self.__pluck(children[index], remain)
			else:
				children = entry.children
				in_entries = [in_entry for in_entry in children if tag == in_entry.name]
				if len(in_entries):
					return self.__pluck(in_entries.pop(), remain)
		elif not path.valid:
			return entry

		raise NotFoundError(entry, path)

	def find(self, root: Entry, via: str, tester: Callable[[Entry, str], bool], depth: int = -1) -> dict[str, Entry]:
		"""基点のパス以下のエントリーを検索

		Args:
			root: ルートエントリー
			via: 探索基点のフルパス
			tester: 検索条件
			depth: 探索深度(-1: 無制限)
		Returns:
			フルパスとエントリーのマップ
		Raises:
			NotFoundError: 基点のエントリーが存在しない
		"""
		entry = self.pluck(root, via)
		all = self.full_pathfy(entry, via, depth)
		return {in_path: in_entry for in_path, in_entry in all.items() if tester(in_entry, in_path)}

	def full_pathfy(self, entry: Entry, path: str = '', depth: int = -1) -> dict[str, Entry]:
		"""指定のエントリー以下のフルパスとマッピングを生成

		Args:
			entry: エントリー
			path: 引数のエントリーのフルパス
			depth: 探索深度(-1: 無制限)
		Returns:
			フルパスとエントリーのマップ
		Note:
			```
			引数のpathには必ずルート要素からのフルパスを指定すること
			相対パスを指定してこの関数を実行すると、本来のフルパスとの整合性が取れなくなる点に注意
			例)
				フルパス時: tree_a.tree_b[1].token
				相対パス時: tree_b.token ※1
				※1 相対の場合、tree_bを基点とすると、インデックスの情報が欠損するため結果が変わる
			```
		"""
		# XXX パスが無い時点はルート要素と見做してパスを設定する
		if not len(path):
			path = entry.name

		in_paths = {path: entry}
		if depth == 0:
			return in_paths

		if entry.has_child:
			children = entry.children
			tag_of_indexs = self.__aligned_children(children)
			for index, in_entry in enumerate(children):
				# 同名の要素が並ぶか否かでパスの書式を変更
				# @see EntryPath.identify
				entry_tag = in_entry.name
				indivisual = len(tag_of_indexs[entry_tag]) == 1
				in_path = EntryPath.join(path, entry_tag) if indivisual else EntryPath.identify(path, entry_tag, index)
				in_paths = {**in_paths, **self.full_pathfy(children[index], in_path.origin, depth - 1)}

		return in_paths

	def __aligned_children(self, children: list[Entry]) -> dict[str, list[int]]:
		"""子の要素を元にエントリータグ毎のインデックスリストに整理する

		Args:
			children: 子の要素リスト
		Returns:
			エントリータグ毎のインデックスリスト
		"""
		index_of_tags = {index: in_entry.name for index, in_entry in enumerate(children)}
		tag_of_indexs: dict[str, list[int]]  = {tag: [] for tag in index_of_tags.values()}
		for tag in tag_of_indexs.keys():
			tag_of_indexs[tag] = [index for index, in_tag in index_of_tags.items() if tag == in_tag]

		return tag_of_indexs
