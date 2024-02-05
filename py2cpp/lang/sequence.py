from itertools import chain
from typing import Any, Sequence, TypeVar, cast

T = TypeVar('T')


flatten = chain.from_iterable


def index_of(seq: Sequence[T], elem: T) -> int:
	"""指定の要素を検出した初めのインデックスを返却。未検出の場合は-1を返却

	Args:
		seq (Sequence[T]): リスト
		elem (T): 検索対象の要素
	Returns:
		int: インデックス
	"""
	return seq.index(elem) if elem in seq else -1


def last_index_of(seq: Sequence[T], elem: T) -> int:
	"""指定の要素を検出した最後のインデックスを返却。未検出の場合は-1を返却

	Args:
		seq (Sequence[T]): リスト
		elem (T): 検索対象の要素
	Returns:
		int: インデックス
	"""
	return (len(seq) - 1) - list(reversed(seq)).index(elem) if elem in seq else -1


def unwrap(entry: list[T] | dict[str, T] | T, path: str = '') -> dict[str, T]:
	"""list/dictを直列に展開

	Args:
		entry (list[T] | dict[str, T] | T): エントリー
	Returns:
		dict[str, T]: マッピング情報
	"""
	entries: dict[str, T] = {}
	if type(entry) is list:
		for index, elem in enumerate(entry):
			routes = [e for e in [path, str(index)] if e]
			in_path = '.'.join(routes)
			entries = {**entries, **unwrap(elem, in_path)}
	elif type(entry) is dict:
		for key, elem in entry.items():
			routes = [e for e in [path, key] if e]
			in_path = '.'.join(routes)
			entries = {**entries, **unwrap(elem, in_path)}
	else:
		entries[path] = cast(T, entry)

	return entries


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


def update(entry: list | dict, path: str, value: Any) -> None:
	"""list/dictの指定パスの値を更新

	Args:
		entry (list | dict): エントリー
		path (str): 更新対象のパス
		value (Any): 更新値
	"""
	index, *remain = path.split('.')
	if not len(remain):
		entry[int(index)] = value
	else:
		update(entry[int(index)], '.'.join(remain), value)
