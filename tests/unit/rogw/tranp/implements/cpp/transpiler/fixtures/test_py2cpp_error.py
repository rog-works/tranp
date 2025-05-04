from collections.abc import Iterator


class InvalidOps:
	def ternary_to_union_types(self) -> None:
		n_or_s = 1 if True else ''

	def yield_return(self) -> Iterator[int]:
		yield 0

	def delete_relay(self) -> None:
		del self.delete_relay

	def destruction_assign(self) -> None:
		a, b = {'a': 1}
