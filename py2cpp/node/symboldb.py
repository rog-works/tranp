from typing import TypeAlias

from py2cpp.ast.travarsal import EntryPath
from py2cpp.errors import LogicError
from py2cpp.module.module import Module
from py2cpp.module.modules import Modules
import py2cpp.node.definition as defs
from py2cpp.node.node import Node

SymbolDB: TypeAlias = dict[str, defs.Types]

class SymbolDBFactory:
	def create(self, modules: Modules) -> SymbolDB:
		main = modules.main
		db, decl_vars, import_nodes = self.__pluck_main(main)

		# XXX 別枠として分離するより、ステートメントの中で処理するのが正しい。また、importを実行したスコープも考慮する必要がある
		# FIXME importで宣言したシンボルで参照範囲が制限されていない
		for import_node in import_nodes:
			module = modules.load(import_node.module_path.to_string())
			db = {**db, **self.__pluck_imported(main, module)}

		for module in modules.core_libralies:
			db = {**db, **self.__pluck_imported(main, module)}

		for var in decl_vars:
			path = EntryPath.join(var.scope, var.symbol.to_string())
			db[path.origin] = self.__resolve_symbol(var, db)

		return db

	def __pluck_main(self, module: Module) -> tuple[SymbolDB, list[defs.AnnoAssign | defs.MoveAssign], list[defs.Import]]:
		db: SymbolDB = {}
		decl_vars: list[defs.AnnoAssign | defs.MoveAssign] = []
		import_nodes: list[defs.Import] = []
		for node in module.entrypoint(Node).calculated():
			if isinstance(node, (defs.Function, defs.Class, defs.Enum)):
				path = EntryPath.join(node.scope, node.symbol.to_string())
				db[path.origin] = node

			if type(node) is defs.Import:
				import_nodes.append(node)

			if type(node) is defs.Entrypoint:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Function:
				decl_vars.extend(node.block.decl_vars)
			elif type(node) is defs.ClassMethod:
				decl_vars.extend(node.block.decl_vars)
			elif type(node) is defs.Method:
				decl_vars.extend(node.block.decl_vars)
			elif type(node) is defs.Class:
				decl_vars.extend(node.vars)
			elif type(node) is defs.Enum:
				decl_vars.extend(node.vars)

		return db, decl_vars, import_nodes

	def __pluck_imported(self, main: Module, imported: Module) -> SymbolDB:
		db: SymbolDB = {}
		for node in imported.entrypoint(Node).calculated():
			# FIXME 一旦Typesに限定
			if isinstance(node, (defs.Function, defs.Class, defs.Enum)):
				org_path = EntryPath.join(node.scope, node.symbol.to_string())
				path = EntryPath.join(main.path, org_path.relativefy(node.module.path).origin)
				db[path.origin] = node

		return db

	def __resolve_symbol(self, var: defs.AnnoAssign | defs.MoveAssign, db: SymbolDB) -> defs.Types:
		type_name = self.__resolve_type_name(var)
		candidates = [
			EntryPath.join(var.scope, type_name),
			EntryPath.join(var.module.path, type_name),
		]
		for candidate in candidates:
			if candidate.origin in db:
				return db[candidate.origin]

		raise LogicError(f'Unresolve var type symbol. symbol: {var.symbol.to_string()}')

	def __resolve_type_name(self, var: defs.AnnoAssign | defs.MoveAssign) -> str:
		if type(var) is defs.AnnoAssign:
			if var.var_type.is_a(defs.This) and var.symbol.to_string() == 'self':
				# XXX 名前空間末尾のクラス名を取る
				return EntryPath(var.namespace).last()[0]
			elif var.var_type.is_a(defs.Symbol):
				return var.var_type.to_string()
			else:
				return var.var_type.as_a(defs.GenericType).symbol.to_string()

		# XXX Unknownの名前は重要なので定数化などの方法で明示
		return 'Unknown'
