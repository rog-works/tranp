from unittest import TestCase

from tranp.node.embed import (
	EmbedKeys,
	Meta,
	accept_tags,
	actualized,
	expandable,
)


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
		self.assertEqual(class_meta, 1)
		self.assertEqual(method_meta['prop'], 2)
		self.assertEqual(a.prop.__annotations__['v'], int)
		self.assertEqual(a.prop.__annotations__['return'], str)

	def test_accept_tags(self) -> None:
		class MetaHolder: pass
		@Meta.embed(MetaHolder, accept_tags('hoge'))
		class B: pass

		class_meta: list[str] = Meta.dig_for_class(MetaHolder, B, EmbedKeys.AcceptTags, default=[])
		self.assertEqual(class_meta, ['hoge'])

	def test_actualized(self) -> None:
		class MetaHolder: pass
		class Base: pass
		@Meta.embed(MetaHolder, actualized(via=Base))
		class Sub(Base): pass

		class_meta = Meta.dig_by_key_for_class(MetaHolder, EmbedKeys.Actualized, value_type=type)
		self.assertEqual(class_meta[Sub], Base)

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
		self.assertEqual(method_meta['prop0'], True)
		self.assertEqual(method_meta['prop1'], True)
