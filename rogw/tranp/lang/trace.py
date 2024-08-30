import json
import re
import sys


class Records:
	"""スタックレコード"""

	_instance: 'Records | None' = None

	@classmethod
	def instance(cls) -> 'Records':
		"""シングルトンインスタンスを取得

		Returns:
			Records: インスタンス
		"""
		if not cls._instance:
			cls._instance = cls()

		return cls._instance

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self._record: dict[str, int] = {}

	def put(self, back_at: int = 2) -> None:
		"""スタックフレームを記録

		Args:
			back_at (int): 遡るフレーム数 (default = 2)
		"""
		frame = sys._getframe(back_at)  # type: ignore XXX 利用面に問題はないため警告を抑制
		matches = re.search(r"file '.+\\(\w+\.py)', line (\d+)", str(frame))
		if not matches:
			raise ValueError(f'Unexpected frame format. frame: {str(frame)}')

		key = f'{matches[1]}:{matches[2]}'
		if key not in self._record:
			self._record[key] = 0

		self._record[key] += 1


	def __str__(self) -> str:
		"""str: 文字列表現"""
		return str(json.dumps(self._record, indent=2))
