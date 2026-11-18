class Memoize3[T_Key, T_Value]:
	"""メモ化3"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self._values: dict[T_Key, T_Value] = {}

	def has(self, key: T_Key) -> bool:
		"""Args: key: キー Returns: True = 存在"""
		return key in self._values

	def get(self, key: T_Key) -> T_Value:
		"""Args: key: キー Returns: 値"""
		return self._values[key]

	def assign(self, key: T_Key, value: T_Value) -> T_Value:
		"""Args: key: キー, value: 値 Returns: 値"""
		self._values[key] = value
		return value
