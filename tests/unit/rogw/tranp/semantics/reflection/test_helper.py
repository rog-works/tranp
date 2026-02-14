from unittest import TestCase

from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.test.helper import data_provider


class Helper:
	@classmethod
	def normalize_props(cls, props: dict[str, str]) -> dict[str, str]:
		unique_keys: list[str] = []
		keys = list(props.keys())
		for i, key in enumerate(keys):
			found = False
			for j in range(i + 1, len(keys)):
				if keys[j].startswith(key):
					found = True
					break

			# 1階層目(klass/returns)は選別が不要なため除外
			if not found and DSN.elem_counts(key) > 1:
				unique_keys.append(key)

		elem_indexs: dict[str, list[int]] = {key: [] for key in unique_keys}
		for key in unique_keys:
			count = DSN.elem_counts(key)
			for i in range(2, count):
				begin = DSN.left(key, i)
				# Unionは条件を並列に並べることが目的。seq.expandによって既に展開されており、階層としては不要なので除外
				if begin in props and props[begin] != 'Union':
					begin_index = int(DSN.right(begin, 1))
					elem_indexs[key].append(begin_index)

			index = int(DSN.right(key, 1))
			elem_indexs[key].append(index)

		return {key: DSN.join(*map(str, indexs)) for key, indexs in elem_indexs.items()}

	@classmethod
	def find_actual_path(cls, schema_path: str, schema_props: dict[str, str], actual_props: dict[str, str]) -> str:
		# 1階層目(klass/returns)は選別が不要なため除外
		if DSN.elem_counts(schema_path) == 1:
			return schema_path

		schema_elems = schema_props[schema_path]
		schema_path_begin = DSN.left(schema_path, 2)
		for actual_path, actual_elems in actual_props.items():
			if not actual_path.startswith(schema_path_begin):
				continue
			elif actual_elems == schema_elems:
				return actual_path
			elif actual_elems.startswith(schema_elems):
				# 正規化後はスキーマより実行時型の方が必ず長い
				lacks = DSN.elem_counts(actual_elems) - DSN.elem_counts(schema_elems)
				return DSN.left(actual_path, DSN.elem_counts(actual_path) - lacks)

		return ''


class TestTemplateManipulator(TestCase):
	@data_provider([
		(
			{
				'klass': 'Self',
				'returns': 'Self',
			},
			{
			},
		),
		(
			{
				'parameters.0': 'Promise',
			},
			{
				'parameters.0': '0',
			},
		),
		(
			{
				'parameters.0': 'CP',
				'parameters.0.0': 'Promise',
			},
			{
				'parameters.0.0': '0.0',
			},
		),
		(
			{
				'klass': 'CWP',
				'klass.0': 'T_co',
				'parameters.0': 'Union',
				'parameters.0.0': 'CP',
				'parameters.0.0.0': 'Promise',
				'parameters.0.1': 'None',
			},
			{
				'klass.0': '0',
				'parameters.0.0.0': '0.0',
				'parameters.0.1': '1',
			},
		),
	])
	def test_normalize_props(self, props: dict[str, str], expected: dict[str, list[str]]) -> None:
		actual = Helper.normalize_props(props)
		self.assertEqual(expected, actual)

	@data_provider([
		# (Self) => Self
		(
			'klass',
			### schema: Self
			{
				'klass': 'Self',
				'returns': 'Self',
			},
			### actual: Promise
			{
				'klass': 'Promise',
			},
			'klass',
		),
		# CWP(Self, CP<T_co>) => None
		(
			'parameters.0.0',
			### schema: CP<T_co>
			{
				'klass': 'CWP',
				'klass.0': 'T_co',
				'parameters.0': 'CP',
				'parameters.0.0': 'T_co',
			},
			### actual: Union<CP<Promise>, None>
			{
				'klass': 'CWP',
				'klass.0': 'T_co',
				'parameters.0': 'Union',
				'parameters.0.0': 'CP',
				'parameters.0.0.0': 'Promise',
				'parameters.0.1': 'None',
			},
			'parameters.0.0.0',
		),
		(
			'parameters.0.0.0',
			### schema: Union<CP<T_co>, None>
			{
				'klass': 'CWP',
				'klass.0': 'T_co',
				'parameters.0': 'Union',
				'parameters.0.0': 'CP',
				'parameters.0.0.0': 'T_co',
			},
			### actual: CP<Promise>
			{
				'klass': 'CWP',
				'klass.0': 'T_co',
				'parameters.0': 'CP',
				'parameters.0.0': 'Promise',
			},
			'parameters.0.0',
		),
		(
			'parameters.0.0',
			### schema: CP<T_co>
			{
				'klass': 'CWP',
				'klass.0': 'T_co',
				'parameters.0': 'CP',
				'parameters.0.0': 'T_co',
			},
			### actual: CP<Promise>
			{
				'klass': 'CWP',
				'klass.0': 'T_co',
				'parameters.0': 'CP',
				'parameters.0.0': 'Promise',
			},
			'parameters.0.0',
		),
		(
			'parameters.0',
			### schema: T_co
			{
				'klass': 'CWP',
				'klass.0': 'T_co',
				'parameters.0': 'T_co',
			},
			### actual: CP<Promise>
			{
				'klass': 'CWP',
				'klass.0': 'T_co',
				'parameters.0': 'CP',
				'parameters.0.0': 'Promise',
			},
			'parameters.0',
		),
		# sequence(Sequence<T_Value>) => Iterator<tuple<int, T_Value>>
		(
			'parameters.0.0',
			### schema: Sequence<T_Value>
			{
				'parameters.0': 'Sequence',
				'parameters.0.0': 'T_Value',
				'returns.0': 'Iterator',
				'returns.0.0': 'tuple',
				'returns.0.0.0': 'int',
				'returns.0.0.0.0': 'T_Value',
			},
			### actual: list<CP<int>>
			{
				'klass': 'list',
				'klass.0': 'T_Value',
				'parameters.0': 'list',
				'parameters.0.0': 'CP',
				'parameters.0.0.0': 'int',
			},
			'parameters.0.0',
		),
	])
	def test_find_actual_path(self, schema_path: str, schema_props: dict[str, str], actual_props: dict[str, str], expected: str) -> None:
		normalize_schema_props = Helper.normalize_props(schema_props)
		normalize_actual_props = Helper.normalize_props(actual_props)
		actual = Helper.find_actual_path(schema_path, normalize_schema_props, normalize_actual_props)
		self.assertEqual(expected, actual)
