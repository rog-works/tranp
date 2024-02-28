import re
from types import UnionType
from unittest import TestCase
from rogw.tranp.analyze.errors import UnresolvedSymbolError

from rogw.tranp.analyze.symbols import Symbols
from rogw.tranp.ast.dsn import DSN
import rogw.tranp.compatible.python.classes as classes
from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.errors import LogicError
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


def _ast(before: str, after: str) -> str:
	_start = 6
	_func = 'file_input.function_def'
	_Base = f'file_input.class_def[{_start + 1}]'
	_Sub = f'file_input.class_def[{_start + 2}]'
	_Sub_init = f'{_Sub}.class_def_raw.block.function_def[1]'
	_Sub_first_number = f'{_Sub}.class_def_raw.block.function_def[2]'
	_Sub_local_ref = f'{_Sub}.class_def_raw.block.function_def[3]'
	_Sub_member_ref = f'{_Sub}.class_def_raw.block.function_def[4]'
	_Sub_member_write = f'{_Sub}.class_def_raw.block.function_def[5]'
	_Sub_param_ref = f'{_Sub}.class_def_raw.block.function_def[6]'
	_Sub_list_ref = f'{_Sub}.class_def_raw.block.function_def[7]'
	_Sub_base_ref = f'{_Sub}.class_def_raw.block.function_def[8]'
	_Sub_returns = f'{_Sub}.class_def_raw.block.function_def[9]'
	_Sub_invoke_method = f'{_Sub}.class_def_raw.block.function_def[10]'
	_Sub_decl_with_pop = f'{_Sub}.class_def_raw.block.function_def[11]'
	_Sub_decl_locals = f'{_Sub}.class_def_raw.block.function_def[12]'
	_Sub_assign_with_param = f'{_Sub}.class_def_raw.block.function_def[13]'
	_Sub_relay_access = f'{_Sub}.class_def_raw.block.function_def[14]'
	_Sub_fill_list = f'{_Sub}.class_def_raw.block.function_def[15]'
	_CalcOps = f'file_input.class_def[{_start + 3}]'
	_AliasOps = f'file_input.class_def[{_start + 4}]'
	_TupleOps = f'file_input.class_def[{_start + 5}]'
	_CompOps = f'file_input.class_def[{_start + 6}]'

	aliases = {
		'__main__.import.xyz': 'file_input.import_stmt[2]',

		'__main__.value': 'file_input.anno_assign',

		'__main__.func.block': f'{_func}.function_def_raw.block',

		'Base': f'{_Base}',
		'Base.__init__.params': f'{_Base}.class_def_raw.block.function_def.function_def_raw.parameters',
		'Base.__init__.return': f'{_Base}.class_def_raw.block.function_def.function_def_raw.typed_none',
		'Base.__init__.block': f'{_Base}.class_def_raw.block.function_def.function_def_raw.block',

		'Sub': f'{_Sub}',
		'Sub.C': f'{_Sub}.class_def_raw.block.class_def',
		'Sub.C.block': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block',
		'Sub.C.class_func': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def',
		'Sub.C.class_func.params': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.parameters',
		'Sub.C.class_func.return': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.typed_getitem',
		'Sub.C.class_func.block': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.block',
		'Sub.__init__.params': f'{_Sub_init}.function_def_raw.parameters',
		'Sub.__init__.return': f'{_Sub_init}.function_def_raw.typed_none',
		'Sub.__init__.block': f'{_Sub_init}.function_def_raw.block',
		'Sub.__init__.block': f'{_Sub_init}.function_def_raw.block',
		'Sub.first_number.block': f'{_Sub_first_number}.function_def_raw.block',
		'Sub.local_ref.params': f'{_Sub_local_ref}.function_def_raw.parameters',
		'Sub.local_ref.return': f'{_Sub_local_ref}.function_def_raw.typed_none',
		'Sub.local_ref.block': f'{_Sub_local_ref}.function_def_raw.block',
		'Sub.member_ref.block': f'{_Sub_member_ref}.function_def_raw.block',
		'Sub.member_write.block': f'{_Sub_member_write}.function_def_raw.block',
		'Sub.param_ref.params': f'{_Sub_param_ref}.function_def_raw.parameters',
		'Sub.param_ref.block': f'{_Sub_param_ref}.function_def_raw.block',
		'Sub.list_ref.params': f'{_Sub_list_ref}.function_def_raw.parameters',
		'Sub.list_ref.block': f'{_Sub_list_ref}.function_def_raw.block',
		'Sub.base_ref.block': f'{_Sub_base_ref}.function_def_raw.block',
		'Sub.returns.return': f'{_Sub_returns}.function_def_raw.typed_var',
		'Sub.returns.block': f'{_Sub_returns}.function_def_raw.block',
		'Sub.invoke_method.block': f'{_Sub_invoke_method}.function_def_raw.block',
		'Sub.decl_with_pop.block': f'{_Sub_decl_with_pop}.function_def_raw.block',
		'Sub.decl_locals.block': f'{_Sub_decl_locals}.function_def_raw.block',
		'Sub.decl_locals.closure.block': f'{_Sub_decl_locals}.function_def_raw.block.function_def.function_def_raw.block',

		'CompOps.list_comp.block': f'{_CompOps}.class_def_raw.block.function_def[0].function_def_raw.block',
	}
	return DSN.join(aliases[before], after)


