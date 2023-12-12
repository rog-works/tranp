from unittest import TestCase

from py2cpp.node.embed import (
	accept_tags,
	EmbedKeys,
	embed_meta,
	expansionable,
	digging_meta_class,
	digging_meta_method,
)




class TestEmbed(TestCase):
	def test_embed_meta(self) -> None:
		class MetaHolder: pass


		@embed_meta(MetaHolder, lambda: {'__test_class_meta__': 1})
		class A:
			@embed_meta(MetaHolder, lambda: {'__test_func_meta__': 2})
			def prop(self, v: int) -> str:
				return str(v)


		a = A()
		class_meta = digging_meta_class(MetaHolder, A, '__test_class_meta__', default=-1)
		method_meta = digging_meta_method(MetaHolder, A, '__test_func_meta__')
		self.assertEqual(class_meta, 1)
		self.assertEqual(method_meta['prop'], 2)
		self.assertEqual(a.prop.__annotations__['v'], int)
		self.assertEqual(a.prop.__annotations__['return'], str)


	def test_accept_tags(self) -> None:
		class MetaHolder: pass


		@embed_meta(MetaHolder, accept_tags('hoge'))
		class B: pass

		class_meta: list[str] = digging_meta_class(MetaHolder, B, EmbedKeys.AcceptTags, default=[])
		self.assertEqual(class_meta, ['hoge'])


	def test_expansionable(self) -> None:
		class MetaHolder: pass


		class C:
			@property
			@embed_meta(MetaHolder, expansionable(order=0))
			def prop0(self) -> int:
				return 0


			@property
			@embed_meta(MetaHolder, expansionable(order=1))
			def prop1(self) -> int:
				return 1


		method_meta = digging_meta_method(MetaHolder, C, EmbedKeys.Expansionable)
		self.assertEqual(method_meta['prop0'], 0)
		self.assertEqual(method_meta['prop1'], 1)
