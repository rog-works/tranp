import os
from unittest import TestCase

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.dsn.translation import alias_dsn
from rogw.tranp.i18n.i18n import I18n, TranslationMapping
from rogw.tranp.implements.cpp.providers.i18n import example_translation_mapping_cpp
from rogw.tranp.implements.cpp.providers.semantics import cpp_plugin_provider
from rogw.tranp.implements.cpp.transpiler.py2cpp import Py2Cpp
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.module import fullyname
from rogw.tranp.lang.profile import profiler
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.test.helper import data_provider
from rogw.tranp.transpiler.types import TranspilerOptions
from rogw.tranp.view.render import Renderer
from tests.test.fixture import Fixture
from tests.unit.rogw.tranp.implements.cpp.transpiler.fixtures.test_py2cpp_expect import BlockExpects


class ASTMapping:
	__begin_class = 13
	_Base = f'file_input.class_def[{__begin_class + 0}]'
	_Sub = f'file_input.class_def[{__begin_class + 1}]'
	_DeclOps = f'file_input.class_def[{__begin_class + 2}]'
	_CVarOps = f'file_input.class_def[{__begin_class + 3}]'
	_FuncOps = f'file_input.class_def[{__begin_class + 4}]'
	_EnumOps = f'file_input.class_def[{__begin_class + 5}]'
	_AccessOps = f'file_input.class_def[{__begin_class + 6}]'
	_Alias = f'file_input.class_def[{__begin_class + 7}]'
	_CompOps = f'file_input.class_def[{__begin_class + 8}]'
	_ForOps = f'file_input.class_def[{__begin_class + 9}]'
	_ListOps = f'file_input.class_def[{__begin_class + 10}]'
	_DictOps = f'file_input.class_def[{__begin_class + 11}]'
	_CastOps = f'file_input.class_def[{__begin_class + 12}]'
	_Nullable = f'file_input.class_def[{__begin_class + 13}]'
	_Template = f'file_input.class_def[{__begin_class + 14}]'
	_GenericOps = f'file_input.class_def[{__begin_class + 15}]'
	_Struct = f'file_input.class_def[{__begin_class + 16}]'
	_StringOps = f'file_input.class_def[{__begin_class + 17}]'
	_AssignOps = f'file_input.class_def[{__begin_class + 18}]'
	_template_func = f'file_input.function_def'

	aliases = {
		'import.typing': 'file_input.import_stmt[1]',

		'c_pragma': 'file_input.funccall[7]',
		'c_include': 'file_input.funccall[8]',
		'c_macro': 'file_input.funccall[9]',

		'DSI': 'file_input.class_assign',

		'DeclOps': f'{_DeclOps}',

		'Base.sub_implements': f'{_Base}.class_def_raw.block.function_def[0]',
		'Base.allowed_overrides': f'{_Base}.class_def_raw.block.function_def[1]',

		'Sub.block': f'{_Sub}.class_def_raw.block',

		'CVarOps.ret_raw.return': f'{_CVarOps}.class_def_raw.block.function_def[0].function_def_raw.block.return_stmt',
		'CVarOps.ret_cp.return': f'{_CVarOps}.class_def_raw.block.function_def[1].function_def_raw.block.return_stmt',
		'CVarOps.ret_csp.return': f'{_CVarOps}.class_def_raw.block.function_def[2].function_def_raw.block.return_stmt',
		'CVarOps.local_move.block': f'{_CVarOps}.class_def_raw.block.function_def[3].function_def_raw.block',
		'CVarOps.param_move.block': f'{_CVarOps}.class_def_raw.block.function_def[4].function_def_raw.block',
		'CVarOps.invoke_method.block': f'{_CVarOps}.class_def_raw.block.function_def[5].function_def_raw.block',
		'CVarOps.unary_calc.block': f'{_CVarOps}.class_def_raw.block.function_def[6].function_def_raw.block',
		'CVarOps.binary_calc.block': f'{_CVarOps}.class_def_raw.block.function_def[7].function_def_raw.block',
		'CVarOps.tenary_calc.block': f'{_CVarOps}.class_def_raw.block.function_def[8].function_def_raw.block',
		'CVarOps.declare.block': f'{_CVarOps}.class_def_raw.block.function_def[9].function_def_raw.block',
		'CVarOps.default_param.block': f'{_CVarOps}.class_def_raw.block.function_def[10].function_def_raw.block',
		'CVarOps.const_move.block': f'{_CVarOps}.class_def_raw.block.function_def[11].function_def_raw.block',
		'CVarOps.to_void.block': f'{_CVarOps}.class_def_raw.block.function_def[12].function_def_raw.block',
		'CVarOps.local_decl.block': f'{_CVarOps}.class_def_raw.block.function_def[13].function_def_raw.block',
		'CVarOps.addr_calc.block': f'{_CVarOps}.class_def_raw.block.function_def[14].function_def_raw.block',
		'CVarOps.raw.block': f'{_CVarOps}.class_def_raw.block.function_def[15].function_def_raw.block',
		'CVarOps.prop_relay.block': f'{_CVarOps}.class_def_raw.block.function_def[16].function_def_raw.block',

		'FuncOps.print.block': f'{_FuncOps}.class_def_raw.block.function_def[0].function_def_raw.block',
		'FuncOps.kw_params.block': f'{_FuncOps}.class_def_raw.block.function_def[1].function_def_raw.block',

		'EnumOps.Values': f'{_EnumOps}.class_def_raw.block.class_def',
		'EnumOps.assign.block': f'{_EnumOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'EnumOps.cast.block': f'{_EnumOps}.class_def_raw.block.function_def[2].function_def_raw.block',

		'AccessOps.__init__': f'{_AccessOps}.class_def_raw.block.function_def[1]',
		'AccessOps.dot.block': f'{_AccessOps}.class_def_raw.block.function_def[2].function_def_raw.block',
		'AccessOps.arrow.block': f'{_AccessOps}.class_def_raw.block.function_def[3].function_def_raw.block',
		'AccessOps.double_colon.block': f'{_AccessOps}.class_def_raw.block.function_def[4].function_def_raw.block',
		'AccessOps.indexer.block': f'{_AccessOps}.class_def_raw.block.function_def[5].function_def_raw.block',

		'Alias.__init__': f'{_Alias}.class_def_raw.block.function_def[1]',
		'Alias.Values': f'{_Alias}.class_def_raw.block.class_def[2]',
		'Alias.Inner': f'{_Alias}.class_def_raw.block.class_def[3]',
		'Alias.in_param_return': f'{_Alias}.class_def_raw.block.function_def[4]',
		'Alias.in_param_return2': f'{_Alias}.class_def_raw.block.function_def[5]',
		'Alias.in_local.block': f'{_Alias}.class_def_raw.block.function_def[6].function_def_raw.block',
		'Alias.in_class_method.block': f'{_Alias}.class_def_raw.block.function_def[7].function_def_raw.block',
		'Alias.InnerB.super_call.block': f'{_Alias}.class_def_raw.block.class_def[8].class_def_raw.block.function_def.function_def_raw.block',

		'CompOps.list_comp.block': f'{_CompOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'CompOps.dict_comp.block': f'{_CompOps}.class_def_raw.block.function_def[2].function_def_raw.block',

		'ForOps.range.block': f'{_ForOps}.class_def_raw.block.function_def[0].function_def_raw.block',
		'ForOps.enumerate.block': f'{_ForOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'ForOps.dict_items.block': f'{_ForOps}.class_def_raw.block.function_def[2].function_def_raw.block',

		'ListOps.len.block': f'{_ListOps}.class_def_raw.block.function_def[0].function_def_raw.block',
		'ListOps.pop.block': f'{_ListOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'ListOps.contains.block': f'{_ListOps}.class_def_raw.block.function_def[2].function_def_raw.block',
		'ListOps.fill.block': f'{_ListOps}.class_def_raw.block.function_def[3].function_def_raw.block',
		'ListOps.slice.block': f'{_ListOps}.class_def_raw.block.function_def[4].function_def_raw.block',
		'ListOps.delete.block': f'{_ListOps}.class_def_raw.block.function_def[5].function_def_raw.block',

		'DictOps.len.block': f'{_DictOps}.class_def_raw.block.function_def[0].function_def_raw.block',
		'DictOps.pop.block': f'{_DictOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'DictOps.keys.block': f'{_DictOps}.class_def_raw.block.function_def[2].function_def_raw.block',
		'DictOps.values.block': f'{_DictOps}.class_def_raw.block.function_def[3].function_def_raw.block',
		'DictOps.decl.block': f'{_DictOps}.class_def_raw.block.function_def[4].function_def_raw.block',
		'DictOps.contains.block': f'{_DictOps}.class_def_raw.block.function_def[5].function_def_raw.block',
		'DictOps.delete.block': f'{_DictOps}.class_def_raw.block.function_def[6].function_def_raw.block',

		'CastOps.cast_binary.block': f'{_CastOps}.class_def_raw.block.function_def[0].function_def_raw.block',
		'CastOps.cast_string.block': f'{_CastOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'CastOps.cast_class.block': f'{_CastOps}.class_def_raw.block.function_def[2].function_def_raw.block',

		'Nullable.params': f'{_Nullable}.class_def_raw.block.function_def[0]',
		'Nullable.returns': f'{_Nullable}.class_def_raw.block.function_def[1]',
		'Nullable.var_move.block': f'{_Nullable}.class_def_raw.block.function_def[2].function_def_raw.block',

		'Template.T2Class': f'{_Template}.class_def_raw.block.class_def',
		'Template.__init__': f'{_Template}.class_def_raw.block.function_def[1]',
		'Template.class_method_t': f'{_Template}.class_def_raw.block.function_def[2]',
		'Template.class_method_t_and_class_t': f'{_Template}.class_def_raw.block.function_def[3]',
		'Template.method_t': f'{_Template}.class_def_raw.block.function_def[4]',
		'Template.method_t_and_class_t': f'{_Template}.class_def_raw.block.function_def[5]',

		'GenericOps.temporal.block': f'{_GenericOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'GenericOps.new.block': f'{_GenericOps}.class_def_raw.block.function_def[2].function_def_raw.block',

		'Struct': f'{_Struct}',

		'StringOps.methods.block': f'{_StringOps}.class_def_raw.block.function_def[0].function_def_raw.block',
		'StringOps.slice.block': f'{_StringOps}.class_def_raw.block.function_def[1].function_def_raw.block',
		'StringOps.len.block': f'{_StringOps}.class_def_raw.block.function_def[2].function_def_raw.block',
		'StringOps.format.block': f'{_StringOps}.class_def_raw.block.function_def[3].function_def_raw.block',

		'AssignOps.assign.block': f'{_AssignOps}.class_def_raw.block.function_def.function_def_raw.block',

		'template_func': f'{_template_func}',
	}


