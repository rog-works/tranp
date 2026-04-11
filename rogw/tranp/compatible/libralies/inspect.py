from typing import Any


class Signature:
	@property
	def parameters(self) -> dict[str, Any]: ...


def signature(t: type[Any]) -> Signature: ...
