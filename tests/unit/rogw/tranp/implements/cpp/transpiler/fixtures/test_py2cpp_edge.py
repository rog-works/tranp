from rogw.tranp.compatible.python.embed import Embed


class A:
	def a(self) -> None: ...
	@Embed.alias('a')
	def b(self) -> None: ...
