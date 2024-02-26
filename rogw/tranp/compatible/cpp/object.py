from abc import ABCMeta, abstractclassmethod
from typing import Callable, Generic, ParamSpec, TypeVar

from rogw.tranp.errors import FatalError
from rogw.tranp.lang.implementation import implements, override

T = TypeVar('T')

P = ParamSpec('P')


class CVar(Generic[T], metaclass=ABCMeta):
	@abstractclassmethod
	def __class_getitem__(cls, var_type: type[T]) -> type[CVar[T]]:
		raise NotImplementedError()

	@classmethod
	def new(cls, ctor: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> CVar[T]:
		raise FatalError(f'Method not allowed. method: "new", cls: {cls}, ctor: {ctor}')

	def __init__(self, origin: T) -> None:
		self.__origin = origin

	@property
	def raw(self) -> T:
		return self.__origin

	@property
	def ref(self) -> 'CVar[T]':
		raise FatalError(f'Method not allowed. method: "ref" self: {self}, origin: {self.__origin}')

	@property
	def addr(self) -> 'CVar[T]':
		raise FatalError(f'Method not allowed. method: "addr", self: {self}, origin: {self.__origin}')


class CP(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type['CP[T]']:
		return CP[var_type]

	@classmethod
	def new(cls, ctor: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> CP[T]:
		return cls(ctor(*args, **kwargs))

	@property
	@override
	def ref(self) -> 'CRef[T]':
		return CRef(self.raw)


class CSP(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type['CSP[T]']:
		return CSP[var_type]

	@classmethod
	def new(cls, ctor: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> CSP[T]:
		return cls(ctor(*args, **kwargs))

	@property
	@override
	def ref(self) -> 'CRef[T]':
		return CRef(self.raw)

	@property
	@override
	def addr(self) -> 'CP[T]':
		return CP(self.raw)


class CRef(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type['CRef[T]']:
		return CRef[var_type]

	@property
	@override
	def addr(self) -> 'CP[T]':
		return CP(self.raw)


class CRaw(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type['CRaw[T]']:
		return CRaw[var_type]

	@property
	@override
	def ref(self) -> 'CRef[T]':
		return CRef(self.raw)

	@property
	@override
	def addr(self) -> 'CP[T]':
		return CP(self.raw)


class CP_Const(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type['CP_Const[T]']:
		return CP_Const[var_type]

	@property
	@override
	def ref(self) -> 'CRef_Const[T]':
		return CRef_Const(self.raw)


class CSP_Const(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type['CSP_Const[T]']:
		return CSP_Const[var_type]

	@property
	@override
	def ref(self) -> 'CRef_Const[T]':
		return CRef_Const(self.raw)

	@property
	@override
	def addr(self) -> 'CP_Const[T]':
		return CP_Const(self.raw)


class CRef_Const(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type['CRef_Const[T]']:
		return CRef_Const[var_type]

	@property
	@override
	def addr(self) -> 'CRef_Const[T]':
		return CRef_Const(self.raw)


class CRaw_Const(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type['CRaw_Const[T]']:
		return CRaw_Const[var_type]

	@property
	@override
	def ref(self) -> 'CRef_Const[T]':
		return CRef_Const(self.raw)

	@property
	@override
	def addr(self) -> 'CP_Const[T]':
		return CP_Const(self.raw)