def _mod(before: str, after: str) -> str:
	aliases = {
		'xyz': 'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz',
		'classes': 'rogw.tranp.compatible.python.classes',
	}
	return DSN.join(aliases[before], after)


class TestSymbols(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		('__main__.Sub.decl_locals.a', list, False),
		('__main__.Sub.decl_locals.closure.b', list, True),
		('__main__.Sub.decl_locals.a', dict, False),
		('__main__.Sub.decl_locals.closure.b', dict, False),
		('__main__.AliasOps.func.d', list, False),
		('__main__.AliasOps.func.d', dict, False),  # XXX エイリアスはdictそのものではないが要検討
	])
	def test_is_a(self, fullyname: str, standard_type: type[Standards], expected: bool) -> None:
		symbols = self.fixture.get(Symbols)
		symbol = symbols.from_fullyname(fullyname)
		self.assertEqual(symbols.is_a(symbol, standard_type), expected)

	@data_provider([
		('__main__.TypeAlias', 'TypeAlias'),

		('__main__.Z', 'Z'),

		('__main__.value', 'int'),

		('__main__.Base', 'Base'),
		('__main__.Base.base_str', 'str'),

		('__main__.Sub', 'Sub'),

		('__main__.Sub.C', 'C'),
		('__main__.Sub.C.value', 'str'),
		('__main__.Sub.C.class_func', 'class_func(C) -> dict<str, int>'),

		('__main__.Sub.numbers', 'list<int>'),

		('__main__.Sub.__init__', '__init__(Sub) -> None'),
		('__main__.Sub.__init__.self', 'Sub'),

		('__main__.Sub.local_ref', 'local_ref(Sub) -> None'),
		('__main__.Sub.local_ref.self', 'Sub'),
		('__main__.Sub.local_ref.value', 'bool'),

		('__main__.Sub.member_ref', 'member_ref(Sub) -> None'),
		('__main__.Sub.member_ref.self', 'Sub'),
		('__main__.Sub.member_write', 'member_write(Sub) -> None'),
		('__main__.Sub.member_write.self', 'Sub'),

		('__main__.Sub.param_ref', 'param_ref(Sub, int) -> None'),
		('__main__.Sub.param_ref.self', 'Sub'),
		('__main__.Sub.param_ref.param', 'int'),

		('__main__.Sub.list_ref', 'list_ref(Sub, list<Sub>) -> None'),
		('__main__.Sub.list_ref.self', 'Sub'),
		('__main__.Sub.list_ref.subs', 'list<Sub>'),

		('__main__.Sub.base_ref', 'base_ref(Sub) -> None'),
		('__main__.Sub.base_ref.self', 'Sub'),

		('__main__.Sub.returns', 'returns(Sub) -> str'),
		('__main__.Sub.returns.self', 'Sub'),

		('__main__.Sub.invoke_method', 'invoke_method(Sub) -> None'),
		('__main__.Sub.invoke_method.self', 'Sub'),

		('__main__.Sub.decl_with_pop.poped', 'int'),

		('__main__.Sub.decl_locals', 'decl_locals(Sub) -> int'),
		('__main__.Sub.decl_locals.a', 'int'),
		('__main__.Sub.decl_locals.closure', 'closure() -> list<int>'),
		('__main__.Sub.decl_locals.closure.b', 'list<int>'),
		('__main__.Sub.decl_locals.if.for.i', 'int'),
		('__main__.Sub.decl_locals.if.for.try.e', 'Exception'),

		('__main__.Sub.relay_access.s', 'str'),

		('__main__.Sub.fill_list.n_x3', 'list<int>'),

		('__main__.CalcOps.unary.n_neg', 'int'),
		('__main__.CalcOps.unary.n_not', 'bool'),
		('__main__.CalcOps.binary.n', 'int'),
		('__main__.CalcOps.binary.nb0', 'int'),
		('__main__.CalcOps.binary.nb1', 'int'),
		('__main__.CalcOps.binary.fn0', 'float'),
		('__main__.CalcOps.binary.fn1', 'float'),
		('__main__.CalcOps.binary.fn2', 'float'),
		('__main__.CalcOps.binary.fb0', 'float'),
		('__main__.CalcOps.binary.fb1', 'float'),
		('__main__.CalcOps.binary.result', 'float'),
		('__main__.CalcOps.binary.l_in', 'bool'),
		('__main__.CalcOps.binary.l_not_in', 'bool'),
		('__main__.CalcOps.binary.n_is', 'bool'),
		('__main__.CalcOps.binary.n_is_not', 'bool'),
		('__main__.CalcOps.tenary.n', 'int'),
		('__main__.CalcOps.tenary.s', 'str'),
		('__main__.CalcOps.tenary.s_or_null', 'Union<str, None>'),

		('__main__.AliasOps.func', 'func(AliasOps, Z2=Z) -> None'),
		('__main__.AliasOps.func.z2', 'Z2=Z'),
		('__main__.AliasOps.func.d', 'DSI=dict<str, int>'),
		('__main__.AliasOps.func.d_in_v', 'int'),
		('__main__.AliasOps.func.d2', 'DSI2=dict<str, DSI=dict<str, int>>'),
		('__main__.AliasOps.func.d2_in_dsi', 'DSI=dict<str, int>'),
		('__main__.AliasOps.func.d2_in_dsi_in_v', 'int'),
		('__main__.AliasOps.func.z2_in_x', 'X'),
		('__main__.AliasOps.func.new_z2_in_x', 'X'),

		('__main__.TupleOps.unpack.for.key0', 'str'),
		('__main__.TupleOps.unpack.for.value0', 'int'),
		('__main__.TupleOps.unpack.for.value1', 'int'),
		('__main__.TupleOps.unpack.for.key1', 'str'),
		('__main__.TupleOps.unpack.for.pair0', 'Pair<str, int>'),
		('__main__.TupleOps.unpack.for.key10', 'str'),
		('__main__.TupleOps.unpack.for.value10', 'DSI=dict<str, int>'),
		('__main__.TupleOps.unpack.for.value11', 'DSI=dict<str, int>'),
		('__main__.TupleOps.unpack.for.key11', 'str'),
		('__main__.TupleOps.unpack.for.pair10', 'Pair<str, DSI=dict<str, int>>'),

		('__main__.TupleOps.unpack_assign.a', 'str'),  # XXX Pythonのシンタックス上は不正。一旦保留
		('__main__.TupleOps.unpack_assign.b', 'int'),  # XXX 〃

		('__main__.CompOps.list_comp.values0', 'list<int>'),
		('__main__.CompOps.list_comp.values1', 'list<int>'),
		('__main__.CompOps.list_comp.values2', 'list<int>'),
		('__main__.CompOps.list_comp.strs', 'list<str>'),
		('__main__.CompOps.list_comp.value', 'int'),

		('__main__.CompOps.dict_comp.kvs0', 'dict<str, int>'),
		('__main__.CompOps.dict_comp.kvs1', 'dict<str, int>'),
		('__main__.CompOps.dict_comp.kvs2', 'dict<str, int>'),

		('__main__.EnumOps.Values', 'Values'),
		('__main__.EnumOps.Values.A', 'int'),  # Enumの定数値を直接参照するとEnum型ではなく、オリジナルの型になる ※情報を損なわないようにするため
		('__main__.EnumOps.Values.B', 'int'),  # 〃
		('__main__.EnumOps.cls_assign.a', 'Values'),
		('__main__.EnumOps.cls_assign.d', 'dict<Values, str>'),
		('__main__.EnumOps.cls_assign.da', 'str'),
		('__main__.EnumOps.assign.a', 'Values'),
		('__main__.EnumOps.assign.d', 'dict<Values, str>'),
		('__main__.EnumOps.assign.da', 'str'),
		('__main__.EnumOps.cast.e', 'Values'),
		('__main__.EnumOps.cast.n', 'int'),
	])
	def test_from_fullyname(self, fullyname: str, expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		symbol = symbols.from_fullyname(fullyname)
		self.assertEqual(str(symbol), expected)

	@data_provider([
		('__main__.CalcOps.tenary.n_or_s', UnresolvedSymbolError, r'Only Nullable.'),
	])
	def test_from_fullyname_error(self, fullyname: str, expected_error: type[Exception], expected: re.Pattern[str]) -> None:
		symbols = self.fixture.get(Symbols)
		with self.assertRaisesRegex(expected_error, expected):
			str(symbols.from_fullyname(fullyname))

	@data_provider([
		(int, _mod('classes', int.__name__)),
		(float, _mod('classes', float.__name__)),
		(str, _mod('classes', str.__name__)),
		(bool, _mod('classes', bool.__name__)),
		(tuple, _mod('classes', tuple.__name__)),
		(classes.Pair, _mod('classes', classes.Pair.__name__)),
		(list, _mod('classes', list.__name__)),
		(dict, _mod('classes', dict.__name__)),
		(classes.Unknown, _mod('classes', classes.Unknown.__name__)),
		(UnionType, _mod('classes', 'Union')),
		(None, _mod('classes', 'None')),
	])
	def test_type_of_standard(self, standard_type: type[Standards] | None, expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		self.assertEqual(symbols.type_of_standard(standard_type).types.fullyname, expected)

	@data_provider([
		(_ast('__main__.import.xyz', 'import_names.name'), _mod('xyz', 'Z'), 'Z'),
		(_ast('__main__.value', 'assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('__main__.value', 'typed_var'), _mod('classes', 'int'), 'int'),
		(_ast('__main__.value', 'number'), _mod('classes', 'int'), 'int'),

		(_ast('Base', ''), '__main__.Base', 'Base'),
		(_ast('Base', 'class_def_raw.name'), '__main__.Base', 'Base'),

		(_ast('Base.__init__.params', 'paramvalue.typedparam.name'), '__main__.Base', 'Base'),
		(_ast('Base.__init__.return', ''), _mod('classes', 'None'), 'None'),
		(_ast('Base.__init__.block', 'anno_assign.assign_namelist.getattr'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'anno_assign.typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'anno_assign.string'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'comment_stmt'), _mod('classes', 'Unknown'), 'Unknown'),

		(_ast('Sub', ''), '__main__.Sub', 'Sub'),
		(_ast('Sub', 'class_def_raw.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub', 'class_def_raw.typed_arguments.typed_argvalue.typed_var'), '__main__.Base', 'Base'),

		(_ast('Sub.C', ''), '__main__.Sub.C', 'C'),
		(_ast('Sub.C.block', 'anno_assign.assign_namelist.var'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.C.block', 'anno_assign.typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.C.block', 'anno_assign.string'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.C.class_func', ''), '__main__.Sub.C.class_func', 'class_func(C) -> dict<str, int>'),
		(_ast('Sub.C.class_func.params', 'paramvalue.typedparam.name'), '__main__.Sub.C', 'C'),
		(_ast('Sub.C.class_func.return', ''), _mod('classes', 'dict'), 'dict<str, int>'),
		(_ast('Sub.C.class_func.block', 'return_stmt.dict'), _mod('classes', 'dict'), 'dict<str, int>'),

		(_ast('Sub.__init__.params', 'paramvalue.typedparam.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub.__init__.return', ''), _mod('classes', 'None'), 'None'),
		(_ast('Sub.__init__.block', 'funccall'), '__main__.Base', 'Base'),
		(_ast('Sub.__init__.block', 'funccall.getattr.funccall.var'), _mod('classes', 'super'), 'super'),
		(_ast('Sub.__init__.block', 'anno_assign'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign.assign_namelist.getattr'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign.typed_getitem'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign.list'), _mod('classes', 'list'), 'list<Unknown>'),  # XXX 空のリストは型を補完できないためlist<Unknown>になる

		(_ast('Sub.first_number.block', 'return_stmt'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.local_ref.params', 'paramvalue.typedparam.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub.local_ref.block', 'assign'), _mod('classes', 'bool'), 'bool'),
		(_ast('Sub.local_ref.block', 'funccall.var'), _mod('classes', 'print'), 'print(Any) -> None'),
		(_ast('Sub.local_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'bool'), 'bool'),
		(_ast('Sub.local_ref.return', ''), _mod('classes', 'None'), 'None'),

		(_ast('Sub.member_ref.block', 'funccall[0].arguments.argvalue'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.member_ref.block', 'funccall[1].arguments.argvalue'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.member_write.block', 'assign[0].assign_namelist.getattr'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.member_write.block', 'assign[0].number'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.member_write.block', 'assign[1].assign_namelist.getattr'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.member_write.block', 'assign[1].string'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.param_ref.params', 'paramvalue[0].typedparam.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub.param_ref.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.param_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.list_ref.params', 'paramvalue[0].typedparam.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub.list_ref.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'list'), 'list<Sub>'),
		(_ast('Sub.list_ref.block', 'funccall[0].arguments.argvalue'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.list_ref.block', 'funccall[1].arguments.argvalue'), _mod('classes', 'list'), 'list<int>'),

		(_ast('Sub.base_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.returns.return', ''), _mod('classes', 'str'), 'str'),
		(_ast('Sub.returns.block', 'return_stmt'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.invoke_method.block', 'funccall.getattr'), '__main__.Sub.invoke_method', 'invoke_method(Sub) -> None'),

		(_ast('Sub.decl_with_pop.block', 'assign.assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.decl_with_pop.block', 'assign.funccall'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.decl_locals.block', 'if_stmt.block.assign.assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.decl_locals.closure.block', 'assign.assign_namelist.var'), _mod('classes', 'list'), 'list<int>'),

		(_ast('CompOps.list_comp.block', 'aug_assign.assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('CompOps.list_comp.block', 'aug_assign.getitem'), _mod('classes', 'float'), 'float'),
	])
	def test_type_of(self, full_path: str, expected: str, attrs_expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		node = self.fixture.shared_nodes.by(full_path)
		symbol = symbols.type_of(node)
		self.assertEqual(symbol.types.fullyname, expected)
		self.assertEqual(str(symbol), attrs_expected)
