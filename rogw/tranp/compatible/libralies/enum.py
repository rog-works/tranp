from collections.abc import Iterator
from typing import Any, Self


class EnumType: ...


class Enum:
	name: str
	value: Any

	def __init__(self, value: Any) -> None:
		self.name = ''
		# FIXME 全く正しくないが実用上は問題ないため一旦これで良しとする
		self.value = value

	@classmethod
	def __iter__(cls: type[Self]) -> Iterator[Self]: ...

	# comparison
	def __eq__(self, other: Any) -> bool: ...
	def __ne__(self, other: Any) -> bool: ...
	def __not__(self, other: Any) -> bool: ...
