from typing import Any, TypeVar, cast

from py2cpp.errors import LogicError
from py2cpp.node.node import Node

T = TypeVar('T')


def serialize(node: Node, schema: type[T]) -> T:
	out = {
		in_key: __serialize_value(getattr(node, in_key), in_schema)
		for in_key, in_schema in schema.__annotations__.items()
	}
	return cast(T, out)


def __serialize_value(value: list[Node] | dict[str, Node] | Node, schema: type) -> Any:
	if hasattr(schema, '__annotations__') and isinstance(value, Node):
		return serialize(value, schema)
	elif hasattr(schema, '__origin__'):
		origin = getattr(schema, '__origin__')
		if origin is list and type(value) is list:
			return [__serialize_value(elem, getattr(schema, '__args__')[0]) for elem in value]
		elif origin is dict and type(value) is dict:
			return {key: __serialize_value(value, getattr(schema, '__args__')[1]) for key, value in value.items()}
	elif schema is str and isinstance(value, Node):
		return value.to_string()

	raise LogicError(value, schema)
