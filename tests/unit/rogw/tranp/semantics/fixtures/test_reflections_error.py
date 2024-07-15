class InvalidOps:
	def tenary_to_union_types(self) -> None:
		n_or_s = 1 if True else 'a'

	def tuple_expand(self) -> None:
		# XXX 要素0のtupleはサブタイプが無いため非対応
		a = [*(), 1]
