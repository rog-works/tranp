from rogw.tranp.compatible.cpp.object import CObject, CP, CRef, CSP

class Base(CObject):
	class_base_n: int = 0

	def __init__(self, n: int = 0) -> None:
		self.base_n: int = n

	def call(self) -> None: ...
	def __add__(self, other: Base) -> Base: ...

class CVarOps:
	def ret_raw(self) -> Base:
		return Base()

	def ret_cp(self) -> Base[CP]:
		return Base()

	def ret_csp(self) -> Base[CSP]:
		return Base()

	def local_move(self) -> None:
		a: Base = Base()
		ap: Base[CP] = a
		asp: Base[CSP] = Base()
		ar: Base[CRef] = a
		if True:
			a = a
			a = ap
			a = asp
			a = ar
		if True:
			ap = a
			ap = ap
			ap = asp
			ap = ar
		if True:
			asp = a  # エラーケース
			asp = ap  # エラーケース
			asp = asp
			asp = ar  # エラーケース
		if True:
			ar = a  # エラーケース
			ar = ap  # エラーケース
			ar = asp  # エラーケース
			ar = ar  # エラーケース

	def param_move(self, a: Base, ap: Base[CP], asp: Base[CSP], ar: Base[CRef]) -> None:
		a1 = a
		a2: Base = ap
		a3: Base = asp
		a4: Base = ar
		a = a1
		ap = a2
		asp = a3  # エラーケース
		ar = a4  # エラーケース

	def invoke_method(self, a: Base, ap: Base[CP], asp: Base[CSP]) -> None:
		self.invoke_method(a, a, a)
		self.invoke_method(ap, ap, ap)  # エラーケース
		self.invoke_method(asp, asp, asp)  # エラーケース

	def sum(self) -> None:
		a = Base()
		ap: Base[CP] = a
		# a2 = a + ap FIXME 実体参照する方法を検討

class FuncOps:
	def print(self) -> None:
		print('%d, %d, %d', 1, 2, 3)

from rogw.tranp.compatible.cpp.enum import CEnum

class AccessOps(Base):
	class Values(CEnum):
		A = 0
		B = 1

	def __init__(self) -> None:
		super().__init__(0)
		self.sub_s: str = ''

	def dot(self, a: AccessOps) -> None:
		print(a.base_n)
		print(a.sub_s)
		print(a.call())

	def arrow(self, ap: AccessOps[CP], asp: AccessOps[CSP]) -> None:
		print(self.base_n)
		print(self.sub_s)
		print(self.call())
		print(ap.base_n)
		print(ap.sub_s)
		print(ap.call())
		print(asp.base_n)
		print(asp.sub_s)
		print(asp.call())

	def double_colon(self) -> None:
		super().call()
		print(Base.class_base_n)
		print(AccessOps.class_base_n)
		print(AccessOps.Values.A)
		d: dict[AccessOps.Values, str] = {
			AccessOps.Values.A: 'A',
			AccessOps.Values.B: 'B',
		}

from rogw.tranp.compatible.python.embed import __alias__

@__alias__('Alias2')
class Alias:
	@__alias__('Inner2')
	class Inner:
		...

	def __init__(self) -> None:
		self.inner: Alias.Inner = Alias.Inner()

	def in_param_return(self, a: 'Alias') -> 'Alias':
		...

	def in_param_return2(self, i: 'Alias.Inner') -> 'Alias.Inner':
		...

	def in_local(self) -> None:
		a = Alias()
		i = Alias.Inner()

class CompOps:
	class C:
		...

	def list_comp(self) -> None:
		values0 = [1, 2, 3]
		values1 = [value for value in values0]

	def dict_comp(self) -> None:
		kvs0 = {'a': CompOps.C()}
		kvs1 = {key: value for key, value in kvs0.items()}

class ForOps:
	def range(self) -> None:
		for i in range(10):
			print(i)

	def enumerate(self) -> None:
		keys = ['a', 'b']
		for index, key in enumerate(keys):
			print(index, key)

	def dict_items(self) -> None:
		kvs = {'a': 1}
		for key, value in kvs.items():
			print(key, value)

class ListOps:
	def len(self) -> None:
		values = [1, 2]
		size_values = len(values)

	def pop(self) -> None:
		values = [1, 2]
		value0 = values.pop(1)
		value1 = values.pop()

class DictOps:
	def len(self) -> None:
		kvs = {'a': 1}
		size_kvs = len(kvs)

	def pop(self) -> None:
		values = {'a': 1, 'b': 2}
		value0 = values.pop('a')
		value1 = values.pop('b')

	def keys(self) -> None:
		kvs = {'a': 1}
		keys = list(kvs.keys())

	def values(self) -> None:
		kvs = {'a': 1}
		values = list(kvs.values())

from typing import TypeAlias

DSI: TypeAlias = dict[str, int]
