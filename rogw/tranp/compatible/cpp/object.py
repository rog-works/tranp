from typing import Generic, TypeVar

from rogw.tranp.compatible.python.embed import __hint_generic__

T = TypeVar('T')


class CVar(Generic[T]):
	def __init__(self, origin: T) -> None:
		self.__origin = origin

	@property
	def on(self) -> T:
		return self.__origin

	@property
	def raw(self) -> T:
		return self.__origin


@__hint_generic__(T)
class CP(CVar[T]):
	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CP[T]]':
		return CP[var_type]

	@classmethod
	def new(cls, origin: T) -> 'CP[T]':
		return cls(origin)

	@property
	def ref(self) -> 'CRef[T]':
		return CRef(self.raw)


@__hint_generic__(T)
class CSP(CVar[T]):
	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CSP[T]]':
		return CSP[var_type]

	@classmethod
	def new(cls, origin: T) -> 'CSP[T]':
		return cls(origin)

	@property
	def ref(self) -> 'CRef[T]':
		return CRef(self.raw)

	@property
	def addr(self) -> 'CP[T]':
		return CP(self.raw)


@__hint_generic__(T)
class CRef(CVar[T]):
	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRef[T]]':
		return CRef[var_type]

	@property
	def addr(self) -> 'CP[T]':
		return CP(self.raw)


@__hint_generic__(T)
class CRaw(CVar[T]):
	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRaw[T]]':
		return CRaw[var_type]

	@property
	def ref(self) -> 'CRef[T]':
		return CRef(self.raw)

	@property
	def addr(self) -> 'CP[T]':
		return CP(self.raw)