def _ast(before: str, after: str) -> str:
	return ModuleDSN.local_joined(ASTMapping.aliases[before], after)


def fixture_translation_mapping(loader: IFileLoader) -> TranslationMapping:
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture_translations = {
		alias_dsn(ModuleDSN.full_joined(fixture_module_path, 'Alias')): 'Alias2',
		alias_dsn(ModuleDSN.full_joined(fixture_module_path, 'Alias.inner')): 'inner_b',
		alias_dsn(ModuleDSN.full_joined(fixture_module_path, 'Alias.Inner')): 'Inner2',
		alias_dsn(ModuleDSN.full_joined(fixture_module_path, 'Alias.Inner.V')): 'V2',
	}
	return example_translation_mapping_cpp(loader).merge(fixture_translations)


def make_renderer(i18n: I18n) -> Renderer:
	return Renderer([os.path.join(tranp_dir(), 'data/cpp/template')], i18n.t)


class TestPy2Cpp(TestCase):
	fixture = Fixture.make(__file__, {
		fullyname(Py2Cpp): Py2Cpp,
		fullyname(PluginProvider): cpp_plugin_provider,
		fullyname(TranslationMapping): fixture_translation_mapping,
		fullyname(TranspilerOptions): lambda: TranspilerOptions(verbose=False),
		fullyname(Renderer): make_renderer,
	})

	@data_provider([
		(_ast('import.typing', ''), defs.Import, '// #include "typing.h"'),

		(_ast('c_pragma', ''), defs.FuncCall, '#pragma once'),
		(_ast('c_include', ''), defs.FuncCall, '#include <memory>'),
		(_ast('c_macro', ''), defs.FuncCall, 'MACRO()'),

		(_ast('DSI', ''), defs.AltClass, 'using DSI = std::map<std::string, int>;'),

		(_ast('DeclOps', ''), defs.Class, BlockExpects.DeclOps),

		(_ast('Base.sub_implements', ''), defs.Function, 'public:\n/** sub_implements */\nvirtual void sub_implements() = 0;'),
		(_ast('Base.allowed_overrides', ''), defs.Function, 'public:\n/** allowed_overrides */\nvirtual int allowed_overrides() {\n\treturn 1;\n}'),

		(_ast('Sub.block', 'comment_stmt[5]'), defs.Comment, '// FIXME other: Any'),

		(_ast('CVarOps.ret_raw.return', ''), defs.Return, 'return Sub(0);'),
		(_ast('CVarOps.ret_cp.return', ''), defs.Return, 'return new Sub(0);'),
		(_ast('CVarOps.ret_csp.return', ''), defs.Return, 'return std::make_shared<Sub>(0);'),

		(_ast('CVarOps.local_move.block', 'anno_assign[0]'), defs.AnnoAssign, 'Sub a = Sub(0);'),
		(_ast('CVarOps.local_move.block', 'anno_assign[1]'), defs.AnnoAssign, 'Sub* ap = &(a);'),
		(_ast('CVarOps.local_move.block', 'anno_assign[2]'), defs.AnnoAssign, 'std::shared_ptr<Sub> asp = std::make_shared<Sub>(0);'),
		(_ast('CVarOps.local_move.block', 'anno_assign[3]'), defs.AnnoAssign, 'Sub& ar = a;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].if_clause.block.assign[0]'), defs.MoveAssign, 'a = a;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].if_clause.block.assign[1]'), defs.MoveAssign, 'a = *(ap);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].if_clause.block.assign[2]'), defs.MoveAssign, 'a = *(asp);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].if_clause.block.assign[3]'), defs.MoveAssign, 'a = ar;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].if_clause.block.assign[0]'), defs.MoveAssign, 'ap = &(a);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].if_clause.block.assign[1]'), defs.MoveAssign, 'ap = ap;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].if_clause.block.assign[2]'), defs.MoveAssign, 'ap = (asp).get();'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].if_clause.block.assign[3]'), defs.MoveAssign, 'ap = &(ar);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[6].if_clause.block.assign'), defs.MoveAssign, 'asp = asp;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[7].if_clause.block.assign[1]'), defs.MoveAssign, 'ar = a;'),  # XXX C++ではNGだが要件等 ※型推論のコストをかけてまでエラー判定が必要なのか微妙
		(_ast('CVarOps.local_move.block', 'if_stmt[7].if_clause.block.assign[3]'), defs.MoveAssign, 'ar = *(ap);'),  # 〃
		(_ast('CVarOps.local_move.block', 'if_stmt[7].if_clause.block.assign[5]'), defs.MoveAssign, 'ar = *(asp);'),  # 〃
		(_ast('CVarOps.local_move.block', 'if_stmt[7].if_clause.block.assign[7]'), defs.MoveAssign, 'ar = ar;'),  # 〃

		(_ast('CVarOps.param_move.block', 'assign[0]'), defs.MoveAssign, 'Sub a1 = a;'),
		(_ast('CVarOps.param_move.block', 'anno_assign[1]'), defs.AnnoAssign, 'Sub a2 = *(ap);'),
		(_ast('CVarOps.param_move.block', 'anno_assign[2]'), defs.AnnoAssign, 'Sub a3 = *(asp);'),
		(_ast('CVarOps.param_move.block', 'anno_assign[3]'), defs.AnnoAssign, 'Sub a4 = ar;'),
		(_ast('CVarOps.param_move.block', 'assign[4]'), defs.MoveAssign, 'a = a1;'),
		(_ast('CVarOps.param_move.block', 'assign[5]'), defs.MoveAssign, 'ap = &(a2);'),
		(_ast('CVarOps.param_move.block', 'assign[8]'), defs.MoveAssign, 'ar = a4;'),  # XXX C++ではNGだが要件等 ※型推論のコストをかけてまでエラー判定が必要なのか微妙

		(_ast('CVarOps.invoke_method.block', 'funccall'), defs.FuncCall, 'this->invoke_method(*(asp), (asp).get(), asp);'),

		(_ast('CVarOps.unary_calc.block', 'assign[0]'), defs.MoveAssign, 'Sub neg_a = -a;'),
		(_ast('CVarOps.unary_calc.block', 'assign[1]'), defs.MoveAssign, 'Sub neg_a2 = -*(ap);'),
		(_ast('CVarOps.unary_calc.block', 'assign[2]'), defs.MoveAssign, 'Sub neg_a3 = -*(asp);'),
		(_ast('CVarOps.unary_calc.block', 'assign[3]'), defs.MoveAssign, 'Sub neg_a4 = -ar;'),

		(_ast('CVarOps.binary_calc.block', 'assign[0]'), defs.MoveAssign, 'Sub add = a + *(ap) + *(asp) + ar;'),
		(_ast('CVarOps.binary_calc.block', 'assign[1]'), defs.MoveAssign, 'Sub sub = a - *(ap) - *(asp) - ar;'),
		(_ast('CVarOps.binary_calc.block', 'assign[2]'), defs.MoveAssign, 'Sub mul = a * *(ap) * *(asp) * ar;'),
		(_ast('CVarOps.binary_calc.block', 'assign[3]'), defs.MoveAssign, 'Sub div = a / *(ap) / *(asp) / ar;'),
		(_ast('CVarOps.binary_calc.block', 'assign[4]'), defs.MoveAssign, 'Sub calc = a + *(ap) * *(asp) - ar / a;'),
		(_ast('CVarOps.binary_calc.block', 'assign[5]'), defs.MoveAssign, 'bool is_a = a == *(ap) == *(asp) == ar;'),
		(_ast('CVarOps.binary_calc.block', 'assign[6]'), defs.MoveAssign, 'bool is_not_a = a != *(ap) != *(asp) != ar;'),
		(_ast('CVarOps.binary_calc.block', 'assign[7]'), defs.MoveAssign, 'bool is_null = apn == nullptr && apn != nullptr;'),

		(_ast('CVarOps.tenary_calc.block', 'assign[0]'), defs.MoveAssign, 'Sub a2 = true ? a : Sub();'),
		(_ast('CVarOps.tenary_calc.block', 'assign[1]'), defs.MoveAssign, 'Sub a3 = true ? a : a;'),
		(_ast('CVarOps.tenary_calc.block', 'assign[2]'), defs.MoveAssign, 'Sub* ap2 = true ? ap : ap;'),
		(_ast('CVarOps.tenary_calc.block', 'assign[3]'), defs.MoveAssign, 'std::shared_ptr<Sub> asp2 = true ? asp : asp;'),
		(_ast('CVarOps.tenary_calc.block', 'assign[4]'), defs.MoveAssign, 'Sub& ar2 = true ? ar : ar;'),
		(_ast('CVarOps.tenary_calc.block', 'assign[5]'), defs.MoveAssign, 'Sub* ap_or_null = true ? ap : nullptr;'),

		(_ast('CVarOps.declare.block', 'assign[1]'), defs.MoveAssign, 'std::vector<int>* arr_p = &(arr);'),
		(_ast('CVarOps.declare.block', 'assign[2]'), defs.MoveAssign, 'std::vector<int>* arr_p2 = new std::vector<int>();'),
		(_ast('CVarOps.declare.block', 'assign[3]'), defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp = std::shared_ptr<std::vector<int>>(new std::vector<int>({1}));'),
		(_ast('CVarOps.declare.block', 'assign[4]'), defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp2 = std::shared_ptr<std::vector<int>>(new std::vector<int>());'),
		(_ast('CVarOps.declare.block', 'assign[5]'), defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp3 = std::shared_ptr<std::vector<int>>(new std::vector<int>(2));'),
		(_ast('CVarOps.declare.block', 'assign[6]'), defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp4 = std::shared_ptr<std::vector<int>>(new std::vector<int>(2, 0));'),
		(_ast('CVarOps.declare.block', 'assign[7]'), defs.MoveAssign, 'std::vector<int>& arr_r = arr;'),
		(_ast('CVarOps.declare.block', 'assign[8]'), defs.MoveAssign, 'std::shared_ptr<int> n_sp_empty = std::shared_ptr<int>();'),
		(_ast('CVarOps.declare.block', 'assign[9]'), defs.MoveAssign, 'CVarOps* this_p = this;'),

		(_ast('CVarOps.default_param.block', 'assign[0]'), defs.MoveAssign, 'int n = ap ? ap->base_n : 0;'),
		(_ast('CVarOps.default_param.block', 'assign[1]'), defs.MoveAssign, 'int n2 = this->default_param();'),

		(_ast('CVarOps.const_move.block', 'assign[0]'), defs.MoveAssign, 'const Sub a_const0 = a;'),
		(_ast('CVarOps.const_move.block', 'assign[1]'), defs.MoveAssign, 'Sub a0 = a_const0;'),
		(_ast('CVarOps.const_move.block', 'assign[2]'), defs.MoveAssign, 'const Sub& r0_const = a_const0;'),
		(_ast('CVarOps.const_move.block', 'assign[3]'), defs.MoveAssign, 'const Sub* ap0_const = &(a_const0);'),

		(_ast('CVarOps.const_move.block', 'assign[4]'), defs.MoveAssign, 'const Sub* ap_const1 = ap;'),
		(_ast('CVarOps.const_move.block', 'assign[5]'), defs.MoveAssign, 'Sub a1 = *(ap_const1);'),
		(_ast('CVarOps.const_move.block', 'assign[6]'), defs.MoveAssign, 'const Sub& r_const1 = *(ap_const1);'),

		(_ast('CVarOps.const_move.block', 'assign[7]'), defs.MoveAssign, 'const std::shared_ptr<Sub> asp_const2 = asp;'),
		(_ast('CVarOps.const_move.block', 'assign[8]'), defs.MoveAssign, 'Sub a2 = *(asp_const2);'),  # XXX 本来の期待値は`std::shared_ptr<Sub>`の様な気がするが、CVarsはただのプロクシーとして実装しているため、操作結果はCSPとほぼ同等になる
		(_ast('CVarOps.const_move.block', 'assign[9]'), defs.MoveAssign, 'const Sub& r_const2 = *(asp_const2);'),  # 〃
		(_ast('CVarOps.const_move.block', 'assign[10]'), defs.MoveAssign, 'const Sub* ap_const2 = (asp_const2).get();'),  # 〃

		(_ast('CVarOps.const_move.block', 'assign[11]'), defs.MoveAssign, 'const Sub& r_const3 = r;'),
		(_ast('CVarOps.const_move.block', 'assign[12]'), defs.MoveAssign, 'Sub a3 = r_const3;'),
		(_ast('CVarOps.const_move.block', 'assign[13]'), defs.MoveAssign, 'const Sub* ap_const3 = &(r_const3);'),

		(_ast('CVarOps.to_void.block', 'assign[0]'), defs.MoveAssign, 'void* a_to_vp = static_cast<void*>(&(a));'),
		(_ast('CVarOps.to_void.block', 'assign[1]'), defs.MoveAssign, 'void* ap_to_vp = static_cast<void*>(ap);'),
		(_ast('CVarOps.to_void.block', 'assign[2]'), defs.MoveAssign, 'void* asp_to_vp = static_cast<void*>((asp).get());'),
		(_ast('CVarOps.to_void.block', 'assign[3]'), defs.MoveAssign, 'void* r_to_vp = static_cast<void*>(&(r));'),

		(_ast('CVarOps.local_decl.block', 'assign[0]'), defs.MoveAssign, 'std::vector<int*> p_arr = {&(n)};'),
		(_ast('CVarOps.local_decl.block', 'assign[1]'), defs.MoveAssign, 'std::map<int, int*> p_map = {{n, &(n)}};'),

		(_ast('CVarOps.addr_calc.block', 'assign[0]'), defs.MoveAssign, 'int a = sp0 - sp1;'),
		(_ast('CVarOps.addr_calc.block', 'assign[1]'), defs.MoveAssign, 'int b = sp0 + 1;'),

		(_ast('CVarOps.raw.block', 'return_stmt'), defs.Return, 'return p->raw();'),

		(_ast('CVarOps.prop_relay.block', 'assign'), defs.MoveAssign, 'CVarOps a = this->prop_relay().prop_relay();'),

		(_ast('FuncOps.print.block', 'funccall'), defs.FuncCall, 'printf("message. %d, %f, %s", 1, 1.0, "abc");'),
		(_ast('FuncOps.kw_params.block', 'assign'), defs.MoveAssign, 'std::string a = this->kw_params(1, 2);'),

		(_ast('EnumOps.Values', ''), defs.Enum, '/** Values */\npublic: enum class Values {\n\tA = 0,\n\tB = 1,\n};'),
		(_ast('EnumOps.assign.block', 'assign[0]'), defs.MoveAssign, 'EnumOps::Values a = EnumOps::Values::A;'),
		(_ast('EnumOps.assign.block', 'assign[1]'), defs.MoveAssign, 'std::map<EnumOps::Values, std::string> d = {\n\t{EnumOps::Values::A, "A"},\n\t{EnumOps::Values::B, "B"},\n};'),
		(_ast('EnumOps.assign.block', 'assign[2]'), defs.MoveAssign, 'std::string da = d[EnumOps::Values::A];'),
		(_ast('EnumOps.cast.block', 'assign[0]'), defs.MoveAssign, 'EnumOps::Values e = static_cast<EnumOps::Values>(0);'),
		(_ast('EnumOps.cast.block', 'assign[1]'), defs.MoveAssign, 'int n = static_cast<int>(EnumOps::Values::A);'),

		(_ast('AccessOps.__init__', ''), defs.Constructor, 'public:\n/** __init__ */\nAccessOps() : Sub(0), sub_s("") {\n}'),

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
		(_ast('AccessOps.arrow.block', 'funccall[6].arguments.argvalue'), defs.Argument, 'ap->base_prop()'),
		(_ast('AccessOps.arrow.block', 'funccall[7].arguments.argvalue'), defs.Argument, 'asp->base_n'),
		(_ast('AccessOps.arrow.block', 'funccall[8].arguments.argvalue'), defs.Argument, 'asp->sub_s'),
		(_ast('AccessOps.arrow.block', 'funccall[9].arguments.argvalue'), defs.Argument, 'asp->call()'),

		(_ast('AccessOps.double_colon.block', 'funccall[0]'), defs.FuncCall, 'Sub::call();'),
		(_ast('AccessOps.double_colon.block', 'funccall[1].arguments.argvalue'), defs.Argument, 'Sub::class_base_n'),
		(_ast('AccessOps.double_colon.block', 'funccall[2].arguments.argvalue'), defs.Argument, 'Sub::base_class_func()'),
		(_ast('AccessOps.double_colon.block', 'funccall[3].arguments.argvalue'), defs.Argument, 'AccessOps::class_base_n'),
		(_ast('AccessOps.double_colon.block', 'funccall[4].arguments.argvalue'), defs.Argument, 'EnumOps::Values::A'),
		(_ast('AccessOps.double_colon.block', 'anno_assign'), defs.AnnoAssign, 'std::map<EnumOps::Values, std::string> d = {\n\t{EnumOps::Values::A, "A"},\n\t{EnumOps::Values::B, "B"},\n};'),

		(_ast('AccessOps.indexer.block', 'funccall[0].arguments.argvalue'), defs.Argument, 'arr_p[0]'),
		(_ast('AccessOps.indexer.block', 'funccall[1].arguments.argvalue'), defs.Argument, 'arr_sp[0]'),
		(_ast('AccessOps.indexer.block', 'funccall[2].arguments.argvalue'), defs.Argument, 'arr_ar[0]'),

		(_ast('Alias.Inner', ''), defs.Class, '/** Inner2 */\nclass Inner2 {\n\tpublic: static int V2 = 0;\n\tpublic:\n\t/** func */\n\tvoid func() {\n\n\t}\n};'),
		(_ast('Alias.__init__', ''), defs.Constructor, 'public:\n/** __init__ */\nAlias2() : inner_b(Alias2::Inner2()) {\n}'),
		(_ast('Alias.in_param_return', ''), defs.Method, 'public:\n/** in_param_return */\nAlias2 in_param_return(Alias2 a) {\n\n}'),
		(_ast('Alias.in_param_return2', ''), defs.Method, 'public:\n/** in_param_return2 */\nAlias2::Inner2 in_param_return2(Alias2::Inner2 i) {\n\n}'),
		(_ast('Alias.in_local.block', 'assign[0]'), defs.MoveAssign, 'Alias2 a = Alias2();'),
		(_ast('Alias.in_local.block', 'assign[1]'), defs.MoveAssign, 'Alias2::Inner2 i = Alias2::Inner2();'),
		(_ast('Alias.in_class_method.block', 'funccall'), defs.FuncCall, 'Alias2::in_class_method();'),
		(_ast('Alias.in_class_method.block', 'assign[1]'), defs.MoveAssign, 'Alias2::Values a = Alias2::Values::A;'),
		(_ast('Alias.in_class_method.block', 'assign[2]'), defs.MoveAssign, 'std::map<Alias2::Values, Alias2::Values> d = {\n\t{Alias2::Values::A, Alias2::Values::B},\n\t{Alias2::Values::B, Alias2::Values::A},\n};'),
		(_ast('Alias.in_class_method.block', 'assign[3]'), defs.MoveAssign, 'std::map<int, std::vector<int>> d2 = {\n\t{static_cast<int>(Alias2::Values::A), {static_cast<int>(Alias2::Values::B)}},\n\t{static_cast<int>(Alias2::Values::B), {static_cast<int>(Alias2::Values::A)}},\n};'),
		(_ast('Alias.InnerB.super_call.block', 'funccall'), defs.FuncCall, 'Alias2::Inner2::func();'),

		(_ast('CompOps.list_comp.block', 'assign[1]'), defs.MoveAssign, BlockExpects.CompOps_list_comp_assign_values1),
		(_ast('CompOps.dict_comp.block', 'assign[1]'), defs.MoveAssign, BlockExpects.CompOps_dict_comp_assign_kvs0_1),
		(_ast('CompOps.dict_comp.block', 'assign[3]'), defs.MoveAssign, BlockExpects.CompOps_dict_comp_assign_kvsp_1),
		(_ast('CompOps.dict_comp.block', 'assign[5]'), defs.MoveAssign, BlockExpects.CompOps_dict_comp_assign_kvs2),

		(_ast('ForOps.range.block', 'for_stmt'), defs.For, 'for (auto i = 0; i < 10; i++) {\n\n}'),
		(_ast('ForOps.enumerate.block', 'for_stmt'), defs.For, BlockExpects.ForOps_enumerate_for_index_key),
		(_ast('ForOps.dict_items.block', 'for_stmt[1]'), defs.For, 'for (auto& [key, value] : kvs) {\n\n}'),
		(_ast('ForOps.dict_items.block', 'for_stmt[3]'), defs.For, 'for (auto& [key, value] : *(kvs_p)) {\n\n}'),

		(_ast('ListOps.len.block', 'assign[1]'), defs.MoveAssign, 'int size_values = values.size();'),
		(_ast('ListOps.pop.block', 'assign[1]'), defs.MoveAssign, BlockExpects.ListOps_pop_assign_value0),
		(_ast('ListOps.pop.block', 'assign[2]'), defs.MoveAssign, BlockExpects.ListOps_pop_assign_value1),
		(_ast('ListOps.contains.block', 'assign[1]'), defs.MoveAssign, 'bool b_in = (std::find(values.begin(), values.end(), 1) != values.end());'),
		(_ast('ListOps.contains.block', 'assign[2]'), defs.MoveAssign, 'bool b_not_in = (std::find(values.begin(), values.end(), 1) == values.end());'),
		(_ast('ListOps.fill.block', 'assign'), defs.MoveAssign, 'std::vector<int> n_x3 = std::vector<int>(3, n);'),
		(_ast('ListOps.slice.block', 'assign[0]'), defs.MoveAssign, BlockExpects.ListOps_slice_assign_ns0),
		(_ast('ListOps.slice.block', 'assign[1]'), defs.MoveAssign, BlockExpects.ListOps_slice_assign_ns1),
		(_ast('ListOps.slice.block', 'assign[2]'), defs.MoveAssign, BlockExpects.ListOps_slice_assign_ns2),
		(_ast('ListOps.delete.block', 'del_stmt'), defs.Delete, 'ns.erase(ns.begin() + 1);\nns.erase(ns.begin() + 2);'),

		(_ast('DictOps.len.block', 'assign[1]'), defs.MoveAssign, 'int size_kvs = kvs.size();'),
		(_ast('DictOps.pop.block', 'assign[1]'), defs.MoveAssign, BlockExpects.DictOps_pop_assign_value0),
		(_ast('DictOps.pop.block', 'assign[2]'), defs.MoveAssign, BlockExpects.DictOps_pop_assign_value1),
		(_ast('DictOps.keys.block', 'assign[1]'), defs.MoveAssign, BlockExpects.DictOps_keys_assign_keys),
		(_ast('DictOps.values.block', 'assign[1]'), defs.MoveAssign, BlockExpects.DictOps_values_assign_values),
		(_ast('DictOps.decl.block', 'assign'), defs.MoveAssign, 'std::map<int, std::vector<int>> d = {{1, {\n\t{1},\n\t{2},\n\t{3},\n}}};'),
		(_ast('DictOps.contains.block', 'assign[1]'), defs.MoveAssign, 'bool b_in = d.contains("a");'),
		(_ast('DictOps.contains.block', 'assign[2]'), defs.MoveAssign, 'bool b_not_in = (!d.contains("a"));'),
		(_ast('DictOps.delete.block', 'del_stmt'), defs.Delete, 'dsn.erase("a");\ndsn.erase("b");'),

		(_ast('CastOps.cast_binary.block', 'assign[0]'), defs.MoveAssign, 'int f_to_n = static_cast<int>(1.0);'),
		(_ast('CastOps.cast_binary.block', 'assign[1]'), defs.MoveAssign, 'float n_to_f = static_cast<float>(1);'),
		(_ast('CastOps.cast_binary.block', 'assign[2]'), defs.MoveAssign, 'bool n_to_b = static_cast<bool>(1);'),
		(_ast('CastOps.cast_binary.block', 'assign[3]'), defs.MoveAssign, 'int e_to_n = static_cast<int>(EnumOps::Values::A);'),

		(_ast('CastOps.cast_string.block', 'assign[0]'), defs.MoveAssign, 'std::string n_to_s = std::to_string(1);'),
		(_ast('CastOps.cast_string.block', 'assign[1]'), defs.MoveAssign, 'std::string f_to_s = std::to_string(1.0);'),
		(_ast('CastOps.cast_string.block', 'assign[2]'), defs.MoveAssign, 'int s_to_n = atoi(n_to_s);'),
		(_ast('CastOps.cast_string.block', 'assign[3]'), defs.MoveAssign, 'float s_to_f = atof(f_to_s);'),
		(_ast('CastOps.cast_string.block', 'assign[4]'), defs.MoveAssign, 'std::string s_to_s = std::string("");'),

		(_ast('CastOps.cast_class.block', 'assign[0]'), defs.MoveAssign, 'Base b = static_cast<Base>(sub);'),
		(_ast('CastOps.cast_class.block', 'assign[1]'), defs.MoveAssign, 'Base* bp = static_cast<Base*>(sub_p);'),
		(_ast('CastOps.cast_class.block', 'assign[3]'), defs.MoveAssign, 'std::map<std::string, Base*> dsbp = static_cast<std::map<std::string, Base*>>(dssp);'),

		(_ast('Nullable.params', ''), defs.Method, 'public:\n/** params */\nvoid params(Sub* p) {\n\n}'),
		(_ast('Nullable.returns', ''), defs.Method, 'public:\n/** returns */\nSub* returns() {\n\n}'),
		(_ast('Nullable.var_move.block', 'anno_assign'), defs.AnnoAssign, 'Sub* p = nullptr;'),
		(_ast('Nullable.var_move.block', 'assign[1]'), defs.MoveAssign, 'p = &(base);'),
		(_ast('Nullable.var_move.block', 'assign[2]'), defs.MoveAssign, 'p = nullptr;'),
		(_ast('Nullable.var_move.block', 'assign[3]'), defs.MoveAssign, 'p = (sp).get();'),
		(_ast('Nullable.var_move.block', 'if_stmt.if_clause.block.return_stmt'), defs.Return, 'return *(p);'),

		(_ast('Template.T2Class', ''), defs.Class, '/** T2Class */\ntemplate<typename T2>\nclass T2Class {\n\n};'),
		(_ast('Template.__init__', ''), defs.Constructor, 'public:\n/** __init__ */\nTemplate(T v) {\n\n}'),
		(_ast('Template.class_method_t', ''), defs.ClassMethod, 'public:\n/** class_method_t */\ntemplate<typename T2>\nstatic T2 class_method_t(T2 v2) {\n\n}'),
		(_ast('Template.class_method_t_and_class_t', ''), defs.ClassMethod, 'public:\n/** class_method_t_and_class_t */\ntemplate<typename T2>\nstatic T2 class_method_t_and_class_t(T v, T2 v2) {\n\n}'),
		(_ast('Template.method_t', ''), defs.Method, 'public:\n/** method_t */\ntemplate<typename T2>\nT2 method_t(T2 v2) {\n\n}'),
		(_ast('Template.method_t_and_class_t', ''), defs.Method, 'public:\n/** method_t_and_class_t */\ntemplate<typename T2>\nT2 method_t_and_class_t(T v, T2 v2) {\n\n}'),

		(_ast('GenericOps.temporal.block', 'assign'), defs.MoveAssign, 'T a = value;'),
		(_ast('GenericOps.new.block', 'assign'), defs.MoveAssign, 'GenericOps<int> a = GenericOps<int>();'),

		(_ast('Struct', ''), defs.Class, '/** Struct */\nstruct Struct {\n\tpublic: int a;\n\tpublic: std::string b;\n\tpublic:\n\t/** __init__ */\n\tStruct(int a, std::string b) : a(a), b(b) {\n\t}\n};'),

		(_ast('StringOps.methods.block', 'assign[0]'), defs.MoveAssign, 'bool a = s.starts_with("");'),
		(_ast('StringOps.methods.block', 'assign[1]'), defs.MoveAssign, 'bool b = s.ends_with("");'),
		(_ast('StringOps.slice.block', 'assign[0]'), defs.MoveAssign, 'std::string a = s.substr(1, s.size() - 1);'),
		(_ast('StringOps.slice.block', 'assign[1]'), defs.MoveAssign, 'std::string b = s.substr(0, 5 - 0);'),
		(_ast('StringOps.len.block', 'assign'), defs.MoveAssign, 'int a = s.size();'),
		(_ast('StringOps.format.block', 'assign[0]'), defs.MoveAssign, 'std::string a = std::format("{}, {}, {}", 1, 2, 3);'),
		(_ast('StringOps.format.block', 'assign[1]'), defs.MoveAssign, 'std::string b = std::format(s, 1, 2, 3);'),

		(_ast('AssignOps.assign.block', 'anno_assign'), defs.AnnoAssign, 'int a = 1;'),
		(_ast('AssignOps.assign.block', 'assign'), defs.MoveAssign, 'std::string b = "b";'),
		(_ast('AssignOps.assign.block', 'aug_assign'), defs.AugAssign, 'b += std::to_string(a);'),

		(_ast('template_func', ''), defs.Function, '/** template_func */\ntemplate<typename T>\nT template_func(T v) {\n\n}'),
	])
	def test_exec(self, full_path: str, expected_type: type[Node], expected: str) -> None:
		transpiler = self.fixture.get(Py2Cpp)
		node = self.fixture.shared_nodes_by(full_path).as_a(expected_type)
		actual = transpiler.transpile(node)
		self.assertEqual(actual, expected)
