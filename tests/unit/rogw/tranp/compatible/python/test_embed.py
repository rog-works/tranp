from unittest import TestCase

from rogw.tranp.compatible.python.embed import Embed


class TestEmbed(TestCase):
	def test_static(self) -> None:
		class A:
			@classmethod
			def cls_method(cls) -> None: ...
			def method(self) -> None: ...
			@property
			def prop(self) -> None: ...

		actual = (
			Embed.static(A.cls_method).decl(lambda: 1),
			Embed.static(A.method).decl(lambda: 2),
			Embed.static(A.prop).decl(lambda: 3),
			Embed.static(A.prop, key='b').decl(lambda: 4),
		)
		self.assertEqual((1, 2, 3, 4), actual)

		actual = (
			Embed.static(A.cls_method).decl(lambda: 11),
			Embed.static(A.method).decl(lambda: 12),
			Embed.static(A.prop).decl(lambda: 13),
			Embed.static(A.prop, key='b').decl(lambda: 14),
		)
		self.assertEqual((1, 2, 3, 4), actual)
