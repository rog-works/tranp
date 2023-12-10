import re
from typing import Callable, cast, TypeAlias

from lark import Token, Tree

from py2cpp.tp_lark.types import Entry

T_Tester: TypeAlias = Callable[[Entry, str], bool]


def normalize_tag(entry_tag: str, index: int) -> str:
	"""タグ名にインデックスを付与

	Args:
		entry_tag (str): エントリータグ名
		index (int): インデックス
	Returns:
		str: 付与後のエントリータグ名
	Note:
		書式: ${entry_tag}[${index}]
	"""
	return f'{entry_tag}[{index}]'


def denormalize_tag(entry_tag: str) -> str:
	"""タグ名に付与されたインデックスを除外

	Args:
		entry_tag (str): エントリータグ名
	Returns:
		str: 元のエントリータグ名
	"""
	return break_tag(entry_tag)[0]


def break_tag(entry_tag: str) -> tuple[str, int]:
	"""タグ名から元のタグ名と付与されたインデックスに分解。インデックスがない場合は-1とする

	Args:
		entry_tag (str): エントリータグ名
	Returns:
		tuple[str, int]: (エントリータグ名, インデックス)
	"""
	matches = re.fullmatch(r'(\w+)\[(\d+)\]', entry_tag)
	return (matches[1], int(matches[2])) if matches else (entry_tag, -1)


def escaped_path(path: str) -> str:
	"""パスを正規表現用にエスケープ

	Args:
		pash (str): パス
	Returns:
		str: エスケープ後のパス
	"""
	return re.sub(r'([.\[\]])', r'\\\1', path)


def __without_root_path(full_path: str) -> str:
	"""フルパスからルート要素を除外した相対パスに変換

	Args:
		full_path (str): フルパス
	Returns:
		str: ルート要素からの相対パス
	"""
	return '.'.join(full_path.split('.')[1:])


def tag_by_entry(entry: Entry) -> str:
	"""エントリーのタグ名を取得

	Args:
		entry (Entry): エントリー
	Returns:
		str: タグ名
	"""
	if type(entry) is Tree:
		return entry.data
	elif type(entry) is Token:
		return entry.type
	else:
		return '__empty__'


def entry_exists(root: Entry, full_path: str) -> bool:
	"""指定のパスに一致するエントリーが存在するか判定

	Args:
		root (Entry): ルートエントリー
		full_path (str): フルパス
	Returns:
		bool: True = 存在
	"""
	try:
		pluck_entry(root, full_path)
		return True
	except ValueError:
		return False


def pluck_entry(root: Entry, full_path: str) -> Entry:
	"""指定のパスに一致するエントリーを抜き出す

	Args:
		root (Entry): ルートエントリー
		full_path (str): 抜き出すエントリーのフルパス
	Returns:
		Entry: エントリー
	Raise:
		ValueError: エントリーが存在しない
	"""
	if tag_by_entry(root) == full_path:
		return root

	return __pluck_entry(root, __without_root_path(full_path))


def __pluck_entry(entry: Entry, path: str) -> Entry:
	"""配下のエントリーから指定のパスに一致するエントリーを抜き出す

	Args:
		entry (Entry): エントリー
		path (str): 引数のエントリーからの相対パス
	Returns:
		Entry: エントリー
	Note:
		@see pluck_entry
	Raise:
		ValueError: エントリーが存在しない
	"""
	if type(entry) is Tree and path:
		org_tag, *remain = path.split('.')
		tag, index = break_tag(org_tag)
		# XXX @see break_tag, pathfy
		if index != -1:
			if index >= 0 and index < len(entry.children):
				return __pluck_entry(entry.children[index], '.'.join(remain))
		else:
			in_entries = [in_entry for in_entry in entry.children if tag == tag_by_entry(in_entry)]
			if len(in_entries):
				return __pluck_entry(in_entries.pop(), '.'.join(remain))
	elif not path:
		return entry

	raise ValueError()


def find_entries(root: Entry, via: str, tester: T_Tester, depth: int = -1) -> dict[str, Entry]:
	"""基点のパス以下のエントリーを検索

	Args:
		root (Entry): ルートエントリー
		via (str): 探索基点のフルパス
		tester (T_Tester): 検索条件
		depth (int): 探索深度(-1: 無制限)
	Returns:
		dict[str, Entry]: フルパスとエントリーのマップ
	"""
	entry = pluck_entry(root, via)
	all = full_pathfy(entry, via, depth)
	return {in_path: in_entry for in_path, in_entry in all.items() if tester(in_entry, in_path)}


def full_pathfy(entry: Entry, path: str = '', depth: int = -1) -> dict[str, Entry]:
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
		path = tag_by_entry(entry)

	in_paths = {path: entry}
	if depth == 0:
		return in_paths

	if type(entry) is Tree:
		tag_of_indexs = __aligned_children(entry.children)
		for index, in_entry in enumerate(entry.children):
			# XXX 同名の要素が並ぶか否かでパスの書式を変更
			# XXX n == 1: {path}.{tag}
			# XXX n >= 2: {path}.{tag}[{index}]
			# XXX @see normalize_tag, pluck
			entry_tag = tag_by_entry(in_entry)
			indivisual = len(tag_of_indexs[entry_tag]) == 1
			in_path = f'{path}.{entry_tag}' if indivisual else f'{path}.{normalize_tag(entry_tag, index)}'
			in_paths = {**in_paths, **full_pathfy(entry.children[index], in_path, depth - 1)}

	return in_paths


def __aligned_children(children: list[Entry]) -> dict[str, list[int]]:
	"""子の要素を元にタグ名毎のインデックスリストに整理する

	Args:
		children (list[Entry]): 子の要素リスト
	Returns:
		dict[str, list[int]]: タグ名毎のインデックスリスト
	"""
	index_of_tags = {index: tag_by_entry(in_entry) for index, in_entry in enumerate(children)}
	tag_of_indexs: dict[str, list[int]]  = {tag: [] for tag in index_of_tags.values()}
	for tag in tag_of_indexs.keys():
		tag_of_indexs[tag] = [index for index, in_tag in index_of_tags.items() if tag == in_tag]

	return tag_of_indexs
