from py2cpp.compatible.cpp.preprocess import pragma
from py2cpp.compatible.cpp.enum import (CEnum, A)

pragma('once')

class Base:
	pass

@deco(A, A.B)
class Hoge(Base):
	class Values(CEnum):
		A = 0
		B = 1

	def func1(self, value: int) -> Values:
		if value == 0:
			return Hoge.Values.A
		else:
			return Hoge.Values.B

	@deco_func('hoge')
	def _func2(self, text: str) -> list[int]:
		map: dict[Hoge.Values, int] = {
			Hoge.Values.A: 0,
			Hoge.Values.B: 1,
		}
		empty_map = {}
		arr: list[int] = [0, 1, 2]
		empty_arr = []
		arr[0]
		arr[0] += arr[1]
		return arr

	def __init__(self, v: int, s: str) -> None:
		self.v: int = v
		self.s: str = s

		def closure() -> None:
			print(self.v)

	@classmethod
	def cls_func(cls) -> bool:
		return True

def func3(ok: bool) -> None:
	pass
