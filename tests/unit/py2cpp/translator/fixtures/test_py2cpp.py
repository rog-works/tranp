from py2cpp.compatible.cpp.object import CObject, CP, CRef, CSP

class A(CObject):
	...

class CVarCheck:
	def ret_raw(self) -> A:
		return A()

	def ret_cp(self) -> A[CP]:
		return A()

	def ret_csp(self) -> A[CSP]:
		return A()

	def local_move(self) -> None:
		a: A = A()
		ap: A[CP] = a
		asp: A[CSP] = A()
		ar: A[CRef] = a
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

	def param_move(self, a: A, ap: A[CP], asp: A[CSP]) -> None:
		a1 = a
		a2: A = ap
		a3: A = asp
		a = a1
		ap = a2
		asp = a3  # エラーケース

	def invoke_method(self, a: A, ap: A[CP], asp: A[CSP]) -> None:
		self.invoke_method(a, a, a)
		self.invoke_method(ap, ap, ap)  # エラーケース
		self.invoke_method(asp, asp, asp)  # エラーケース
