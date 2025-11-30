from enum import Enum

from rogw.tranp.compatible.python.embed import Embed


class E(Enum):
	Alias = 'name'


class A:
	def a(self) -> None: ...
	@Embed.alias(a.__name__)
	def b_to_a(self) -> None: ...
	@Embed.alias(E.Alias.value)
	def c_to_name(self) -> None: ...
