from typing import Protocol


class CoreLibrariesProvider(Protocol):
	def __call__(self) -> list[str]:
		...


def core_libraries() -> list[str]:
	return ['py2cpp.python.classes']
