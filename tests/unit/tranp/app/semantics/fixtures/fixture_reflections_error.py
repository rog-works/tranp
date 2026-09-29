class InvalidOps:
	def tuple_expand(self) -> None:
		# XXX 要素0のtupleはサブタイプが無いため非対応
		a = [*(), 1]
