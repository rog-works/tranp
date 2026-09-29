class datetime:
	year: int
	month: int
	day: int
	hour: int
	minute: int
	second: int
	microsecond: int

	def __init__(self) -> None:
		self.year = 0
		self.month = 0
		self.day = 0
		self.hour = 0
		self.minute = 0
		self.second = 0
		self.microsecond = 0

	@classmethod
	def now(cls) -> 'datetime': ...
	def timestamp(self) -> float: ...
