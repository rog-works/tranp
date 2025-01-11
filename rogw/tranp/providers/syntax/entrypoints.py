from rogw.tranp.cache.cache import CacheProvider
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.convertion import as_a
from rogw.tranp.lang.di import LazyDI
from rogw.tranp.lang.locator import Invoker, Locator
from rogw.tranp.module.loader import ModuleDependencyProvider
from rogw.tranp.module.types import ModulePath
from rogw.tranp.syntax.ast.entrypoints import EntrypointLoader
from rogw.tranp.syntax.ast.parser import SyntaxParser
from rogw.tranp.syntax.ast.query import Query
from rogw.tranp.syntax.ast.resolver import SymbolMapping
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node


@injectable
def entrypoint_loader(locator: Locator, dependencies: ModuleDependencyProvider) -> EntrypointLoader:
	"""エントリーポイントローダーを生成

	Args:
		locator: ロケーター @inject
		dependencies: @inject
	Returns:
		エントリーポイントローダー
	"""
	def handler(module_path: ModulePath) -> defs.Entrypoint:
		shared_di = as_a(LazyDI, locator)
		# XXX 共有が必須のモジュールを事前に解決
		shared_di.resolve(SyntaxParser)
		shared_di.resolve(CacheProvider)
		shared_di.resolve(SymbolMapping)
		dependency_di = LazyDI.instantiate(dependencies())
		new_di = shared_di.combine(dependency_di)
		new_di.rebind(Locator, lambda: new_di)
		new_di.rebind(Invoker, lambda: new_di.invoke)
		new_di.bind(ModulePath, lambda: module_path)
		return new_di.resolve(defs.Entrypoint)

	return handler


def entrypoint(query: Query[Node]) -> defs.Entrypoint:
	"""エントリーポイントを解決

	Args:
		query: ノードクエリー
	Returns:
		エントリーポイント
	"""
	return query.by('file_input').as_a(defs.Entrypoint)
