import os
import re
from unittest import TestCase

from rogw.tranp.analyze.plugin import PluginProvider
from rogw.tranp.analyze.symbols import Symbols
from rogw.tranp.app.io import appdir
from rogw.tranp.ast.dsn import DSN
from rogw.tranp.errors import LogicError
from rogw.tranp.implements.cpp.providers.analyze import cpp_plugin_provider
from rogw.tranp.lang.module import fullyname
import rogw.tranp.node.definition as defs
from rogw.tranp.node.node import Node
from rogw.tranp.translator.option import TranslatorOptions
from rogw.tranp.translator.py2cpp import Py2Cpp
from rogw.tranp.view.render import Renderer
from tests.test.fixture import Fixture
from tests.test.helper import data_provider, profiler
from tests.unit.rogw.tranp.translator.fixtures.test_py2cpp_expect import BlockExpects


def _ast(before: str, after: str) -> str:
	__begin_class = 9
	_Base = f'file_input.class_def[{__begin_class + 0}]'
	_DeclOps = f'file_input.class_def[{__begin_class + 1}]'
	_CVarOps = f'file_input.class_def[{__begin_class + 2}]'
	_FuncOps = f'file_input.class_def[{__begin_class + 3}]'
	_EnumOps = f'file_input.class_def[{__begin_class + 4}]'
	_AccessOps = f'file_input.class_def[{__begin_class + 5}]'
	_Alias = f'file_input.class_def[{__begin_class + 6}]'
	_CompOps = f'file_input.class_def[{__begin_class + 7}]'
	_ForOps = f'file_input.class_def[{__begin_class + 8}]'
	_ListOps = f'file_input.class_def[{__begin_class + 9}]'
	_DictOps = f'file_input.class_def[{__begin_class + 10}]'
	_CastOps = f'file_input.class_def[{__begin_class + 11}]'
	_Nullable = f'file_input.class_def[{__begin_class + 12}]'
	_Template = f'file_input.class_def[{__begin_class + 13}]'
	_template_func = f'file_input.function_def'

	aliases = {
		'import.typing': 'file_input.import_stmt[0]',

		'directive': 'file_input.funccall',

		'DSI': 'file_input.class_assign',

		'DeclOps': f'{_DeclOps}',

		'CVarOps.ret_raw.return': f'{_CVarOps}.class_def_raw.block.function_def[0].function_def_raw.block.return_stmt',
		'CVarOps.ret_cp.return': f'{_CVarOps}.class_def_raw.block.function_def[1].function_def_raw.block.return_stmt',
		'CVarOps.ret_csp.return': f'{_CVarOps}.class_def_raw.block.function_def[2].function_def_raw.block.return_stmt',
		'CVarOps.local_move.block': f'{_CVarOps}.class_def_raw.block.function_def[3].function_def_raw.block',
		'CVarOps.param_move.block': f'{_CVarOps}.class_def_raw.block.function_def[4].function_def_raw.block',
		'CVarOps.invoke_method.block': f'{_CVarOps}.class_def_raw.block.function_def[5].function_def_raw.block',
		'CVarOps.unary_calc.block': f'{_CVarOps}.class_def_raw.block.function_def[6].function_def_raw.block',
		'CVarOps.binary_calc.block': f'{_CVarOps}.class_def_raw.block.function_def[7].function_def_raw.block',
		'CVarOps.tenary_calc.block': f'{_CVarOps}.class_def_raw.block.function_def[8].function_def_raw.block',

		'FuncOps.print.block': f'{_FuncOps}.class_def_raw.block.function_def.function_def_raw.block',

		'EnumOps.Values': f'{_EnumOps}.class_def_raw.block.class_def',
		'EnumOps.assign.block': f'{_EnumOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'EnumOps.cast.block': f'{_EnumOps}.class_def_raw.block.function_def[2].function_def_raw.block',

		'AccessOps.__init__': f'{_AccessOps}.class_def_raw.block.function_def[0]',
		'AccessOps.dot.block': f'{_AccessOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'AccessOps.arrow.block': f'{_AccessOps}.class_def_raw.block.function_def[2].function_def_raw.block',
		'AccessOps.double_colon.block': f'{_AccessOps}.class_def_raw.block.function_def[3].function_def_raw.block',

		'Alias.Inner': f'{_Alias}.class_def_raw.block.class_def',
		'Alias.__init__': f'{_Alias}.class_def_raw.block.function_def[1]',
		'Alias.in_param_return': f'{_Alias}.class_def_raw.block.function_def[2]',
		'Alias.in_param_return2': f'{_Alias}.class_def_raw.block.function_def[3]',
		'Alias.in_local.block': f'{_Alias}.class_def_raw.block.function_def[4].function_def_raw.block',

		'CompOps.list_comp.block': f'{_CompOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'CompOps.dict_comp.block': f'{_CompOps}.class_def_raw.block.function_def[2].function_def_raw.block',

		'ForOps.range.block': f'{_ForOps}.class_def_raw.block.function_def[0].function_def_raw.block',
		'ForOps.enumerate.block': f'{_ForOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'ForOps.dict_items.block': f'{_ForOps}.class_def_raw.block.function_def[2].function_def_raw.block',

		'ListOps.len.block': f'{_ListOps}.class_def_raw.block.function_def[0].function_def_raw.block',
		'ListOps.pop.block': f'{_ListOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'ListOps.contains.block': f'{_ListOps}.class_def_raw.block.function_def[2].function_def_raw.block',
		'ListOps.fill.block': f'{_ListOps}.class_def_raw.block.function_def[3].function_def_raw.block',

		'DictOps.len.block': f'{_DictOps}.class_def_raw.block.function_def[0].function_def_raw.block',
		'DictOps.pop.block': f'{_DictOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'DictOps.keys.block': f'{_DictOps}.class_def_raw.block.function_def[2].function_def_raw.block',
		'DictOps.values.block': f'{_DictOps}.class_def_raw.block.function_def[3].function_def_raw.block',
		'DictOps.decl.block': f'{_DictOps}.class_def_raw.block.function_def[4].function_def_raw.block',
		'DictOps.contains.block': f'{_DictOps}.class_def_raw.block.function_def[5].function_def_raw.block',

		'CastOps.cast_binary.block': f'{_CastOps}.class_def_raw.block.function_def[0].function_def_raw.block',
		'CastOps.cast_string.block': f'{_CastOps}.class_def_raw.block.function_def[1].function_def_raw.block',

		'Nullable.params': f'{_Nullable}.class_def_raw.block.function_def[0]',
		'Nullable.returns': f'{_Nullable}.class_def_raw.block.function_def[1]',
		'Nullable.invalid_params': f'{_Nullable}.class_def_raw.block.function_def[2]',
		'Nullable.invalid_returns': f'{_Nullable}.class_def_raw.block.function_def[3]',
		'Nullable.var_move.block': f'{_Nullable}.class_def_raw.block.function_def[4].function_def_raw.block',

		'Template.T2Class': f'{_Template}.class_def_raw.block.class_def',
		'Template.__init__': f'{_Template}.class_def_raw.block.function_def[1]',
		'Template.class_method_t': f'{_Template}.class_def_raw.block.function_def[2]',
		'Template.class_method_t_and_class_t': f'{_Template}.class_def_raw.block.function_def[3]',
		'Template.method_t': f'{_Template}.class_def_raw.block.function_def[4]',
		'Template.method_t_and_class_t': f'{_Template}.class_def_raw.block.function_def[5]',

		'template_func': f'{_template_func}',
	}
	return DSN.join(aliases[before], after)


