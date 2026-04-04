from typing import Generic, TypeVar

T = TypeVar('T')


class G(Generic[T]):
	@property
	def n(self) -> T: ...


class A:
	class B(G[int]): ...


def run() -> None:
	b = A.B()
	bn = b.n
