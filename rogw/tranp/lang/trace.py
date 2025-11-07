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
		return json.dumps(self.summary(), indent=2)

	def summary(self) -> dict[str, int]:
		"""Returns: サマリー"""
		return {**dict(sorted(self._record.items(), key=lambda entry: entry[0])), 'total': self.total}

	@property
	def total(self) -> int:
		"""Returns: 総コール数"""
		return sum(self._record.values())

	def put(self, back_at: int = 2) -> None:
		"""コールスタックを記録

		Args:
			back_at: 遡るフレーム数 (default = 2)
		Note:
			```
			### back_atに関して
			2: putをコールした関数の呼び出し元
			1: putをコールした関数
			```
		"""
		frame = sys._getframe(back_at)  # type: ignore XXX 利用面に問題はないため警告を抑制
		matches = re.search(r"file '.+[^\w\d]([\w\d]+\.py)', line (\d+)", str(frame))
		assert matches

		key = f'{matches[1]}:{matches[2]}'
		if key not in self._record:
			self._record[key] = 0

		self._record[key] += 1
