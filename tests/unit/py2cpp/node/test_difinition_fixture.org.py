from py2cpp.cpp.enum import (CEnum, A)

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
	def _func2(self, text: str) -> None:
		map = {
			Hoge.Values.A: 0,
			Hoge.Values.B: 1,
		}
		empty_map = {}
		arr = [0, 1, 2]
		empty_arr = []

	def __init__(self, v: int, s: str) -> None:
		self.v: int = v
		self.s: str = s

def func3(ok: bool) -> None:
	pass
