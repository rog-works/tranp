import json
import re
import sys


class Records:
	"""コールスタックを記録。デバッグ用"""

	_instance: 'Records | None' = None

	@classmethod
	def instance(cls) -> 'Records':
		"""シングルトンインスタンスを取得

		Returns:
			インスタンス
		"""
		if not cls._instance:
			cls._instance = cls()

		return cls._instance

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self._record: dict[str, int] = {}

	def __str__(self) -> str:
		"""Returns: 文字列表現"""
		data = {**dict(sorted(self._record.items(), key=lambda entry: entry[0])), 'total': self.total}
		return str(json.dumps(data, indent=2))

	@property
	def total(self) -> int:
		"""Returns: 総コール数"""
		return sum(self._record.values())

	def put(self, back_at: int = 2) -> None:
		"""コールスタックを記録

		Args:
			back_at: 遡るフレーム数 (default = 2)
		"""
		frame = sys._getframe(back_at)  # type: ignore XXX 利用面に問題はないため警告を抑制
		matches = re.search(r"file '.+\\(\w+\.py)', line (\d+)", str(frame))
		if not matches:
			raise ValueError(f'Unexpected frame format. frame: {str(frame)}')

		key = f'{matches[1]}:{matches[2]}'
		if key not in self._record:
			self._record[key] = 0

		self._record[key] += 1
