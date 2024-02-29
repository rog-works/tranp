from rogw.tranp.ast.query import Query
from rogw.tranp.ast.resolver import SymbolMapping
import rogw.tranp.node.definition as defs
from rogw.tranp.node.node import Node


def entrypoint(query: Query[Node]) -> Node:
	"""エントリーポイントを解決

	Args:
		query (Query[Node]): ノードクエリー
	Returns:
		Node: エントリーポイント
	"""
	return query.by('file_input')


def symbol_mapping() -> SymbolMapping:
	"""ノードのシンボルマッピングデータを生成

	Returns:
		SymbolMapping: シンボルマッピングデータ
	"""
	return SymbolMapping[Node](
		symbols={
			# -- General --
			defs.Entrypoint: ['file_input'],
			# -- Statement compound --
			defs.Block: ['block'],
			defs.ElseIf: ['elif_'],
			defs.If: ['if_stmt'],
			defs.While: ['while_stmt'],
			defs.For: ['for_stmt'],
			defs.Catch: ['except_clause'],
			defs.Try: ['try_stmt'],
			defs.ClassMethod: ['function_def'],
			defs.Constructor: ['function_def'],
			defs.Method: ['function_def'],
			defs.Closure: ['function_def'],
			defs.Function: ['function_def'],
			defs.Enum: ['class_def'],
			defs.Class: ['class_def'],
			defs.AltClass: ['class_assign'],
			defs.TemplateClass: ['template_assign'],
			# -- Function/Class Elements --
			defs.Parameter: ['paramvalue', 'starparam'],
			defs.Decorator: ['decorator'],
			# -- Statement simple --
			defs.MoveAssign: ['assign'],
			defs.AnnoAssign: ['anno_assign'],
			defs.AugAssign: ['aug_assign'],
			defs.Return: ['return_stmt'],
			defs.Throw: ['raise_stmt'],
			defs.Pass: ['pass_stmt'],
			defs.Break: ['break_stmt'],
			defs.Continue: ['continue_stmt'],
			defs.Comment: ['comment_stmt'],
			defs.Import: ['import_stmt'],
			# -- Primary --
			defs.DeclClassVar: ['var'],
			defs.DeclThisVar: ['getattr'],
			defs.DeclClassParam: ['name'],
			defs.DeclThisParam: ['name'],
			defs.DeclParam: ['name'],
			defs.DeclLocalVar: ['var', 'name'],
			defs.TypesName: ['name'],
			defs.ImportName: ['name'],
			defs.Relay: ['getattr'],
			defs.ClassRef: ['var'],
			defs.ThisRef: ['var'],
			defs.ArgumentLabel: ['name'],
			defs.Variable: ['var', 'name'],
			defs.ImportPath: ['dotted_name'],
			defs.DecoratorPath: ['dotted_name'],
			defs.Indexer: ['getitem'],
			defs.RelayOfType: ['typed_getattr'],
			defs.VarOfType: ['typed_var'],
			defs.ListType: ['typed_getitem'],
			defs.DictType: ['typed_getitem'],
			defs.CallableType: ['typed_getitem'],
			defs.CustomType: ['typed_getitem'],
			defs.UnionType: ['typed_or_expr'],
			defs.NullType: ['typed_none'],
			defs.TypeParameters: ['typed_list'],
			defs.Super: ['funccall'],
			defs.FuncCall: ['funccall'],
			defs.Argument: ['argvalue'],
			defs.InheritArgument: ['typed_argvalue'],
			defs.Elipsis: ['elipsis'],
			defs.ForIn: ['for_in', 'comp_for_in'],
			defs.CompFor: ['comp_for'],
			defs.ListComp: ['list_comp'],
			defs.DictComp: ['dict_comp'],
			# -- Operator --
			defs.Factor: ['factor'],
			defs.NotCompare: ['not_test'],
			defs.OrCompare: ['or_test'],
			defs.AndCompare: ['and_test'],
			defs.Comparison: ['comparison'],
			defs.OrBitwise: ['or_expr'],
			defs.XorBitwise: ['xor_expr'],
			defs.AndBitwise: ['and_expr'],
			defs.ShiftBitwise: ['shift_expr'],
			defs.Sum: ['sum'],
			defs.Term: ['term'],
			defs.TenaryOperator: ['tenary_test'],
			# -- Literal --
			defs.Integer: ['number'],
			defs.Float: ['number'],
			defs.DocString: ['string'],
			defs.String: ['string'],
			defs.Truthy: ['const_true'],
			defs.Falsy: ['const_false'],
			defs.Pair: ['key_value'],
			defs.List: ['list'],
			defs.Dict: ['dict'],
			defs.Null: ['const_none'],
			# -- Expression --
			defs.Group: ['group_expr'],
			# -- Terminal --
			defs.Empty: ['__empty__'],
		},
		fallback=defs.Terminal
	)
