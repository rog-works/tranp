def getcwd() -> str: ...

class path:
	def exists(self, filepath: str) -> bool: ...
	def join(self, *args: str) -> str: ...
	def dirname(self, filepath: str) -> str: ...
	def basename(self, filepath: str) -> str: ...
	def absbase(self, filepath: str) -> str: ...
