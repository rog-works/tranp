from rogw.tranp.data.meta.types import ModuleMeta, ModuleMetaFactory
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.annotation import implements, injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.lang.module import module_path_to_filepath
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.module.module import Module
from rogw.tranp.module.loader import IModuleLoader
from rogw.tranp.semantics.processor import PreprocessorProvider
from rogw.tranp.semantics.reflection.db import SymbolDB
from rogw.tranp.syntax.ast.entrypoints import Entrypoints


def module_path_dummy() -> ModulePath:
	"""ダミーのモジュールパスを生成

	Returns:
		ModulePath: モジュールパス
	Note:
		モジュール経由で読み込みが不要な一部のテストでのみ利用
	"""
	return ModulePath('__main__', language='py')


def library_paths() -> ModulePaths:
	"""標準ライブラリーモジュールのパスリストを生成

	Returns:
		ModulePaths: モジュールパスリスト
	"""
	return ModulePaths([ModulePath('rogw.tranp.compatible.libralies.classes', language='py')])


def module_paths() -> ModulePaths:
	"""処理対象モジュールのパスリストを生成

	Returns:
		ModulePath: モジュールパスリスト
	"""
	return ModulePaths([ModulePath('example.example', language='py')])


class ModuleLoader(IModuleLoader):
	"""モジュールローダー"""

	@injectable
	def __init__(self, invoker: Invoker, entrypoints: Entrypoints, db: SymbolDB, processors: PreprocessorProvider) -> None:
		"""インスタンスを生成

		Args:
			invoker (Invoker): ファクトリー関数 @inject
			entrypoints (Entrypoints): エントリーポイントマネージャー @inject
			db (SymbolDB): シンボルテーブル @inject
			processors (PreprocessorProvider): プリプロセッサープロバイダー @inject
		"""
		self.invoker = invoker
		self.entrypoints = entrypoints
		self.db = db
		self.processors = processors

	@implements
	def load(self, module_path: ModulePath) -> Module:
		"""モジュールをロード

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			Module: モジュール
		"""
		return self.invoker(Module, module_path, self.entrypoints.load(module_path.path, module_path.language))

	@implements
	def unload(self, module_path: ModulePath) -> None:
		"""モジュールをアンロード

		Args:
			module_path (ModulePath): モジュールパス
		"""
		self.entrypoints.unload(module_path.path)
		self.db.unload(module_path.path)

	@implements
	def preprocess(self, module: Module) -> None:
		"""モジュールにプリプロセスを実施

		Args:
			module (Module): モジュール
		"""
		for proc in self.processors():
			if not proc(module, self.db):
				break


@injectable
def module_meta_factory(module_paths: ModulePaths, files: IFileLoader) -> ModuleMetaFactory:
	"""モジュールメタファクトリーを生成

	Args:
		module_paths (ModulePaths): モジュールパスリスト @inject
		files (IFileLoader): ファイルローダー @inject
	Returns:
		ModuleMetaFactory: モジュールメタファクトリー
	"""
	def handler(module_path: str) -> ModuleMeta:
		index = [module_path.path for module_path in module_paths].index(module_path)
		target_module_path = module_paths[index]
		filepath = module_path_to_filepath(target_module_path.path, f'.{target_module_path.language}')
		return {'hash': files.hash(filepath), 'path': module_path}

	return handler
