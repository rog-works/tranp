from collections.abc import Iterator

from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.module.types import LibraryPaths
from rogw.tranp.semantics.errors import MustBeImplementedError, SymbolNotDefinedError
from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.semantics.reflection.db import SymbolDB
import rogw.tranp.syntax.node.definition as defs


class SymbolFinder:
	"""シンボル検索インターフェイス"""

	@injectable
	def __init__(self, library_paths: LibraryPaths) -> None:
		"""インスタンスを生成

		Args:
			library_paths: 標準ライブラリーパスリスト @inject
		"""
		self.__library_paths = [module_path.path for module_path in library_paths]

	def get_object(self, db: SymbolDB) -> IReflection:
		"""objectのシンボルを取得

		Args:
			db: シンボルテーブル
		Returns:
			シンボル
		Raises:
			MustBeImplementedError: objectが未実装
		Note:
			必ず存在すると言う前提。見つからない場合は実装ミス
		"""
		raw = self.__find_raw(db, [ModuleDSN(module_path) for module_path in self.__library_paths], object.__name__)
		if raw is not None:
			return raw

		raise MustBeImplementedError('"object" class is required.')

	def by(self, db: SymbolDB, fullyname: str) -> IReflection:
		"""完全参照名からシンボルを取得

		Args:
			db: シンボルテーブル
			fullyname: 完全参照名
		Returns:
			シンボル
		Raises:
			SymbolNotDefinedError: シンボルが見つからない
		"""
		if fullyname in db:
			return db[fullyname]

		raise SymbolNotDefinedError(f'fullyname: {fullyname}')

	def by_standard(self, db: SymbolDB, standard_type: type[Standards] | None) -> IReflection:
		"""標準クラスのシンボルを取得

		Args:
			db: シンボルテーブル
			standard_type: 標準クラス
		Returns:
			シンボル
		Raises:
			MustBeImplementedError: 標準クラスが未実装
		"""
		domain_name = standard_type.__name__ if standard_type is not None else 'None'
		raw = self.__find_raw(db, [ModuleDSN(module_path) for module_path in self.__library_paths], domain_name)
		if raw is not None:
			return raw

		raise MustBeImplementedError(f'"{domain_name}" class is required.')

	def by_symbolic(self, db: SymbolDB, node: defs.Symbolic) -> IReflection:
		"""シンボル系ノードからシンボルを取得

		Args:
			db: シンボルテーブル
			node: (Symbolic): シンボル系ノード
		Returns:
			シンボル
		Raises:
			SymbolNotDefinedError: シンボルが見つからない
		"""
		raw = self.find_by_symbolic(db, node)
		if raw is not None:
			return raw

		raise SymbolNotDefinedError(f'fullyname: {node.fullyname}')

	def find_by_symbolic(self, db: SymbolDB, node: defs.Symbolic, prop_name: str = '') -> IReflection | None:
		"""シンボルを検索。未検出の場合はNoneを返却

		Args:
			db: シンボルテーブル
			node: シンボル系ノード
			prop_name: プロパティー名(default = '')
		Returns:
			シンボル
		"""
		domain_name = ModuleDSN.local_joined(node.domain_name, prop_name)
		scopes = [scope for scope in self.__make_scopes(node.scope) if not self.__is_local_var_with_class_scope(db, node, scope)]
		if not isinstance(node, defs.Type):
			return self.__find_raw(db, scopes, domain_name)
		else:
			return self.__find_raw_for_type(db, scopes, domain_name)

	def __is_local_var_with_class_scope(self, db: SymbolDB, node: defs.Symbolic, scope: ModuleDSN) -> bool:
		"""ローカル変数の参照、且つクラス直下のスコープ参照の組み合わせか判定

		Args:
			db: シンボルテーブル
			node: シンボル系ノード
			scope: 探索スコープ
		Returns:
			True = 真
		Note:
			* FIXME メソッド内はクラス直下のスコープを参照出来ない。これを除外する判定にのみ使用
			* FIXME しかし、現状の判定は不完全であり、本質的にはノードのスコープ自体を是正しなければ期待通りに判定できない
		Examples:
			```python
			class A:
				class_var = 0
				def method(self, n: int = class_var) -> None:  # OK メソッドの仮引数内はクラススコープを参照出来る
					print(A.class_var)  # OK メソッド内はクラスと同じ参照スコープを持つ XXX が、それでは仮引数やメソッド内のローカル変数を参照できず片手落ち。この件により対応保留
					print(class_var)  # NG 上記の仕様により参照できない
					def closure(self, n: int = class_var) -> None: ...  # NG 同上
			```
		"""
		if not node.is_a(defs.Var):
			return False

		if 'paramvalue' in node.full_path:
			return False

		return scope.dsn in db and db[scope.dsn].types.is_a(defs.Class)

	def __make_scopes(self, scope: str) -> list[ModuleDSN]:
		"""スコープを元に探索スコープのリストを生成

		Args:
			scope: スコープ
		Returns:
			探索スコープリスト
		"""
		module_path, elems = ModuleDSN.expanded(scope)
		module_dsn = ModuleDSN(module_path)
		scopes_of_node = [module_dsn.join(*elems[:i]) for i in range(len(elems) + 1)]
		return list(reversed(scopes_of_node))

	def __find_raw(self, db: SymbolDB, scopes: list[ModuleDSN], domain_name: str) -> IReflection | None:
		"""シンボルを検索。未検出の場合はNoneを返却 (汎用)

		Args:
			db: シンボルテーブル
			scopes: 探索スコープリスト
			domain_name: ドメイン名
		Returns:
			シンボル
		"""
		for raw in self.__each_find_raw(db, scopes, domain_name):
			return raw

		return None

	def __find_raw_for_type(self, db: SymbolDB, scopes: list[ModuleDSN], domain_name: str) -> IReflection | None:
		"""シンボルを検索。未検出の場合はNoneを返却 (タイプノード専用)

		Args:
			db: シンボルテーブル
			scopes: 探索スコープリスト
			domain_name: ドメイン名
		Returns:
			シンボル
		Note:
			シンボル系ノードがタイプの場合はクラスかタイプのみを検索対象とする
		"""
		for raw in self.__each_find_raw(db, scopes, domain_name):
			if raw.decl.is_a(*defs.ClassOrTypeTs):
				return raw

		return None

	def __each_find_raw(self, db: SymbolDB, scopes: list[ModuleDSN], domain_name: str) -> Iterator[IReflection]:
		"""スコープを辿り、指定のドメイン名を持つシンボルを検索

		Args:
			db: シンボルテーブル
			scopes: 探索スコープリスト
			domain_name: ドメイン名
		Returns:
			イテレーター
		"""
		for scope in scopes:
			fullyname = scope.join(domain_name).dsn
			if fullyname in db:
				yield db[fullyname]

		raw = self.__find_imported_raw(db, scopes[0].module_path, domain_name)
		if raw:
			yield raw

		raw = self.__find_library_raw(db, domain_name)
		if raw:
			yield raw

	def __find_imported_raw(self, db: SymbolDB, on_module_path: str, domain_name: str) -> IReflection | None:
		"""ドメインが所属するモジュールのインポートノードを経由してシンボルを探索

		Args:
			db: シンボルテーブル
			on_module_path: 所属モジュールのパス
			domain_name: ドメイン名
		Returns:
			シンボル。未定義の場合はNone
		"""
		elems = ModuleDSN.expand_elements(domain_name)
		import_fullyname = ModuleDSN.full_joined(on_module_path, elems[0])
		if import_fullyname not in db:
			return None

		import_raw = db[import_fullyname]
		if not isinstance(import_raw.node, defs.ImportAsName):
			return None

		imported_dsn = ModuleDSN.full_join(import_raw.types.module_path, import_raw.node.domain_name)
		return self.__find_raw_recursive(db, imported_dsn, elems[1:])

	def __find_library_raw(self, db: SymbolDB, domain_name: str) -> IReflection | None:
		"""標準ライブラリーのモジュールからシンボルを探索

		Args:
			db: シンボルテーブル
			domain_name: ドメイン名
		Returns:
			シンボル。未定義の場合はNone
		"""
		elems = ModuleDSN.expand_elements(domain_name)
		for module_path in self.__library_paths:
			raw = self.__find_raw_recursive(db, ModuleDSN.full_join(module_path, elems[0]), elems[1:])
			if raw:
				return raw

		return None

	def __find_raw_recursive(self, db: SymbolDB, scope: ModuleDSN, elems: list[str]) -> IReflection | None:
		"""シンボルを再帰的に探索

		Args:
			db: シンボルテーブル
			scope: スコープ
			elems: ドメイン名の要素リスト
		Returns:
			シンボル。未定義の場合はNone
		"""
		if scope.dsn not in db:
			return None

		raw = db[scope.dsn]
		if len(elems) == 0:
			return raw

		new_scope = scope.join(elems[0])
		if new_scope.dsn in db:
			return self.__find_raw_recursive(db, new_scope, elems[1:])

		if not isinstance(raw.types, defs.Class):
			return None

		for inherit in raw.types.inherits:
			inherit_elems = [*scope.elements[:-1], inherit.type_name.tokens, elems[0]]
			inherit_scope = ModuleDSN.full_join(scope.module_path, *inherit_elems)
			if inherit_scope.dsn in db:
				return self.__find_raw_recursive(db, inherit_scope, elems[1:])

		return None
