from tranp.app.data.meta.types import ModuleMeta, ModuleMetaFactory
from tranp.app.file.loader import ISourceLoader
from tranp.app.lang.annotation import implements, injectable
from tranp.app.lang.locator import Invoker
from tranp.app.lang.module import module_path_to_filepath
from tranp.app.module.loader import IModuleLoader
from tranp.app.module.module import Module
from tranp.app.module.types import ModulePath, ModulePaths
from tranp.app.semantics.processor import PreprocessorProvider
from tranp.app.semantics.reflection.db import SymbolDB
from tranp.app.syntax.ast.entrypoints import Entrypoints


def module_path_dummy() -> ModulePath:
	"""ダミーのモジュールパスを生成

	Returns:
		モジュールパス
	Note:
		モジュール経由で読み込みが不要な一部のテストでのみ利用
	"""
	return ModulePath('__main__', language='py')


def library_paths() -> ModulePaths:
	"""標準ライブラリーモジュールのパスリストを生成

	Returns:
		モジュールパスリスト
	"""
	return ModulePaths([
		ModulePath('tranp.app.compatible.libralies.type', language='py'),
		ModulePath('tranp.app.compatible.libralies.classes', language='py'),
	])


def module_paths() -> ModulePaths:
	"""処理対象モジュールのパスリストを生成

	Returns:
		モジュールパスリスト
	"""
	return ModulePaths([ModulePath('example.example', language='py')])


class ModuleLoader(IModuleLoader):
	"""モジュールローダー"""

	@injectable
	def __init__(self, invoker: Invoker, entrypoints: Entrypoints, db: SymbolDB, processors: PreprocessorProvider) -> None:
		"""インスタンスを生成

		Args:
			invoker: ファクトリー関数 @inject
			entrypoints: エントリーポイントマネージャー @inject
			db: シンボルテーブル @inject
			processors: プリプロセッサープロバイダー @inject
		"""
		self.invoker = invoker
		self.entrypoints = entrypoints
		self.db = db
		self.processors = processors

	@implements
	def load(self, module_path: ModulePath) -> Module:
		"""モジュールをロード

		Args:
			module_path: モジュールパス
		Returns:
			モジュール
		"""
		return self.invoker(Module, module_path, self.entrypoints.load(module_path.path, module_path.language))

	@implements
	def unload(self, module_path: ModulePath) -> None:
		"""モジュールをアンロード

		Args:
			module_path: モジュールパス
		"""
		self.entrypoints.unload(module_path.path)
		self.db.unload(module_path.path)

	@implements
	def preprocess(self, module: Module) -> None:
		"""モジュールにプリプロセスを実施

		Args:
			module: モジュール
		"""
		for proc in self.processors():
			if not proc(module, self.db):
				break


@injectable
def module_meta_factory(module_paths: ModulePaths, sources: ISourceLoader) -> ModuleMetaFactory:
	"""モジュールメタファクトリーを生成

	Args:
		module_paths: モジュールパスリスト @inject
		sources: ソースコードローダー @inject
	Returns:
		モジュールメタファクトリー
	"""
	def handler(module_path: str) -> ModuleMeta:
		index = [module_path.path for module_path in module_paths].index(module_path)
		target_module_path = module_paths[index]
		filepath = module_path_to_filepath(target_module_path.path, f'.{target_module_path.language}')
		return {'hash': sources.hash(filepath), 'path': module_path}

	return handler
