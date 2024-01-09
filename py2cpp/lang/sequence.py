from itertools import chain
from typing import Sequence, TypeVar

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
