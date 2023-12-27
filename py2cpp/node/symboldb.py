from typing import NamedTuple, TypeAlias

from py2cpp.ast.dns import domainize
from py2cpp.errors import LogicError
from py2cpp.module.module import Module
from py2cpp.module.modules import Modules
import py2cpp.node.definition as defs


class SymbolRow(NamedTuple):
	"""シンボル情報

	Attributes:
		ref_path: 参照パス
		org_path: 参照パス(オリジナル)
		module: 展開先のモジュール
		symbol: シンボルノード
		types: タイプ(クラス/関数全般)
	"""

	ref_path: str
	org_path: str
	module: Module
	symbol: defs.Symbol
	types: defs.Types


SymbolDB: TypeAlias = dict[str, SymbolRow]
DeclVar: TypeAlias = defs.Parameter | defs.AnnoAssign | defs.MoveAssign


class SymbolDBFactory:
	"""シンボルテーブルファクトリー"""

	@classmethod
	def create(cls, modules: Modules) -> SymbolDB:
		"""シンボルテーブルを生成

		Args:
			modules (Modules): モジュールマネージャー
		Returns:
			SymbolDB: シンボルテーブル
		"""
		main = modules.main

		# メインモジュール(Types)を展開
		db, decl_vars, import_nodes = cls.__pluck_main(main)

		# インポートモジュール(Types)を展開
		# XXX 別枠として分離するより、ステートメントの中で処理するのが理想
		# XXX また、ステートメントのスコープも合わせて考慮
		for import_node in import_nodes:
			module = modules.load(import_node.module_path.tokens)
			imported_db = cls.__pluck_imported(main, module)
			expanded_db = {
				row.org_path: SymbolRow(row.org_path, row.org_path, row.module, row.symbol, row.types)
				for _, row in imported_db.items()
			}
			# import句で明示したシンボルに限定
			imported_symbol_names = [symbol.tokens for symbol in import_node.import_symbols]
			filtered_db = {
				path: row
				for path, row in imported_db.items()
				if row.symbol.tokens in imported_symbol_names
			}
			db = {**expanded_db, **filtered_db, **db}

		# 標準ライブラリ(Types)を展開
		for module in modules.core_libralies:
			imported_db = cls.__pluck_imported(main, module)
			expanded_db = {
				row.org_path: SymbolRow(row.org_path, row.org_path, row.module, row.symbol, row.types)
				for _, row in imported_db.items()
			}
			# 第1層で宣言されているTypesに限定
			primary_symbol_names = [
				node.symbol.tokens
				for node in module.entrypoint(defs.Entrypoint).statements
				if isinstance(node, defs.Types)
			]
			filtered_db = {
				path: row
				for path, row in imported_db.items()
				if row.symbol.tokens in primary_symbol_names
			}
			db = {**expanded_db, **filtered_db, **db}

			# XXX インポートモジュール側に展開
			for import_node in import_nodes:
				filtered_db = {
					path.replace(row.module.path, import_node.module_path.tokens): row
					for path, row in imported_db.items()
					if row.symbol.tokens in primary_symbol_names
				}
				db = {**filtered_db, **db}

		# メインモジュールの変数シンボルを展開
		for var in decl_vars:
			# XXX This以外を登録
			if not var.symbol.is_a(defs.This):
				db[var.symbol.domain_id] = cls.__resolve_var_type(var, db)

		return db

	@classmethod
	def __pluck_main(cls, main: Module) -> tuple[SymbolDB, list[DeclVar], list[defs.Import]]:
		"""メインモジュールの全シンボルを展開

		Args:
			module (Module): メインモジュール
		Returns:
			tuple[SymbolDB, list[DeclVar], list[defs.Import]]: (シンボルテーブル, 変数リスト, インポートリスト)
		"""
		db: SymbolDB = {}
		decl_vars: list[DeclVar] = []
		import_nodes: list[defs.Import] = []
		entrypoint = main.entrypoint(defs.Entrypoint)
		for node in entrypoint.flatten():
			if isinstance(node, defs.Types):
				db[node.domain_id] = SymbolRow(node.domain_id, node.domain_id, node.module, node.symbol, node)

			if type(node) is defs.Import:
				import_nodes.append(node)

			if type(node) is defs.Function:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.ClassMethod:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Constructor:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Method:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Class:
				decl_vars.extend(node.vars)
			elif type(node) is defs.Enum:
				decl_vars.extend(node.vars)

		# XXX calculatedに含まれないためエントリーポイントは個別に処理
		decl_vars = [*entrypoint.decl_vars, *decl_vars]

		return db, decl_vars, import_nodes

	@classmethod
	def __pluck_imported(cls, main: Module, imported: Module) -> SymbolDB:
		"""インポートモジュールのシンボルを展開

		Args:
			main (Module): メインモジュール
			imported (Module): インポートモジュール
		Returns:
			SymbolDB: シンボルテーブル
		"""
		db: SymbolDB = {}
		entrypoint = imported.entrypoint(defs.Entrypoint)
		for node in entrypoint.flatten():
			# FIXME 一旦Typesに限定
			if isinstance(node, defs.Types):
				ref_domain_id = node.domain_id.replace(node.module.path, main.path)
				db[ref_domain_id] = SymbolRow(ref_domain_id, node.domain_id, main, node.symbol, node)

		return db

	@classmethod
	def __resolve_var_type(cls, var: DeclVar, db: SymbolDB) -> SymbolRow:
		"""シンボルテーブルから変数の型を解決

		Args:
			var (DeclVar): 変数
			db (SymbolDB): シンボルテーブル
		Returns:
			SymbolRow: シンボル情報
		"""
		type_symbol = cls.__fetch_type_symbol(var)
		candidates = []
		if type_symbol is not None:
			candidates = [type_symbol.domain_id, type_symbol.domain_name]
		else:
			# 型が不明な変数はUnknownにフォールバック
			# XXX Unknownの名前は重要なので定数化などの方法で明示
			candidates = [domainize(var.module.path, 'Unknown')]

		for candidate in candidates:
			if candidate in db:
				return db[candidate]

		raise LogicError(f'Unresolve var type. symbol: {var.symbol.tokens}')

	@classmethod
	def __fetch_type_symbol(cls, var: DeclVar) -> defs.Symbol | None:
		"""変数の型のシンボルノードを取得

		Args:
			var (DeclVar): 変数
		Returns:
			Symbol: シンボルノード
		"""
		if isinstance(var, (defs.AnnoAssign, defs.Parameter)):
			if var.var_type.is_a(defs.Symbol):
				return var.var_type.as_a(defs.Symbol)
			elif var.var_type.is_a(defs.GenericType):
				return var.var_type.as_a(defs.GenericType).symbol

		return None
