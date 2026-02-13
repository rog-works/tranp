from unittest import TestCase

from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.test.helper import data_provider


class TestTemplateManipulator(TestCase):
	@data_provider([
		(
			### schema: CP<T_co>
			# [CP, T_co]
			'parameters.0.0',
			{
				'klass.0': ['CWP', 'T_co'],
				'parameters.0.0': ['CP', 'T_co'],
			},
			{
				### actual: Union<CP<Promise>, None>
				# CWP<T_co>
				'klass.0': ['CWP', 'T_co'],
				# Union<CP<Promise>, None>
				'parameters.0.0.0': ['CP', 'Promise'],
				'parameters.0.1': ['None'],
			},
			'parameters.0.0.0',
		),
	])
	def test_update_path(self, target: str, schema_props: dict[str, list[str]], actual_props: dict[str, list[str]], expected: str) -> None:
		actual = self.find_actual_path(target, schema_props[target], actual_props)
		self.assertEqual(expected, actual)

	@data_provider([
		(
			{
				'parameters.0': 'Union',
				'parameters.0.0': 'CP',
				'parameters.0.0.0': 'Promise',
				'parameters.0.1': 'None',
			},
			{
				'parameters.0.0.0': ['Union', 'CP', 'Promise'],
				'parameters.0.1': ['Union', 'None'],
			},
		),
	])
	def test_normalize(self, props: dict[str, str], expected: dict[str, list[str]]) -> None:
		actual = self.normalize_props(props)
		self.assertEqual(expected, actual)

	def normalize_props(self, props: dict[str, str]) -> dict[str, list[str]]:
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
				if begin in props:
					normalized[key].append(props[begin])

			normalized[key].append(props[key])

		return normalized

	def find_actual_path(self, target: str, target_props: list[str], actual_props: dict[str, list[str]]) -> str:
		target_begin = DSN.left(target, 2)
		target_begins = target_props[:-1]
		for actual_path, props in actual_props.items():
			if actual_path.startswith(target_begin) and len(target_props) == len(props) and target_begins == props[:-1]:
				return actual_path

		return ''
