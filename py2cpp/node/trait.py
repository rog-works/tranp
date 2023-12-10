class ScopeTrait:
	"""スコープを所有するノードを明示

	Note:
		対象:
			* クラス
			* 関数
			* Enum
			* 制御構文(if/for/while/try)
	"""
	pass


class NamedScopeTrait:
	"""名前空間を所有するノードを明示

	Note:
		対象:
			* クラス
			* Enum
	"""
	@property
	def scope_name(self) -> str:
		...