class TestPy2Cpp(TestCase):
	fixture = Fixture.make(__file__, {fullyname(PluginProvider): cpp_plugin_provider})

	def translator(self) -> Py2Cpp:
		renderer = Renderer(os.path.join(appdir(), 'example/template'))
		options = TranslatorOptions(verbose=False)
		return Py2Cpp(self.fixture.get(Symbols), renderer, options)

	@data_provider([
		(_ast('import.typing', ''), defs.Import, '// #include "typing.h"'),

		(_ast('directive', ''), defs.FuncCall, '#pragma once'),

		(_ast('DSI', ''), defs.AltClass, 'using DSI = std::map<std::string, int>;'),

		(_ast('DeclOps', ''), defs.Class, BlockExpects.DeclOps),

		(_ast('CVarOps.ret_raw.return', ''), defs.Return, 'return Base(0);'),
		(_ast('CVarOps.ret_cp.return', ''), defs.Return, 'return new Base(0);'),
		(_ast('CVarOps.ret_csp.return', ''), defs.Return, 'return std::make_shared<Base>(0);'),

		(_ast('CVarOps.local_move.block', 'anno_assign[0]'), defs.AnnoAssign, 'Base a = Base(0);'),
		(_ast('CVarOps.local_move.block', 'anno_assign[1]'), defs.AnnoAssign, 'Base* ap = &(a);'),
		(_ast('CVarOps.local_move.block', 'anno_assign[2]'), defs.AnnoAssign, 'std::shared_ptr<Base> asp = std::make_shared<Base>(0);'),
		(_ast('CVarOps.local_move.block', 'anno_assign[3]'), defs.AnnoAssign, 'Base& ar = a;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].block.assign[0]'), defs.MoveAssign, 'a = a;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].block.assign[1]'), defs.MoveAssign, 'a = *(ap);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].block.assign[2]'), defs.MoveAssign, 'a = *(asp);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].block.assign[3]'), defs.MoveAssign, 'a = ar;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].block.assign[0]'), defs.MoveAssign, 'ap = &(a);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].block.assign[1]'), defs.MoveAssign, 'ap = ap;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].block.assign[2]'), defs.MoveAssign, 'ap = (asp).get();'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].block.assign[3]'), defs.MoveAssign, 'ap = &(ar);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[6].block.assign'), defs.MoveAssign, 'asp = asp;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[7].block.assign[0]'), defs.MoveAssign, 'ar = a;'),  # XXX C++ではNGだが要件等 ※型推論のコストをかけてまでエラー判定が必要なのか微妙
		(_ast('CVarOps.local_move.block', 'if_stmt[7].block.assign[1]'), defs.MoveAssign, 'ar = *(ap);'),  # 〃
		(_ast('CVarOps.local_move.block', 'if_stmt[7].block.assign[2]'), defs.MoveAssign, 'ar = *(asp);'),  # 〃
		(_ast('CVarOps.local_move.block', 'if_stmt[7].block.assign[3]'), defs.MoveAssign, 'ar = ar;'),  # 〃

		(_ast('CVarOps.param_move.block', 'assign[0]'), defs.MoveAssign, 'Base a1 = a;'),
		(_ast('CVarOps.param_move.block', 'anno_assign[1]'), defs.AnnoAssign, 'Base a2 = *(ap);'),
		(_ast('CVarOps.param_move.block', 'anno_assign[2]'), defs.AnnoAssign, 'Base a3 = *(asp);'),
		(_ast('CVarOps.param_move.block', 'anno_assign[3]'), defs.AnnoAssign, 'Base a4 = ar;'),
		(_ast('CVarOps.param_move.block', 'assign[4]'), defs.MoveAssign, 'a = a1;'),
		(_ast('CVarOps.param_move.block', 'assign[5]'), defs.MoveAssign, 'ap = &(a2);'),
		(_ast('CVarOps.param_move.block', 'assign[6]'), defs.MoveAssign, 'ar = a4;'),  # XXX C++ではNGだが要件等 ※型推論のコストをかけてまでエラー判定が必要なのか微妙

		(_ast('CVarOps.invoke_method.block', 'funccall'), defs.FuncCall, 'this->invoke_method(*(asp), (asp).get(), asp);'),

		(_ast('CVarOps.unary_calc.block', 'assign[0]'), defs.MoveAssign, 'Base neg_a = -a;'),
		(_ast('CVarOps.unary_calc.block', 'assign[1]'), defs.MoveAssign, 'Base neg_a2 = -*(ap);'),
		(_ast('CVarOps.unary_calc.block', 'assign[2]'), defs.MoveAssign, 'Base neg_a3 = -*(asp);'),
		(_ast('CVarOps.unary_calc.block', 'assign[3]'), defs.MoveAssign, 'Base neg_a4 = -ar;'),

		(_ast('CVarOps.binary_calc.block', 'assign[0]'), defs.MoveAssign, 'Base add = a + *(ap) + *(asp) + ar;'),
		(_ast('CVarOps.binary_calc.block', 'assign[1]'), defs.MoveAssign, 'Base sub = a - *(ap) - *(asp) - ar;'),
		(_ast('CVarOps.binary_calc.block', 'assign[2]'), defs.MoveAssign, 'Base mul = a * *(ap) * *(asp) * ar;'),
		(_ast('CVarOps.binary_calc.block', 'assign[3]'), defs.MoveAssign, 'Base div = a / *(ap) / *(asp) / ar;'),
		(_ast('CVarOps.binary_calc.block', 'assign[4]'), defs.MoveAssign, 'Base calc = a + *(ap) * *(asp) - ar / a;'),
		(_ast('CVarOps.binary_calc.block', 'assign[5]'), defs.MoveAssign, 'bool is_a = a == *(ap) == *(asp) == ar;'),
		(_ast('CVarOps.binary_calc.block', 'assign[6]'), defs.MoveAssign, 'bool is_not_a = a != *(ap) != *(asp) != ar;'),

		(_ast('CVarOps.tenary_calc.block', 'assign[0]'), defs.MoveAssign, 'Base a2 = true ? a : Base();'),
		(_ast('CVarOps.tenary_calc.block', 'assign[1]'), defs.MoveAssign, 'Base a3 = true ? a : a;'),
		(_ast('CVarOps.tenary_calc.block', 'assign[2]'), defs.MoveAssign, 'Base* ap2 = true ? ap : ap;'),
		(_ast('CVarOps.tenary_calc.block', 'assign[3]'), defs.MoveAssign, 'std::shared_ptr<Base> asp2 = true ? asp : asp;'),
		(_ast('CVarOps.tenary_calc.block', 'assign[4]'), defs.MoveAssign, 'Base& ar2 = true ? ar : ar;'),
		(_ast('CVarOps.tenary_calc.block', 'assign[5]'), defs.MoveAssign, 'Base* ap_or_null = true ? ap : nullptr;'),

		(_ast('FuncOps.print.block', 'funccall'), defs.FuncCall, 'printf("message. %d, %f, %s", 1, 1.0, "abc");'),

		(_ast('EnumOps.Values', ''), defs.Enum, '/** Values */\npublic: enum class Values {\n\tA = 0,\n\tB = 1,\n};'),
		(_ast('EnumOps.assign.block', 'assign[0]'), defs.MoveAssign, 'EnumOps::Values a = EnumOps::Values::A;'),
		(_ast('EnumOps.assign.block', 'assign[1]'), defs.MoveAssign, 'std::map<EnumOps::Values, std::string> d = {\n\t{EnumOps::Values::A, "A"},\n\t{EnumOps::Values::B, "B"},\n};'),
		(_ast('EnumOps.assign.block', 'assign[2]'), defs.MoveAssign, 'std::string da = d[EnumOps::Values::A];'),
		(_ast('EnumOps.cast.block', 'assign[0]'), defs.MoveAssign, 'EnumOps::Values e = (EnumOps::Values)(0);'),
		(_ast('EnumOps.cast.block', 'assign[1]'), defs.MoveAssign, 'int n = (int)(EnumOps::Values::A);'),

		(_ast('AccessOps.__init__', ''), defs.Constructor, '/** Constructor */\npublic: AccessOps() : Base(0), sub_s("") {\n}'),

		(_ast('AccessOps.dot.block', 'funccall[0].arguments.argvalue'), defs.Argument, 'a.base_n'),
		(_ast('AccessOps.dot.block', 'funccall[1].arguments.argvalue'), defs.Argument, 'a.sub_s'),
		(_ast('AccessOps.dot.block', 'funccall[2].arguments.argvalue'), defs.Argument, 'a.sub_s.split'),
		(_ast('AccessOps.dot.block', 'funccall[3].arguments.argvalue'), defs.Argument, 'a.call()'),
		(_ast('AccessOps.dot.block', 'funccall[5].arguments.argvalue'), defs.Argument, 'dda[1][1].sub_s'),

		(_ast('AccessOps.arrow.block', 'funccall[0].arguments.argvalue'), defs.Argument, 'this->base_n'),
		(_ast('AccessOps.arrow.block', 'funccall[1].arguments.argvalue'), defs.Argument, 'this->sub_s'),
		(_ast('AccessOps.arrow.block', 'funccall[2].arguments.argvalue'), defs.Argument, 'this->call()'),
		(_ast('AccessOps.arrow.block', 'funccall[3].arguments.argvalue'), defs.Argument, 'ap->base_n'),
		(_ast('AccessOps.arrow.block', 'funccall[4].arguments.argvalue'), defs.Argument, 'ap->sub_s'),
		(_ast('AccessOps.arrow.block', 'funccall[5].arguments.argvalue'), defs.Argument, 'ap->call()'),
		(_ast('AccessOps.arrow.block', 'funccall[6].arguments.argvalue'), defs.Argument, 'asp->base_n'),
		(_ast('AccessOps.arrow.block', 'funccall[7].arguments.argvalue'), defs.Argument, 'asp->sub_s'),
		(_ast('AccessOps.arrow.block', 'funccall[8].arguments.argvalue'), defs.Argument, 'asp->call()'),

		(_ast('AccessOps.double_colon.block', 'funccall[0]'), defs.FuncCall, 'Base::call();'),
		(_ast('AccessOps.double_colon.block', 'funccall[1].arguments.argvalue'), defs.Argument, 'Base::class_base_n'),
		(_ast('AccessOps.double_colon.block', 'funccall[2].arguments.argvalue'), defs.Argument, 'AccessOps::class_base_n'),
		(_ast('AccessOps.double_colon.block', 'funccall[3].arguments.argvalue'), defs.Argument, 'EnumOps::Values::A'),
		(_ast('AccessOps.double_colon.block', 'anno_assign'), defs.AnnoAssign, 'std::map<EnumOps::Values, std::string> d = {\n\t{EnumOps::Values::A, "A"},\n\t{EnumOps::Values::B, "B"},\n};'),

		(_ast('Alias.Inner', ''), defs.Class, '/** Inner2 */\nclass Inner2 {\n\n};'),
		(_ast('Alias.__init__', ''), defs.Constructor, '/** Constructor */\npublic: Alias2() : inner(Alias2::Inner2()) {\n}'),
		(_ast('Alias.in_param_return', ''), defs.Method, '/** in_param_return */\npublic: Alias2 in_param_return(Alias2 a) {\n\n}'),
		(_ast('Alias.in_param_return2', ''), defs.Method, '/** in_param_return2 */\npublic: Alias2::Inner2 in_param_return2(Alias2::Inner2 i) {\n\n}'),
		(_ast('Alias.in_local.block', 'assign[0]'), defs.MoveAssign, 'Alias2 a = Alias2();'),
		(_ast('Alias.in_local.block', 'assign[1]'), defs.MoveAssign, 'Alias2::Inner2 i = Alias2::Inner2();'),

		(_ast('CompOps.list_comp.block', 'assign[1]'), defs.MoveAssign, BlockExpects.CompOps_list_comp_assign_values1),
		(_ast('CompOps.dict_comp.block', 'assign[1]'), defs.MoveAssign, BlockExpects.CompOps_dict_comp_assign_kvs1),

		(_ast('ForOps.range.block', 'for_stmt'), defs.For, 'for (auto i = 0; i < 10; i++) {\n\n}'),
		(_ast('ForOps.enumerate.block', 'for_stmt'), defs.For, BlockExpects.ForOps_enumerate_for_index_key),
		(_ast('ForOps.dict_items.block', 'for_stmt'), defs.For, 'for (auto& [key, value] : kvs) {\n\n}'),

		(_ast('ListOps.len.block', 'assign[1]'), defs.MoveAssign, 'int size_values = values.size();'),
		(_ast('ListOps.pop.block', 'assign[1]'), defs.MoveAssign, BlockExpects.ListOps_pop_assign_value0),
		(_ast('ListOps.pop.block', 'assign[2]'), defs.MoveAssign, BlockExpects.ListOps_pop_assign_value1),
		(_ast('ListOps.contains.block', 'assign[1]'), defs.MoveAssign, 'bool b_in = (std::find(values.begin(), values.end(), 1) != values.end());'),
		(_ast('ListOps.contains.block', 'assign[2]'), defs.MoveAssign, 'bool b_not_in = (std::find(values.begin(), values.end(), 1) == values.end());'),
		(_ast('ListOps.fill.block', 'assign'), defs.MoveAssign, 'std::vector<int> n_x3 = std::vector<int>(3, n);'),

		(_ast('DictOps.len.block', 'assign[1]'), defs.MoveAssign, 'int size_kvs = kvs.size();'),
		(_ast('DictOps.pop.block', 'assign[1]'), defs.MoveAssign, BlockExpects.DictOps_pop_assign_value0),
		(_ast('DictOps.pop.block', 'assign[2]'), defs.MoveAssign, BlockExpects.DictOps_pop_assign_value1),
		(_ast('DictOps.keys.block', 'assign[1]'), defs.MoveAssign, BlockExpects.DictOps_keys_assign_keys),
		(_ast('DictOps.values.block', 'assign[1]'), defs.MoveAssign, BlockExpects.DictOps_values_assign_values),
		(_ast('DictOps.decl.block', 'assign'), defs.MoveAssign, 'std::map<int, std::vector<int>> d = {{1, {\n\t{1},\n\t{2},\n\t{3},\n}}};'),
		(_ast('DictOps.contains.block', 'assign[1]'), defs.MoveAssign, 'bool b_in = d.contains("a");'),
		(_ast('DictOps.contains.block', 'assign[2]'), defs.MoveAssign, 'bool b_not_in = (!d.contains("a"));'),

		(_ast('CastOps.cast_binary.block', 'assign[0]'), defs.MoveAssign, 'int f_to_n = (int)(1.0);'),
		(_ast('CastOps.cast_binary.block', 'assign[1]'), defs.MoveAssign, 'float n_to_f = (float)(1);'),
		(_ast('CastOps.cast_binary.block', 'assign[2]'), defs.MoveAssign, 'bool n_to_b = (bool)(1);'),
		(_ast('CastOps.cast_binary.block', 'assign[3]'), defs.MoveAssign, 'int e_to_n = (int)(EnumOps::Values::A);'),

		(_ast('CastOps.cast_string.block', 'assign[0]'), defs.MoveAssign, 'std::string n_to_s = std::to_string(1);'),
		(_ast('CastOps.cast_string.block', 'assign[1]'), defs.MoveAssign, 'std::string f_to_s = std::to_string(1.0);'),
		(_ast('CastOps.cast_string.block', 'assign[2]'), defs.MoveAssign, 'int s_to_n = atoi(n_to_s);'),
		(_ast('CastOps.cast_string.block', 'assign[3]'), defs.MoveAssign, 'float s_to_f = atof(f_to_s);'),

		(_ast('Nullable.params', ''), defs.Method, '/** params */\npublic: void params(Base* p) {\n\n}'),
		(_ast('Nullable.returns', ''), defs.Method, '/** returns */\npublic: Base* returns() {\n\n}'),
		(_ast('Nullable.var_move.block', 'anno_assign'), defs.AnnoAssign, 'Base* p = nullptr;'),
		(_ast('Nullable.var_move.block', 'assign[1]'), defs.MoveAssign, 'p = &(base);'),
		(_ast('Nullable.var_move.block', 'assign[2]'), defs.MoveAssign, 'p = (sp).get();'),
		(_ast('Nullable.var_move.block', 'assign[3]'), defs.MoveAssign, 'p = nullptr;'),
		(_ast('Nullable.var_move.block', 'if_stmt.block.return_stmt'), defs.Return, 'return *(p);'),

		(_ast('Template.T2Class', ''), defs.Class, '/** T2Class */\ntemplate<typename T2>\nclass T2Class {\n\n};'),
		(_ast('Template.__init__', ''), defs.Constructor, '/** Constructor */\npublic: Template(T v) {\n\n}'),
		(_ast('Template.class_method_t', ''), defs.ClassMethod, '/** class_method_t */\npublic:\ntemplate<typename T2>\nstatic T2 class_method_t(T2 v2) {\n\n}'),
		(_ast('Template.class_method_t_and_class_t', ''), defs.ClassMethod, '/** class_method_t_and_class_t */\npublic:\ntemplate<typename T2>\nstatic T2 class_method_t_and_class_t(T v, T2 v2) {\n\n}'),
		(_ast('Template.method_t', ''), defs.Method, '/** method_t */\npublic:\ntemplate<typename T2>\nT2 method_t(T2 v2) {\n\n}'),
		(_ast('Template.method_t_and_class_t', ''), defs.Method, '/** method_t_and_class_t */\npublic:\ntemplate<typename T2>\nT2 method_t_and_class_t(T v, T2 v2) {\n\n}'),

		(_ast('template_func', ''), defs.Function, '/** template_func */\ntemplate<typename T>\nT template_func(T v) {\n\n}'),
	])
	def test_exec(self, full_path: str, expected_type: type[Node], expected: str) -> None:
		translator = self.translator()
		node = self.fixture.shared_nodes.by(full_path).as_a(expected_type)
		actual = translator.translate(node)
		self.assertEqual(actual, expected)

	@data_provider([
		(_ast('CVarOps.tenary_calc.block', 'assign[6]'), r'Tenary operation not allowed.'),

		(_ast('Nullable.invalid_params', ''), r'Unexpected UnionType.'),
		(_ast('Nullable.invalid_returns', ''), r'Unexpected UnionType.'),
	])
	def test_exec_error(self, full_path: str, expected: re.Pattern) -> None:
		translator = self.translator()
		node = self.fixture.shared_nodes.by(full_path)
		with self.assertRaisesRegex(LogicError, expected):
			translator.translate(node)
