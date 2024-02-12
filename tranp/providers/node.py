from tranp.ast.query import Query
from tranp.ast.resolver import SymbolMapping
import tranp.node.definition as defs
from tranp.node.node import Node


def entrypoint(query: Query[Node]) -> Node:
	return query.by('file_input')


def symbol_mapping() -> SymbolMapping:
	return SymbolMapping(
		symbols={
			# -- General --
			'file_input': defs.Entrypoint,
			# -- Statement compound --
			'block': defs.Block,
			'elif_': defs.ElseIf,
			'if_stmt': defs.If,
			'while_stmt': defs.While,
			'for_in': defs.ForIn,
			'for_stmt': defs.For,
			'except_clause': defs.Catch,
			'try_stmt': defs.Try,
			'function_def': defs.Function,
			# 'function_def': defs.ClassMethod,
			# 'function_def': defs.Constructor,
			# 'function_def': defs.Method,
			# 'function_def': defs.Closure,
			'class_def': defs.Class,
			# 'class_def': defs.Enum,
			'class_assign': defs.AltClass,
			'template_assign': defs.TemplateClass,
			# -- Function/Class Elements --
			'paramvalue': defs.Parameter,
			'starparam': defs.Parameter,
			'decorator': defs.Decorator,
			# -- Statement simple --
			'assign': defs.MoveAssign,
			'anno_assign': defs.AnnoAssign,
			'aug_assign': defs.AugAssign,
			'return_stmt': defs.Return,
			'raise_stmt': defs.Throw,
			'pass_stmt': defs.Pass,
			'break_stmt': defs.Break,
			'continue_stmt': defs.Continue,
			'import_stmt': defs.Import,
			# -- Primary --
			'getattr': defs.Fragment,
			'var': defs.Fragment,
			'name': defs.Fragment,
			# 'var': defs.ClassDeclVar,
			# 'getattr': defs.ThisDeclVar,
			# 'name': defs.ParamClass,
			# 'name': defs.ParamThis,
			# '': defs.LocalDeclVar,
			# 'name': defs.TypesName,
			# 'name': defs.ImportName,
			# 'getattr': defs.Relay,
			# '': defs.ClassVar,
			# '': defs.ThisVar,
			# '': defs.Variable,
			'dotted_name': defs.Path,
			# 'dotted_name': defs.ImportPath,
			# 'dotted_name': defs.DecoratorPath,
			'getitem': defs.Indexer,
			'typed_getattr': defs.TypeRelay,
			'typed_var': defs.TypeVar,
			'typed_getitem': defs.GenericType,
			# 'typed_getitem': defs.ListType,
			# 'typed_getitem': defs.DictType,
			# 'typed_getitem': defs.CallableType,
			# 'typed_getitem': defs.CustomType,
			'typed_or_expr': defs.UnionType,
			'typed_none': defs.NullType,
			'typed_list': defs.TypeParameters,
			'funccall': defs.FuncCall,
			# 'funccall': defs.Super,
			'argvalue': defs.Argument,
			'typed_argvalue': defs.InheritArgument,
			'elipsis': defs.Elipsis,
			# -- Operator --
			'factor': defs.Factor,
			'not_test': defs.NotCompare,
			'or_test': defs.OrCompare,
			'and_test': defs.AndCompare,
			'comparison': defs.Comparison,
			'or_expr': defs.OrBitwise,
			'xor_expr': defs.XorBitwise,
			'and_expr': defs.AndBitwise,
			'shift_expr': defs.ShiftBitwise,
			'sum': defs.Sum,
			'term': defs.Term,
			# 'group_expr': defs.Group,
			# -- Literal --
			'number': defs.Number,
			# 'number': defs.Integer,
			# 'number': defs.Float,
			'string': defs.String,
			# 'string': defs.Comment,
			'const_true': defs.Truthy,
			'const_false': defs.Falsy,
			'key_value': defs.Pair,
			'list': defs.List,
			'dict': defs.Dict,
			'const_none': defs.Null,
			# -- Expression --
			'group_expr': defs.Group,
			# -- Terminal --
			# '': defs.Terminal,
			'__empty__': defs.Empty,
		},
		fallback=defs.Terminal
	)
