from itertools import chain
from typing import Any, Sequence, TypeVar, cast

T_Seq = TypeVar('T_Seq')


flatten = chain.from_iterable


def index_of(seq: Sequence[T_Seq], elem: T_Seq) -> int:
	"""指定の要素を検出した初めのインデックスを返却。未検出の場合は-1を返却

	Args:
		seq (Sequence[T_Seq]): リスト
		elem (T_Seq): 検索対象の要素
	Returns:
		int: インデックス
	"""
	return seq.index(elem) if elem in seq else -1


def last_index_of(seq: Sequence[T_Seq], elem: T_Seq) -> int:
	"""指定の要素を検出した最後のインデックスを返却。未検出の場合は-1を返却

	Args:
		seq (Sequence[T_Seq]): リスト
		elem (T_Seq): 検索対象の要素
	Returns:
		int: インデックス
	"""
	return (len(seq) - 1) - list(reversed(seq)).index(elem) if elem in seq else -1


def expand(entry: list | dict | Any, path: str = '', iter_key: str | None = None) -> dict[str, Any]:
	"""list/dictを直列に展開

	Args:
		entry (list | dict | Any): エントリー
		path (str): 開始パス(default = '')
		iter_key (str | None): イテレーター属性のキー(default = None)
	Returns:
		dict[str, Any]: 展開データ
	"""
	entries: dict[str, Any] = {}
	if type(entry) is list:
		for index, elem in enumerate(entry):
			routes = [e for e in [path, str(index)] if e]
			in_path = '.'.join(routes)
			entries = {**entries, **expand(elem, in_path, iter_key)}
	elif type(entry) is dict:
		for iter_key, elem in entry.items():
			routes = [e for e in [path, iter_key] if e]
			in_path = '.'.join(routes)
			entries = {**entries, **expand(elem, in_path, iter_key)}
	else:
		entries[path] = entry
		if iter_key and hasattr(entry, iter_key):
			for index, elem in enumerate(getattr(entry, iter_key)):
				routes = [e for e in [path, str(index)] if e]
				in_path = '.'.join(routes)
				entries = {**entries, **expand(elem, in_path, iter_key)}

	return entries


def update(entry: list | dict, path: str, value: Any, iter_key: str | None = None) -> None:
	"""list/dictの指定パスの値を更新

	Args:
		entry (list | dict): エントリー
		path (str): 更新対象のパス
		value (Any): 更新値
		iter_key (str | None): イテレーター属性のキー(default = None)
	"""
	key, *remain = path.split('.')
	if len(remain):
		remain_path = '.'.join(remain)
		if type(entry) is list:
			update(entry[int(key)], remain_path, value, iter_key)
		elif type(entry) is dict:
			update(entry[key], remain_path, value, iter_key)
		elif iter_key:
			update(getattr(entry, iter_key)[int(key)], remain_path, value, iter_key)
	else:
		if type(entry) is list:
			entry[int(key)] = value
		elif type(entry) is dict:
			entry[key] = value
		elif iter_key:
			getattr(entry, iter_key)[int(key)] = value


def deep_copy(entry: list | dict) -> list | dict:
	"""list/dictを再帰的に複製

	Args:
		entry (list | dict): エントリー
	Returns:
		list | dict: 複製
	"""
	if type(entry) is list:
		new = []
		for elem in entry:
			if type(elem) is list:
				new.append(deep_copy(elem))
			elif type(elem) is dict:
				new.append(deep_copy(elem))
			else:
				new.append(elem)

		return new
	else:
		new = {}
		for key, elem in cast(dict, entry).items():
			if type(elem) is list:
				new[key] = deep_copy(elem)
			elif type(elem) is dict:
				new[key] = deep_copy(elem)
			else:
				new[key] = elem

		return new
