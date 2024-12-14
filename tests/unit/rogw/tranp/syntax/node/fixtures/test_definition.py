from abc import abstractmethod
from typing import ClassVar, Generic, TypeVar

from rogw.tranp.compatible.cpp.enum import CEnum as Enum
from rogw.tranp.compatible.python.embed import __actual__

T = TypeVar('T')


global_n = 0
global_s: str = ''


class Values(Enum):
	A = 0
	B = 1


class Base:
	anno_n: int
	move_s: str

	def __init__(self) -> None:
		self.anno_n: int = 0
		self.move_s = ''

	@abstractmethod
	def public_method(self) -> Values: ...


class Class(Base):
	cn: ClassVar[int] = 0
	move_ns: list[int]

	@classmethod
	def class_method(cls) -> bool:
		if True:
			lb = True
			return lb
		else:
			return False

	def __init__(self, n: int, s: str) -> None:
		super().__init__()
		self.anno_n = n
		self.move_s = s
		self.move_ns = [n]
		ln = n
		lb: bool = False

		def method_in_closure() -> None:
			for i in range(10): ...

	@property
	def property_method(self) -> int:
		return 0

	def public_method(self, n: int) -> Values:
		try:
			raise Exception()
		except Exception as e:
			raise e

	def _protected_method(self, s: str) -> list[int]: ...


def func(b: bool) -> None:
	lb = b

	def func_in_closure(n: int) -> None: ...


@__actual__('Actual')
class Class2: ...


class GenBase(Generic[T]): ...


class GenSub(GenBase[T]): ...


class ParamOps:
	def star_params(self, n: int, *args: str) -> None:
		self.star_params(1, '2', '3')

	def kw_params(self, s: str, *args: int, **kwargs: bool) -> None:
		self.kw_params('1', 2, 3, on=True, off=False)
