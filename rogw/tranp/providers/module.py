from rogw.tranp.data.meta.types import ModuleMeta, ModuleMetaFactory
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.lang.module import module_path_to_filepath
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.module.module import Module
from rogw.tranp.module.loader import ModuleLoader
from rogw.tranp.semantics.processor import Preprocessors
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


@injectable
def module_loader(invoker: Invoker, entrypoints: Entrypoints, db: SymbolDB, processors: Preprocessors) -> ModuleLoader:
	"""モジュールローダーを生成

	Args:
		invoker (Invoker): ファクトリー関数 @inject
		entrypoints (Entrypoints): エントリーポイントマネージャー @inject
		db (SymbolDB): シンボルテーブル @inject
		processors (Preprocessors): プリプロセッサープロバイダー @inject
	Returns:
		ModuleLoader: モジュールローダー
	"""
	def handler(module_path: ModulePath) -> Module:
		module = invoker(Module, module_path, entrypoints.load(module_path.path, module_path.language))
		for proc in processors():
			proc(module, db)

		return module

	return handler


@injectable
def module_meta_factory(module_paths: ModulePaths, loader: IFileLoader) -> ModuleMetaFactory:
	"""モジュールメタファクトリーを生成

	Args:
		module_paths (ModulePaths): モジュールパスリスト @inject
		loader (IFileLoader): ファイルローダー @inject
	Returns:
		ModuleMetaFactory: モジュールメタファクトリー
	"""
	def handler(module_path: str) -> ModuleMeta:
		index = [module_path.path for module_path in module_paths].index(module_path)
		target_module_path = module_paths[index]
		filepath = module_path_to_filepath(target_module_path.path, f'.{target_module_path.language}')
		return {'hash': loader.hash(filepath), 'path': module_path}

	return handler
