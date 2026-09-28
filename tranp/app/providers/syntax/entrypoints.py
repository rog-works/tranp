import tranp.app.syntax.node.definition as defs
from tranp.app.cache.cache import CacheProvider
from tranp.app.lang.annotation import injectable
from tranp.app.lang.convertion import as_a
from tranp.app.lang.di import LazyDI
from tranp.app.lang.locator import Invoker, Locator
from tranp.app.module.loader import ModuleDependencyProvider
from tranp.app.module.types import ModulePath
from tranp.app.syntax.ast.entrypoints import EntrypointLoader
from tranp.app.syntax.ast.parser import SyntaxParser
from tranp.app.syntax.ast.query import Query
from tranp.app.syntax.ast.resolver import SymbolMapping
from tranp.app.syntax.node.node import Node


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
