class FileLoader:
	def __call__(self, filepath: str) -> str:
		with open(filepath, mode='r') as f:
			return '\n'.join(f.readlines())
