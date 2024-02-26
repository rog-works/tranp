from typing import Callable, Generic, ParamSpec, TypeVar

from rogw.tranp.errors import FatalError
from rogw.tranp.lang.implementation import implements, override

T = TypeVar('T')
P = ParamSpec('P')


class CVar(Generic[T]):
	# XXX 成り立たないためコメントアウト
	# @abstractclassmethod
	# def __class_getitem__(cls, var_type: type[T]) -> 'type[CVar[T]]':
	# 	raise NotImplementedError()

	@classmethod
	def new(cls, ctor: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> 'CVar[T]':
		raise FatalError(f'Method not allowed. method: "new", cls: {cls}, ctor: {ctor}')

	def __init__(self, origin: T) -> None:
		self.__origin = origin

	def raw(self) -> T:
		return self.__origin

	def ref(self) -> 'CVar[T]':
		raise FatalError(f'Method not allowed. method: "ref" self: {self}, origin: {self.__origin}')

	def addr(self) -> 'CVar[T]':
		raise FatalError(f'Method not allowed. method: "addr", self: {self}, origin: {self.__origin}')


class CP(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CP[T]]':
		return CP[var_type]

	@classmethod
	def new(cls, ctor: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> 'CP[T]':
		return cls(ctor(*args, **kwargs))

	@override
	def ref(self) -> 'CRef[T]':
		return CRef(self.raw())


class CSP(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CSP[T]]':
		return CSP[var_type]

	@classmethod
	def new(cls, ctor: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> 'CSP[T]':
		return cls(ctor(*args, **kwargs))

	@override
	def ref(self) -> 'CRef[T]':
		return CRef(self.raw())

	@override
	def addr(self) -> 'CP[T]':
		return CP(self.raw())


class CRef(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRef[T]]':
		return CRef[var_type]

	@override
	def addr(self) -> 'CP[T]':
		return CP(self.raw())


class CRaw(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRaw[T]]':
		return CRaw[var_type]

	@override
	def ref(self) -> 'CRef[T]':
		return CRef(self.raw())

	@override
	def addr(self) -> 'CP[T]':
		return CP(self.raw())
