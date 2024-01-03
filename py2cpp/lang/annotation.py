from typing import Callable


class ValueAnnotation:
	def __init__(self, origin: type) -> None:
		self.__type = origin

	@property
	def org_type(self) -> type:
		return self.__type

	@property
	def is_generic(self) -> bool:
		return hasattr(self.__type, '__origin__')

	@property
	def is_list(self) -> bool:
		return self.is_generic and self.origin is list

	@property
	def origin(self) -> type:
		return getattr(self.__type, '__origin__')


class FunctionAnnotation:
	def __init__(self, func: Callable) -> None:
		self.__func = func

	@property
	def args(self) -> dict[str, ValueAnnotation]:
		return {key: ValueAnnotation(in_type) for key, in_type in self.__annos.items() if key != 'return'}

	@property
	def return_type(self) -> ValueAnnotation:
		return ValueAnnotation(self.__annos['return'])

	@property
	def __annos(self) -> dict[str, type]:
		return self.__func.__annotations__
