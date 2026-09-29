from typing import Any, TypeAlias

_Node: TypeAlias = int | float | str | dict | list


def dict_pluck(node: _Node, path: str, fallback: _Node = '') -> _Node:
	"""指定のパスのエントリーの値を抜き出す

	Args:
		node: エントリー
		path: パス
		fallback: 存在しない場合の代用値 (default = '')
	Returns:
		エントリーの値
	"""
	if type(node) is dict and path:
		key, *remain = path.split('.')
		if key not in node:
			return fallback

		return dict_pluck(node[key], '.'.join(remain))
	elif type(node) is list and path:
		key, *remain = path.split('.')
		index = int(key)
		if index not in node:
			return fallback

		return dict_pluck(node[index], '.'.join(remain))
	else:
		return node


def dict_merge(d1: dict[Any, Any], d2: dict[Any, Any]) -> dict[Any, Any]:
	"""連想配列同士をディープマージ

	Args:
		d1: 連想配列1
		d2: 連想配列2
	Returns:
		結合後の連想配列
	"""
	merged = d1.copy()
	for key, value in d2.items():
		if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
			merged[key] = dict_merge(merged[key], value)
		else:
			merged[key] = value

	return merged
