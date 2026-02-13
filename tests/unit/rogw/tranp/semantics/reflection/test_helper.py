from unittest import TestCase

from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.test.helper import data_provider


class Helper:
	@classmethod
	def normalize_props(cls, props: dict[str, str], ignore: list[str]) -> dict[str, list[str]]:
		unique_keys: list[str] = []
		keys = list(props.keys())
		for i, key in enumerate(keys):
			found = False
			for j in range(i + 1, len(keys)):
				if keys[j].startswith(key):
					found = True
					break

			if not found:
				unique_keys.append(key)

		normalized: dict[str, list[str]] = {key: [] for key in unique_keys}
		for key in unique_keys:
			count = DSN.elem_counts(key)
			for i in range(2, count):
				begin = DSN.left(key, i)
				if begin in props and props[begin] not in ignore:
					normalized[key].append(props[begin])

			normalized[key].append(props[key])

		return normalized

	@classmethod
	def find_actual_path(cls, target: str, target_props: list[str], actual_props: dict[str, list[str]]) -> str:
		target_begin = DSN.left(target, 2)
		target_begins = target_props[:-1]
		for actual_path, props in actual_props.items():
			if actual_path.startswith(target_begin) and len(target_props) == len(props) and target_begins == props[:-1]:
				return actual_path

		return ''


class TestTemplateManipulator(TestCase):
	@data_provider([
		(
			{
				'parameters.0': 'Union',
				'parameters.0.0': 'CP',
				'parameters.0.0.0': 'Promise',
				'parameters.0.1': 'None',
			},
			['Union'],
			{
				'parameters.0.0.0': ['CP', 'Promise'],
				'parameters.0.1': ['None'],
			},
		),
	])
	def test_normalize_props(self, props: dict[str, str], ignore: list[str], expected: dict[str, list[str]]) -> None:
		actual = Helper.normalize_props(props, ignore)
		self.assertEqual(expected, actual)

	@data_provider([
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
	])
	def test_find_actual_path(self, target: str, schema_props: dict[str, str], actual_props: dict[str, str], expected: str) -> None:
		normalize_schema_props = Helper.normalize_props(schema_props, ignore=['Union'])
		normalize_actual_props = Helper.normalize_props(actual_props, ignore=['Union'])
		actual = Helper.find_actual_path(target, normalize_schema_props[target], normalize_actual_props)
		self.assertEqual(expected, actual)
