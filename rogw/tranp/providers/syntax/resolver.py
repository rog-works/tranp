from rogw.tranp.syntax.ast.resolver import SymbolMapping
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node


def symbol_mapping() -> SymbolMapping:
	"""ノードのシンボルマッピングデータを生成

	Returns:
		シンボルマッピングデータ
	Note:
		登録順にmatch_featureで評価されるため、整形目的で並び順を変更しないこと
	"""
	return SymbolMapping[Node](
		symbols={
			# -- General --
			defs.Entrypoint: ['file_input'],
			# -- Statement compound --
			defs.Block: ['block'],
			defs.IfClause: ['if_clause'],
			defs.ElseIf: ['elif_clause'],
			defs.Else: ['else_clause'],
			defs.If: ['if_stmt'],
			defs.While: ['while_stmt'],
			defs.For: ['for_stmt'],
			defs.Catch: ['except_clause'],
			defs.TryClause: ['try_clause'],
			defs.Try: ['try_stmt'],
			defs.WithEntry: ['with_item'],
			defs.With: ['with_stmt'],
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
			defs.Parameter: ['paramvalue', 'starparam', 'kwparams'],
			defs.Decorator: ['decorator'],
			# -- Statement simple --
			defs.MoveAssign: ['assign'],
			defs.AnnoAssign: ['anno_assign', 'class_var_assign'],
			defs.AugAssign: ['aug_assign'],
			defs.Delete: ['del_stmt'],
			defs.Return: ['return_stmt'],
			defs.Yield: ['yield_stmt'],
			defs.Assert: ['assert_stmt'],
			defs.Throw: ['raise_stmt'],
			defs.Pass: ['pass_stmt'],
			defs.Break: ['break_stmt'],
			defs.Continue: ['continue_stmt'],
			defs.Comment: ['comment_stmt'],
			defs.Import: ['import_stmt'],
			# -- Primary --
			defs.Argument: ['argvalue', 'starargs', 'kwargs'],
			defs.InheritArgument: ['typed_argvalue'],
			defs.ArgumentLabel: ['name'],
			defs.DeclClassVar: ['var'],
			defs.DeclThisVarForward: ['var'],
			defs.DeclThisVar: ['getattr'],
			defs.DeclClassParam: ['name'],
			defs.DeclThisParam: ['name'],
			defs.DeclParam: ['name'],
			defs.DeclLocalVar: ['var', 'name'],
			defs.TypesName: ['name'],
			defs.AltTypesName: ['var'],
			defs.ImportName: ['name'],
			defs.ImportAsName: ['import_as_name'],
			defs.Relay: ['getattr'],
			defs.ClassRef: ['var'],
			defs.ThisRef: ['var'],
			defs.Var: ['var', 'name'],
			defs.Indexer: ['getitem'],
			defs.ImportPath: ['dotted_name'],
			defs.DecoratorPath: ['dotted_name'],
			defs.RelayOfType: ['typed_getattr'],
			defs.VarOfType: ['typed_var'],
			defs.ListType: ['typed_getitem'],
			defs.DictType: ['typed_getitem'],
			defs.CallableType: ['typed_getitem'],
			defs.CustomType: ['typed_getitem'],
			defs.UnionType: ['typed_or_expr'],
			defs.NullType: ['typed_none'],
			defs.TypeParameters: ['typed_list', 'typed_elipsis'],
			defs.Super: ['funccall'],
			defs.FuncCall: ['funccall'],
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
			defs.TernaryOperator: ['ternary_test'],
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
			defs.Tuple: ['tuple'],
			defs.Null: ['const_none'],
			# -- Expression --
			defs.Group: ['group_expr'],
			defs.Spread: ['star_expr'],
			defs.Lambda: ['lambdadef'],
			# -- Terminal --
			defs.Empty: ['__empty__'],
		},
		fallback=defs.Terminal
	)
