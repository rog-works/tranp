from collections.abc import Iterator


class InvalidOps:
	def tenary_to_union_types(self) -> None:
		n_or_s = 1 if True else ''

	def param_of_raw_or_null(self, base: int | None) -> None: ...
	def return_of_raw_or_null(self) -> int | None: ...

	def yield_return(self) -> Iterator[int]:
		yield 0

	def delete_relay(self) -> None:
		del self.delete_relay

	def destruction_assign(self) -> None:
		a, b = [1, 2]
