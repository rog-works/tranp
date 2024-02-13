from rogw.tranp.compatible.cpp.enum import CEnum
from rogw.tranp.compatible.python.embed import __actual__, __alias__

class Values(CEnum):
	A = 0
	B = 1

class Base: ...

@__alias__('Alias')
class Class(Base):
	cn: int = 0

	@classmethod
	def class_method(cls) -> bool:
		if True:
			lb = True
			return lb
		else:
			return False

	def __init__(self, n: int, s: str) -> None:
		self.n: int = n
		self.s: str = s
		ln = n
		lb: bool = False

		def method_in_closure() -> None:
			for i in range(10): ...

	@__alias__('alias')
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

a = 0
b: str = ''
