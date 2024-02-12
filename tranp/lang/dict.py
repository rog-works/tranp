from typing import TypeAlias

_Node: TypeAlias = int | float | str | dict | list


def pluck(node: _Node, path: str) -> _Node:
	if type(node) is dict and path:
		key, *remain = path.split('.')
		return pluck(node[key], '.'.join(remain))
	elif type(node) is list and path:
		key, *remain = path.split('.')
		index = int(key)
		return pluck(node[index], '.'.join(remain))
	else:
		return node


def deep_merge(d1: dict, d2: dict) -> dict:
	merged = d1.copy()
	for key, value in d2.items():
		if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
			merged[key] = deep_merge(merged[key], value)
		else:
			merged[key] = value

	return merged
