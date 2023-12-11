from unittest import TestCase

from py2cpp.node.embed import EmbedKeys, embed_meta, expansionable


class TestEmbed(TestCase):
	def test_embed_meta(self) -> None:
		class MetaHolder: pass


		@embed_meta(MetaHolder, lambda: {'__test_class_meta__': 1})
		class A:
			@embed_meta(MetaHolder, lambda: {'__test_func_meta__': 2})
			def prop(self, v: int) -> str:
				return str(v)


		a = A()
		self.assertEqual(hasattr(MetaHolder, f'__test_class_meta__:{A.__module__}.A'), True)
		self.assertEqual(getattr(MetaHolder, f'__test_class_meta__:{A.__module__}.A'), 1)
		self.assertEqual(hasattr(MetaHolder, f'__test_func_meta__:{A.__module__}.A:prop'), True)
		self.assertEqual(getattr(MetaHolder, f'__test_func_meta__:{A.__module__}.A:prop'), 2)
		self.assertEqual(a.prop.__annotations__['v'], int)
		self.assertEqual(a.prop.__annotations__['return'], str)


	def test_expansionable(self) -> None:
		class MetaHolder: pass


		class A:
			@property
			@embed_meta(MetaHolder, expansionable(order=0))
			def prop0(self) -> int:
				return 0


			@property
			@embed_meta(MetaHolder, expansionable(order=1))
			def prop1(self) -> int:
				return 1


		a = A()
		self.assertEqual(hasattr(MetaHolder, f'{EmbedKeys.Expansionable}:{A.__module__}.A:prop0'), True)
		self.assertEqual(getattr(MetaHolder, f'{EmbedKeys.Expansionable}:{A.__module__}.A:prop0'), 0)
		self.assertEqual(hasattr(MetaHolder, f'{EmbedKeys.Expansionable}:{A.__module__}.A:prop1'), True)
		self.assertEqual(getattr(MetaHolder, f'{EmbedKeys.Expansionable}:{A.__module__}.A:prop1'), 1)
