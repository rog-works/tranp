from typing import NamedTuple, TypeAlias

from py2cpp.ast.dns import domainize
from py2cpp.errors import LogicError
from py2cpp.module.module import Module
from py2cpp.module.modules import Modules
import py2cpp.node.definition as defs


class SymbolRow(NamedTuple):
	ref_path: str
	org_path: str
	module: Module
	symbol: defs.Symbol
	types: defs.Types


SymbolDB: TypeAlias = dict[str, SymbolRow]
DeclVar: TypeAlias = defs.Parameter | defs.AnnoAssign | defs.MoveAssign


class SymbolDBFactory:
	@classmethod
	def create(cls, modules: Modules) -> SymbolDB:
		main = modules.main
		db, decl_vars, import_nodes = cls.__pluck_main(main)

		# インポートモジュールの追加
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

		# 標準ライブラリの追加
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

			# XXX インポートモジュール側にも展開
			for import_node in import_nodes:
				filtered_db = {
					path.replace(row.module.path, import_node.module_path.tokens): row
					for path, row in imported_db.items()
					if row.symbol.tokens in primary_symbol_names
				}
				db = {**filtered_db, **db}

		for var in decl_vars:
			# Thisは登録から除外
			if var.symbol.is_a(defs.This):
				pass
			# ThisVarはクラス直下に配置
			elif var.symbol.is_a(defs.ThisVar):
				db[var.symbol.domain_id] = cls.__resolve_var_type(var, db)
			# それ以外はスコープ配下に配置
			else:
				db[var.symbol.domain_id] = cls.__resolve_var_type(var, db)

		return db

	@classmethod
	def __pluck_main(cls, module: Module) -> tuple[SymbolDB, list[DeclVar], list[defs.Import]]:
		db: SymbolDB = {}
		decl_vars: list[DeclVar] = []
		import_nodes: list[defs.Import] = []
		entrypoint = module.entrypoint(defs.Entrypoint)
		for node in entrypoint.calculated():
			if isinstance(node, defs.Types):
				db[node.domain_id] = SymbolRow(node.domain_id, node.domain_id, node.module, node.symbol, node)

			if type(node) is defs.Import:
				import_nodes.append(node)

			if type(node) is defs.Entrypoint:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Function:
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
		decl_vars.extend(entrypoint.decl_vars)

		return db, decl_vars, import_nodes

	@classmethod
	def __pluck_imported(cls, expand_module: Module, imported: Module) -> SymbolDB:
		db: SymbolDB = {}
		entrypoint = imported.entrypoint(defs.Entrypoint)
		for node in entrypoint.calculated():
			# FIXME 一旦Typesに限定
			if isinstance(node, defs.Types):
				ref_domain_id = node.domain_id.replace(node.module.path, expand_module.path)
				db[ref_domain_id] = SymbolRow(ref_domain_id, node.domain_id, expand_module, node.symbol, node)

		return db

	@classmethod
	def __resolve_var_type(cls, var: DeclVar, db: SymbolDB) -> SymbolRow:
		type_symbol = cls.__fetch_type_symbol(var)
		candidates = []
		if type_symbol is not None:
			candidates = [type_symbol.domain_id, type_symbol.domain_name]
		else:
			# XXX Unknownの名前は重要なので定数化などの方法で明示
			type_name = 'Unknown'
			candidates = [domainize(var.scope, type_name), domainize(var.module.path, type_name)]

		for candidate in candidates:
			if candidate in db:
				return db[candidate]

		raise LogicError(f'Unresolve var type symbol. symbol: {var.symbol.tokens}')

	@classmethod
	def __fetch_type_symbol(cls, var: DeclVar) -> defs.Symbol | None:
		if isinstance(var, (defs.AnnoAssign, defs.Parameter)):
			if var.var_type.is_a(defs.Symbol):
				return var.var_type.as_a(defs.Symbol)
			elif var.var_type.is_a(defs.GenericType):
				return var.var_type.as_a(defs.GenericType).symbol

		return None
