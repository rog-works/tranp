import os
import re
import sys


class CaseDiscovery:
	"""テストケースを抽出"""

	@classmethod
	def put(cls, filepath: str) -> None:
		"""テストケースを抽出し、標準出力に結果を出力

		Args:
			filepath: テストモジュールのファイルパス
		"""
		methods = cls.discover(filepath)
		sys.stdout.writelines([f'{method}\n' for method in methods])
		sys.stdout.flush()

	@classmethod
	def discover(cls, filepath: str) -> list[str]:
		"""テストケースを抽出

		Args:
			filepath: テストモジュールのファイルパス
		Returns:
			テストケースのモジュールパスリスト
		"""
		if not os.path.exists(filepath):
			raise FileNotFoundError(filepath)

		return cls.analyze_cases(cls.load_source(filepath))

	@classmethod
	def load_source(cls, filepath: str) -> str:
		"""ソースファイルをロード

		Args:
			filepath: ファイルパス
		Returns:
			ソースファイル
		"""
		with open(filepath, mode='r', encoding='utf-8') as f:
			return f.read()

	@classmethod
	def analyze_cases(cls, source: str) -> list[str]:
		"""テストケースを抽出

		Args:
			source: ソースファイル
		Returns:
			テストケースのモジュールパスリスト
		"""
		class_pattern = re.compile(r'^class (Test[\w\d]+)')
		method_pattern = re.compile(r'^\tdef (test_[\w\d]+)')
		klass = ''
		methods: list[str] = []
		for line in source.split('\n'):
			matches = re.search(method_pattern, line)
			if matches:
				methods.append(f'{klass}.{matches[1]}')
				continue

			matches = re.search(class_pattern, line)
			if matches:
				klass = matches[1]

		return methods


if __name__ == '__main__':
	CaseDiscovery.put(sys.argv[1])
