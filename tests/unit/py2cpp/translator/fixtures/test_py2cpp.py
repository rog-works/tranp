from py2cpp.compatible.cpp.object import CObject, CP, CSP

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
		a = a
		a = ap
		a = asp
		ap = a
		ap = ap
		ap = asp
		asp = a  # XXX あえて誤った実装でテスト
		asp = ap  # XXX あえて誤った実装でテスト
		asp = asp

	def param_move(self, a: A, ap: A[CP], asp: A[CSP]) -> None:
		a1 = a
		a2: A = ap
		a3: A = asp
		a = a1
		ap = a2
		asp = a3  # XXX あえて誤った実装でテスト

	def invoke_method(self, a: A, ap: A[CP], asp: A[CSP]) -> None:
		self.invoke_method(a, a, a)
		self.invoke_method(ap, ap, ap)  # XXX あえて誤った実装でテスト(第3引数)
		self.invoke_method(asp, asp, asp)
