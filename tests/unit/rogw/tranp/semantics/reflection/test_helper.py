from unittest import TestCase

import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.test.helper import data_provider


class TestTemplateManipulator(TestCase):
	@data_provider([
		(
			### schema: CP<T_co>
			'parameters.0.0',
			{
				### actual: Union<CP<Promise>, None>
				# CWP<T_co>
				'klass': defs.Class,
				'klass.0': defs.Class,
				# Union<CP<Promise>, None>
				'parameters.0': defs.UnionType,
				'parameters.0.0': defs.Class,
				'parameters.0.0.0': defs.Class,
				'parameters.0.1': defs.NullType,
			},
			'parameters.0.0.0',
		),
	])
	def test_update_path(self, target: str, props: dict[str, type[Node]], expected: str) -> None:
		actual = self.find_actual_path(target, props)
		self.assertEqual(expected, actual)

	def find_actual_path(self, target: str, props: dict[str, type[Node]]) -> str:
		count = DSN.elem_counts(target)
		if count == 1:
			return target

		begin = DSN.left(target, 2)
		return self.__find_actual_path_internal(count - 1, props, begin, first=True)

	def __find_actual_path_internal(self, remain: int, props: dict[str, type[Node]], begin: str, first: bool = False) -> str:
		if remain == 0:
			return begin

		i = 0
		path = begin if first else DSN.join(begin, str(i))
		while path in props:
			next_remain = remain if props[path] is (defs.UnionType) else remain - 1
			found = self.__find_actual_path_internal(next_remain, props, path)
			if found:
				return found
			
			if first:
				break

			i += 1
			path = DSN.join(path, str(i))

		return ''
