from typing import TypeVar

from rogw.tranp.compatible.cpp.object import CSP

T = TypeVar('T', bound='A')

class A: ...
class B(A): ...


def factory(t: type[T]) -> CSP[T]:
	return CSP.new(t())


def main() -> None:
	b = factory(B)
