from unittest import TestCase

from rogw.tranp.syntax.node.embed import EmbedKeys, Meta, accept_tags, expandable


class TestMeta(TestCase):
	def test_embed(self) -> None:
		class MetaHolder: pass
		@Meta.embed(MetaHolder, lambda: {'__test_class_meta__': 1})
		class A:
			@Meta.embed(MetaHolder, lambda: {'__test_func_meta__': 2})
			def prop(self, v: int) -> str:
				return str(v)

		a = A()
		class_meta = Meta.dig_for_class(MetaHolder, A, '__test_class_meta__', default=-1)
		method_meta = Meta.dig_for_method(MetaHolder, A, '__test_func_meta__', value_type=int)
		self.assertEqual(1, class_meta)
		self.assertEqual(2, method_meta['prop'])
		self.assertEqual(int, a.prop.__annotations__['v'])
		self.assertEqual(str, a.prop.__annotations__['return'])

	def test_accept_tags(self) -> None:
		class MetaHolder: pass
		@Meta.embed(MetaHolder, accept_tags('hoge'))
		class B: pass

		class_meta: list[str] = Meta.dig_for_class(MetaHolder, B, EmbedKeys.AcceptTags, default=[])
		self.assertEqual(['hoge'], class_meta)

	def test_expandable(self) -> None:
		class MetaHolder: pass
		class C:
			@property
			@Meta.embed(MetaHolder, expandable)
			def prop0(self) -> int:
				return 0

			@property
			@Meta.embed(MetaHolder, expandable)
			def prop1(self) -> int:
				return 1

		method_meta = Meta.dig_for_method(MetaHolder, C, EmbedKeys.Expandable, value_type=int)
		self.assertEqual(True, method_meta['prop0'])
		self.assertEqual(True, method_meta['prop1'])
