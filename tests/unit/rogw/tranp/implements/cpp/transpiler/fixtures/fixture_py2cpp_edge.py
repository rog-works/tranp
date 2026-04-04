from typing import Generic, TypeVar

T = TypeVar('T')


class G(Generic[T]):
	@property
	def v(self) -> T: ...


class A:
	class B(G[int]): ...
	class C(G[T]): ...


def run() -> None:
	b = A.B()
	bv = b.v
	bv2 = A.B().v
	c = A.C[str]()
	cv = c.v
	cv2 = A.C[str]().v
