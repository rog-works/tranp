from rogw.tranp.compatible.cpp.embed import __allow_override__, __embed__, __struct__
from rogw.tranp.compatible.cpp.object import CP

class Base: ...

class InvalidOps:
	def tenary_to_union_types(self, a: Base, ap: CP[Base]) -> None:
		a_or_ap = a if True else ap

	def param_of_raw_or_null(self, base: Base | None) -> None: ...
	def return_of_raw_or_null(self) -> Base | None: ...
