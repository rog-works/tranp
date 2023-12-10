from unittest import TestCase

from py2cpp.node.embed import EmbedKeys, embed_meta, node_properties


class TestEmbed(TestCase):
	def test_embed_meta(self) -> None:
		@embed_meta(lambda: {'__test_class_meta__': 1})
		class A:
			@embed_meta(lambda: {'__test_func_meta__': 2})
			def prop(self, v: int) -> str:
				return str(v)

		a = A()
		self.assertEqual(hasattr(a.__class__, '__test_class_meta__'), True)
		self.assertEqual(getattr(a.__class__, '__test_class_meta__'), 1)
		self.assertEqual(hasattr(a.__class__.__dict__['prop'], '__test_func_meta__'), True)
		self.assertEqual(getattr(a.__class__.__dict__['prop'], '__test_func_meta__'), 2)
		self.assertEqual(a.prop.__annotations__['v'], int)
		self.assertEqual(a.prop.__annotations__['return'], str)


	def test_node_properties(self) -> None:
		@embed_meta(node_properties('prop0', 'prop1'))
		class A:
			@property
			def prop1(self) -> int:
				return 1


			@property
			def prop0(self) -> int:
				return 0


		a = A()
		self.assertEqual(hasattr(a.__class__, f'{EmbedKeys.NodeProp}.prop0'), True)
		self.assertEqual(getattr(a.__class__, f'{EmbedKeys.NodeProp}.prop0'), 0)
		self.assertEqual(hasattr(a.__class__, f'{EmbedKeys.NodeProp}.prop1'), True)
		self.assertEqual(getattr(a.__class__, f'{EmbedKeys.NodeProp}.prop1'), 1)
