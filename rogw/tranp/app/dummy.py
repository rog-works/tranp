from rogw.tranp.data.meta.types import ModuleMetaFactory
from rogw.tranp.lang.annotation import duck_typed, injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.providers.module import module_path_dummy
from rogw.tranp.providers.syntax.ast import source_provider
from rogw.tranp.syntax.ast.parser import SourceProvider


class WrapSourceProvider:
	"""偽装ソースコードプロバイダー"""

	@injectable
	def __init__(self, invoker: Invoker) -> None:
		"""インスタンスを生成

		Args:
			sources (ISourceLoader): ソースローダー @inject
		"""
		self._org_source_provider = invoker(source_provider)
		self.main_module_path = module_path_dummy().path
		self.source_code = ''

	@duck_typed(SourceProvider)
	def __call__(self, module_path: str) -> str:
		"""モジュールパスを基にソースコードを生成

		Args:
			module_path (str): モジュールパス
		Returns:
			str: ソースコード
		"""
		if module_path == self.main_module_path:
			return f'{self.source_code}\n'
		else:
			return self._org_source_provider(module_path)


def make_dummy_module_meta_factory() -> ModuleMetaFactory:
	"""ダミーのメタファクトリーを生成

	Returns:
		ModuleMetaFactory: モジュールのメタファクトリー
	"""
	return lambda module_path: {'hash': 'dummy', 'path': module_path}
