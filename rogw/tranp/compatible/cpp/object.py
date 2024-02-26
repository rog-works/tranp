from abc import ABCMeta, abstractclassmethod
from typing import Generic, TypeVar

from rogw.tranp.lang.implementation import implements

T = TypeVar('T')


class CVar(Generic[T], metaclass=ABCMeta):
	@abstractclassmethod
	def __class_getitem__(cls, var_type: type[T]) -> type[CVar[T]]:
		raise NotImplementedError()

	def __init__(self, origin: T) -> None:
		self.__origin = origin

	@property
	def raw(self) -> T:
		return self.__origin

	@property
	def ref(self) -> T:
		return self.__origin


class CP(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type[CP[T]]:
		return CP[var_type]


class CSP(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type[CSP[T]]:
		return CSP[var_type]


class CRef(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type[CRef[T]]:
		return CRef[var_type]


class CRaw(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type[CRaw[T]]:
		return CRaw[var_type]


class CP_Const(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type[CP_Const[T]]:
		return CP_Const[var_type]


class CSP_Const(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type[CSP_Const[T]]:
		return CSP_Const[var_type]


class CRef_Const(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type[CRef_Const[T]]:
		return CRef_Const[var_type]


class CRaw_Const(CVar[T]):
	@classmethod
	@implements
	def __class_getitem__(cls, var_type: type[T]) -> type[CRaw_Const[T]]:
		return CRaw_Const[var_type]
