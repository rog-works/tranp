from typing import Any, TypeVar, cast

from py2cpp.errors import LogicError
from py2cpp.node.node import Node

T = TypeVar('T')


def serialize(node: Node, schema: type[T]) -> T:
	"""指定のスキーマを元にノードをdictにシリアライズ

	Args:
		node (Node): ノード
		schema (type[T]): シリアライズスキーマ
	Returns:
		T: シリアライズしたdict
	"""
	out = {
		in_key: __serialize_value(getattr(node, in_key), in_schema)
		for in_key, in_schema in schema.__annotations__.items()
	}
	return cast(T, out)


def __serialize_value(value: list[Node] | Node, schema: type) -> Any:
	"""指定のスキーマを元にノードをdictにシリアライズ

	Args:
		value (list[Node] | Node): ノード
		schema (type[T]): シリアライズスキーマ
	Returns:
		Any: シリアライズした値
	"""
	if hasattr(schema, '__annotations__') and isinstance(value, Node):
		return serialize(value, schema)
	elif hasattr(schema, '__origin__') and getattr(schema, '__origin__') is list and type(value) is list:
		return [__serialize_value(elem, getattr(schema, '__args__')[0]) for elem in value]
	elif schema is str and isinstance(value, Node):
		return value.to_string()
	elif schema is str and type(value) is str:
		return value

	raise LogicError(value, schema)
