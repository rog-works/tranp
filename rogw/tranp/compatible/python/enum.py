from rogw.tranp.compatible.python.template import T_Self

class Enum:
	@classmethod
	def __class_getitem__(cls: type[T_Self], key: str) -> T_Self: ...
	def __init__(self, value: int) -> None: ...
