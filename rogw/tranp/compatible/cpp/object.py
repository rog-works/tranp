from typing import Generic, TypeVar

from rogw.tranp.compatible.python.embed import __hint_generic__

T = TypeVar('T')


class CVar(Generic[T]):
	# XXX 成り立たないためコメントアウト
	# @abstractclassmethod
	# def __class_getitem__(cls, var_type: type[T]) -> 'type[CVar[T]]':
	# 	raise Exception()

	@classmethod
	def new(cls, origin: T) -> 'CVar[T]':
		# XXX 一旦Exceptionで対応
		raise Exception(f'Method not allowed. method: "new", cls: {cls}, origin: {origin}')

	def __init__(self, origin: T) -> None:
		self.__origin = origin

	def on(self) -> T:
		return self.__origin

	def raw(self) -> T:
		return self.__origin

	def ref(self) -> 'CVar[T]':
		# XXX 一旦Exceptionで対応
		raise Exception(f'Method not allowed. method: "ref" self: {self}, origin: {self.__origin}')

	def addr(self) -> 'CVar[T]':
		# XXX 一旦Exceptionで対応
		raise Exception(f'Method not allowed. method: "addr", self: {self}, origin: {self.__origin}')


@__hint_generic__(T)
class CP(CVar[T]):
	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CP[T]]':
		return CP[var_type]

	@classmethod
	def new(cls, origin: T) -> 'CP[T]':
		return cls(origin)

	def ref(self) -> 'CRef[T]':
		return CRef(self.raw())


@__hint_generic__(T)
class CSP(CVar[T]):
	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CSP[T]]':
		return CSP[var_type]

	@classmethod
	def new(cls, origin: T) -> 'CSP[T]':
		return cls(origin)

	def ref(self) -> 'CRef[T]':
		return CRef(self.raw())

	def addr(self) -> 'CP[T]':
		return CP(self.raw())


@__hint_generic__(T)
class CRef(CVar[T]):
	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRef[T]]':
		return CRef[var_type]

	def addr(self) -> 'CP[T]':
		return CP(self.raw())


@__hint_generic__(T)
class CRaw(CVar[T]):
	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRaw[T]]':
		return CRaw[var_type]

	def ref(self) -> 'CRef[T]':
		return CRef(self.raw())

	def addr(self) -> 'CP[T]':
		return CP(self.raw())
