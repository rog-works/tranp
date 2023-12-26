from typing import NamedTuple, TypeAlias

from py2cpp.ast.path import EntryPath
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

		# XXX 別枠として分離するより、ステートメントの中で処理するのが理想
		# XXX また、ステートメントのスコープも合わせて考慮
		for import_node in import_nodes:
			module = modules.load(import_node.module_path.to_string())
			imported_db = cls.__pluck_imported(main, module)
			expanded_db = {
				row.org_path: SymbolRow(row.org_path, row.org_path, row.module, row.symbol, row.types)
				for _, row in imported_db.items()
			}
			# import句で明示したシンボルに限定
			imported_symbol_names = [symbol.to_string() for symbol in import_node.import_symbols]
			filtered_db = {
				path: row
				for path, row in imported_db.items()
				if row.symbol.to_string() in imported_symbol_names
			}
			db = {**expanded_db, **filtered_db, **db}

		for module in modules.core_libralies:
			imported_db = cls.__pluck_imported(main, module)
			expanded_db = {
				row.org_path: SymbolRow(row.org_path, row.org_path, row.module, row.symbol, row.types)
				for _, row in imported_db.items()
			}
			# 第1層で宣言されているTypesに限定
			primary_symbol_names = [
				node.symbol.to_string()
				for node in module.entrypoint(defs.Entrypoint).statements
				if isinstance(node, defs.Types)
			]
			filtered_db = {
				path: row
				for path, row in imported_db.items()
				if row.symbol.to_string() in primary_symbol_names
			}
			db = {**expanded_db, **filtered_db, **db}

		for var in decl_vars:
			scope = var.scope if type(var) is not defs.Parameter else var.parent.as_a(defs.Function).block.scope
			path = EntryPath.join(scope, var.symbol.to_string())
			db[path.origin] = cls.__resolve_symbol(var, db)

		return db

	@classmethod
	def __pluck_main(cls, module: Module) -> tuple[SymbolDB, list[DeclVar], list[defs.Import]]:
		db: SymbolDB = {}
		decl_vars: list[DeclVar] = []
		import_nodes: list[defs.Import] = []
		for node in module.entrypoint(defs.Entrypoint).calculated():
			if isinstance(node, defs.Types):
				path = EntryPath.join(node.scope, node.symbol.to_string())
				db[path.origin] = SymbolRow(path.origin, path.origin, node.module, node.symbol, node)

			if type(node) is defs.Import:
				import_nodes.append(node)

			if type(node) is defs.Entrypoint:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Function:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.ClassMethod:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Method:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Class:
				decl_vars.extend(node.vars)
			elif type(node) is defs.Enum:
				decl_vars.extend(node.vars)

		return db, decl_vars, import_nodes

	@classmethod
	def __pluck_imported(cls, expand_module: Module, imported: Module) -> SymbolDB:
		db: SymbolDB = {}
		for node in imported.entrypoint(defs.Entrypoint).calculated():
			# FIXME 一旦Typesに限定
			if isinstance(node, defs.Types):
				org_path = EntryPath.join(node.scope, node.symbol.to_string())
				path = EntryPath.join(expand_module.path, org_path.relativefy(node.module.path).origin)
				db[path.origin] = SymbolRow(path.origin, org_path.origin, expand_module, node.symbol, node)

		return db

	@classmethod
	def __resolve_symbol(cls, var: DeclVar, db: SymbolDB) -> SymbolRow:
		type_name = cls.__resolve_type_name(var)
		candidates = [
			EntryPath.join(var.scope, type_name),
			EntryPath.join(var.module.path, type_name),
		]
		for candidate in candidates:
			if candidate.origin in db:
				return db[candidate.origin]

		raise LogicError(f'Unresolve var type symbol. symbol: {var.symbol.to_string()}')

	@classmethod
	def __resolve_type_name(cls, var: DeclVar) -> str:
		if isinstance(var, (defs.AnnoAssign, defs.Parameter)):
			if var.symbol.is_a(defs.This):
				# XXX 自己参照の場合は名前空間からクラス名を取る
				return EntryPath(var.namespace).last()[0]
			elif var.var_type.is_a(defs.Symbol):
				return var.var_type.to_string()
			elif var.var_type.is_a(defs.GenericType):
				return var.var_type.as_a(defs.GenericType).symbol.to_string()

		# XXX Unknownの名前は重要なので定数化などの方法で明示
		return 'Unknown'
