import os
import sys
from unittest import TestCase

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.dsn.translation import alias_dsn
from rogw.tranp.i18n.i18n import I18n, TranslationMapping
from rogw.tranp.implements.cpp.providers.i18n import translation_mapping_cpp_example
from rogw.tranp.implements.cpp.providers.view import renderer_helper_provider_cpp
from rogw.tranp.implements.cpp.providers.semantics import plugin_provider_cpp
from rogw.tranp.implements.cpp.transpiler.py2cpp import Py2Cpp
from rogw.tranp.file.loader import IDataLoader
from rogw.tranp.lang.module import to_fullyname
from rogw.tranp.lang.profile import profiler
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.test.helper import data_provider
from rogw.tranp.transpiler.types import TranspilerOptions
from rogw.tranp.view.render import Renderer, RendererHelperProvider, RendererSetting
from tests.test.fixture import Fixture
from tests.unit.rogw.tranp.implements.cpp.transpiler.fixtures.test_py2cpp_expect import BlockExpects


profiler_on = '--' in sys.argv


def fixture_translation_mapping(datums: IDataLoader) -> TranslationMapping:
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture_translations = {
		alias_dsn(ModuleDSN.full_joined(fixture_module_path, 'Alias.inner')): 'inner_b',
		alias_dsn(ModuleDSN.full_joined(fixture_module_path, 'Alias.Inner.V')): 'V2',
	}
	return translation_mapping_cpp_example(datums).merge(fixture_translations)


def make_renderer_setting(i18n: I18n) -> RendererSetting:
	template_dirs = [os.path.join(tranp_dir(), 'data/cpp/template')]
	env = {'immutable_param_types': ['std::string', 'std::vector', 'std::map', 'std::function']}
	return RendererSetting(template_dirs, i18n.t, env)


class TestPy2Cpp(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__, {
		to_fullyname(Py2Cpp): Py2Cpp,
		to_fullyname(PluginProvider): plugin_provider_cpp,
		to_fullyname(Renderer): Renderer,
		to_fullyname(RendererHelperProvider): renderer_helper_provider_cpp,
		to_fullyname(RendererSetting): make_renderer_setting,
		to_fullyname(TranslationMapping): fixture_translation_mapping,
		to_fullyname(TranspilerOptions): lambda: TranspilerOptions(verbose=False, env={}),
	})

	@profiler(on=profiler_on)
	@data_provider([
		('', 'import_stmt[1]', defs.Import, '#include <functional>'),

		('', 'funccall[9]', defs.FuncCall, '#pragma once'),
		('', 'funccall[10]', defs.FuncCall, '#include <memory>'),
		('', 'funccall[11]', defs.FuncCall, 'MACRO()'),

		('T', '', defs.TemplateClass, '// template<typename T>'),
		('T2', '', defs.TemplateClass, '// template<typename T2>'),

		('DSI', '', defs.AltClass, 'using DSI = std::map<std::string, int>;'),
		('TSII', '', defs.AltClass, 'using TSII = std::tuple<std::string, int, int>;'),

		('Values', '', defs.Enum, '/** Values */\nenum class Values {\n\tA = 0,\n\tB = 1,\n};'),

		('DeclOps', '', defs.Class, BlockExpects.DeclOps),

		('Base.sub_implements', '', defs.Method, 'public:\n/** sub_implements */\nvirtual void sub_implements() = 0;'),
		('Base.allowed_overrides', '', defs.Method, 'public:\n/** allowed_overrides */\nvirtual int allowed_overrides() {\n\treturn 1;\n}'),
		('Base.base_class_func', '', defs.ClassMethod, BlockExpects.class_method(access='public', name='base_class_func', return_type='int')),
		('Base.base_prop', '', defs.Method, BlockExpects.method(access='public', name='base_prop', return_type='std::string', prop=True)),

		('Sub', 'class_def_raw.block.comment_stmt[5]', defs.Comment, '// FIXME other: Any'),

		('CVarOps.ret_raw', 'function_def_raw.block.return_stmt', defs.Return, 'return Sub(0);'),
		('CVarOps.ret_cp', 'function_def_raw.block.return_stmt', defs.Return, 'return new Sub(0);'),
		('CVarOps.ret_csp', 'function_def_raw.block.return_stmt', defs.Return, 'return std::make_shared<Sub>(0);'),

		('CVarOps.local_move', 'function_def_raw.block.anno_assign[0]', defs.AnnoAssign, 'Sub a{0};'),
		('CVarOps.local_move', 'function_def_raw.block.anno_assign[1]', defs.AnnoAssign, 'Sub* ap = (&(a));'),
		('CVarOps.local_move', 'function_def_raw.block.anno_assign[2]', defs.AnnoAssign, 'std::shared_ptr<Sub> asp = std::make_shared<Sub>(0);'),
		('CVarOps.local_move', 'function_def_raw.block.anno_assign[3]', defs.AnnoAssign, 'Sub& ar = a;'),
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[4].if_clause.block.assign[0]', defs.MoveAssign, 'a = a;'),
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[4].if_clause.block.assign[1]', defs.MoveAssign, 'a = (*(ap));'),
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[4].if_clause.block.assign[2]', defs.MoveAssign, 'a = (*(asp));'),
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[4].if_clause.block.assign[3]', defs.MoveAssign, 'a = ar;'),
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[5].if_clause.block.assign[0]', defs.MoveAssign, 'ap = (&(a));'),
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[5].if_clause.block.assign[1]', defs.MoveAssign, 'ap = ap;'),
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[5].if_clause.block.assign[2]', defs.MoveAssign, 'ap = (asp).get();'),
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[5].if_clause.block.assign[3]', defs.MoveAssign, 'ap = (&(ar));'),
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[6].if_clause.block.assign', defs.MoveAssign, 'asp = asp;'),
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[7].if_clause.block.assign[1]', defs.MoveAssign, 'ar = a;'),  # XXX C++ではNGだが要件等 ※型推論のコストをかけてまでエラー判定が必要なのか微妙
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[7].if_clause.block.assign[3]', defs.MoveAssign, 'ar = (*(ap));'),  # 〃
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[7].if_clause.block.assign[5]', defs.MoveAssign, 'ar = (*(asp));'),  # 〃
		('CVarOps.local_move', 'function_def_raw.block.if_stmt[7].if_clause.block.assign[7]', defs.MoveAssign, 'ar = ar;'),  # 〃

		('CVarOps.param_move', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'Sub a1 = a;'),
		('CVarOps.param_move', 'function_def_raw.block.anno_assign[1]', defs.AnnoAssign, 'Sub a2 = (*(ap));'),
		('CVarOps.param_move', 'function_def_raw.block.anno_assign[2]', defs.AnnoAssign, 'Sub a3 = (*(asp));'),
		('CVarOps.param_move', 'function_def_raw.block.anno_assign[3]', defs.AnnoAssign, 'Sub a4 = ar;'),
		('CVarOps.param_move', 'function_def_raw.block.assign[4]', defs.MoveAssign, 'a = a1;'),
		('CVarOps.param_move', 'function_def_raw.block.assign[5]', defs.MoveAssign, 'ap = (&(a2));'),
		('CVarOps.param_move', 'function_def_raw.block.assign[8]', defs.MoveAssign, 'ar = a4;'),  # XXX C++ではNGだが要件等 ※型推論のコストをかけてまでエラー判定が必要なのか微妙

		('CVarOps.invoke_method', 'function_def_raw.block.funccall', defs.FuncCall, 'this->invoke_method((*(asp)), (asp).get(), asp);'),

		('CVarOps.unary_calc', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'Sub neg_a = -a;'),
		('CVarOps.unary_calc', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'Sub neg_a2 = -(*(ap));'),
		('CVarOps.unary_calc', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'Sub neg_a3 = -(*(asp));'),
		('CVarOps.unary_calc', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'Sub neg_a4 = -ar;'),

		('CVarOps.binary_calc', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'Sub add = a + (*(ap)) + (*(asp)) + ar;'),
		('CVarOps.binary_calc', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'Sub sub = a - (*(ap)) - (*(asp)) - ar;'),
		('CVarOps.binary_calc', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'Sub mul = a * (*(ap)) * (*(asp)) * ar;'),
		('CVarOps.binary_calc', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'Sub div = a / (*(ap)) / (*(asp)) / ar;'),
		('CVarOps.binary_calc', 'function_def_raw.block.assign[4]', defs.MoveAssign, 'float mod = fmod(1.0, 1);'),
		('CVarOps.binary_calc', 'function_def_raw.block.assign[5]', defs.MoveAssign, 'Sub calc = a + (*(ap)) * (*(asp)) - ar / a;'),
		('CVarOps.binary_calc', 'function_def_raw.block.assign[6]', defs.MoveAssign, 'bool is_a = a == (*(ap)) == (*(asp)) == ar;'),
		('CVarOps.binary_calc', 'function_def_raw.block.assign[7]', defs.MoveAssign, 'bool is_not_a = a != (*(ap)) != (*(asp)) != ar;'),
		('CVarOps.binary_calc', 'function_def_raw.block.assign[8]', defs.MoveAssign, 'bool is_null = apn == nullptr && apn != nullptr;'),

		('CVarOps.tenary_calc', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'Sub a2 = true ? a : Sub();'),
		('CVarOps.tenary_calc', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'Sub a3 = true ? a : a;'),
		('CVarOps.tenary_calc', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'Sub* ap2 = true ? ap : ap;'),
		('CVarOps.tenary_calc', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'std::shared_ptr<Sub> asp2 = true ? asp : asp;'),
		('CVarOps.tenary_calc', 'function_def_raw.block.assign[4]', defs.MoveAssign, 'Sub& ar2 = true ? ar : ar;'),
		('CVarOps.tenary_calc', 'function_def_raw.block.assign[5]', defs.MoveAssign, 'Sub* ap_or_null = true ? ap : nullptr;'),

		('CVarOps.declare', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'std::vector<int>* arr_p = (&(arr));'),
		('CVarOps.declare', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'std::vector<int>* arr_p2 = new std::vector<int>();'),
		('CVarOps.declare', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp{new std::vector<int>({1})};'),
		('CVarOps.declare', 'function_def_raw.block.assign[4]', defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp2{new std::vector<int>()};'),
		('CVarOps.declare', 'function_def_raw.block.assign[5]', defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp3{new std::vector<int>(2)};'),
		('CVarOps.declare', 'function_def_raw.block.assign[6]', defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp4{new std::vector<int>(2, 0)};'),
		('CVarOps.declare', 'function_def_raw.block.assign[7]', defs.MoveAssign, 'std::vector<int>& arr_r = arr;'),
		('CVarOps.declare', 'function_def_raw.block.assign[8]', defs.MoveAssign, 'std::shared_ptr<int> n_sp_empty{};'),
		('CVarOps.declare', 'function_def_raw.block.assign[9]', defs.MoveAssign, 'CVarOps* this_p = this;'),
		('CVarOps.declare', 'function_def_raw.block.assign[10]', defs.MoveAssign, 'std::vector<CVarOps*> this_ps = {this};'),
		('CVarOps.declare', 'function_def_raw.block.assign[11]', defs.MoveAssign, 'std::vector<CVarOps*>& this_ps_ref = this_ps;'),

		('CVarOps.default_param', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'int n = ap ? ap->base_n : 0;'),
		('CVarOps.default_param', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'int n2 = this->default_param();'),

		('CVarOps.const_move', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'const Sub a_const0 = a;'),
		('CVarOps.const_move', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'Sub a0 = a_const0;'),
		('CVarOps.const_move', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'const Sub& r0_const = a_const0;'),
		('CVarOps.const_move', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'const Sub* ap0_const = (&(a_const0));'),

		('CVarOps.const_move', 'function_def_raw.block.assign[4]', defs.MoveAssign, 'const Sub* ap_const1 = ap;'),
		('CVarOps.const_move', 'function_def_raw.block.assign[5]', defs.MoveAssign, 'Sub a1 = (*(ap_const1));'),
		('CVarOps.const_move', 'function_def_raw.block.assign[6]', defs.MoveAssign, 'const Sub& r_const1 = (*(ap_const1));'),

		('CVarOps.const_move', 'function_def_raw.block.assign[7]', defs.MoveAssign, 'const std::shared_ptr<Sub> asp_const2 = asp;'),
		('CVarOps.const_move', 'function_def_raw.block.assign[8]', defs.MoveAssign, 'Sub a2 = (*(asp_const2));'),  # XXX 本来の期待値は`std::shared_ptr<Sub>`の様な気がするが、CVarsはただのプロクシーとして実装しているため、操作結果はCSPとほぼ同等になる
		('CVarOps.const_move', 'function_def_raw.block.assign[9]', defs.MoveAssign, 'const Sub& r_const2 = (*(asp_const2));'),  # 〃
		('CVarOps.const_move', 'function_def_raw.block.assign[10]', defs.MoveAssign, 'const Sub* ap_const2 = (asp_const2).get();'),  # 〃

		('CVarOps.const_move', 'function_def_raw.block.assign[11]', defs.MoveAssign, 'const Sub& r_const3 = r;'),
		('CVarOps.const_move', 'function_def_raw.block.assign[12]', defs.MoveAssign, 'Sub a3 = r_const3;'),
		('CVarOps.const_move', 'function_def_raw.block.assign[13]', defs.MoveAssign, 'const Sub* ap_const3 = (&(r_const3));'),

		('CVarOps.to_void', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'void* a_to_vp = static_cast<void*>((&(a)));'),
		('CVarOps.to_void', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'void* ap_to_vp = static_cast<void*>(ap);'),
		('CVarOps.to_void', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'void* asp_to_vp = static_cast<void*>((asp).get());'),
		('CVarOps.to_void', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'void* r_to_vp = static_cast<void*>((&(r)));'),

		('CVarOps.local_decl', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'std::vector<int*> p_arr = {(&(n))};'),
		('CVarOps.local_decl', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'std::map<int, int*> p_map = {{n, (&(n))}};'),

		('CVarOps.addr_calc', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'int a = sp0 - sp1;'),
		('CVarOps.addr_calc', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'int b = sp0 + 1;'),

		('CVarOps.raw', 'function_def_raw.block.return_stmt', defs.Return, 'return p->raw();'),

		('CVarOps.prop_relay', 'function_def_raw.block.assign', defs.MoveAssign, 'CVarOps a = this->prop_relay().prop_relay();'),

		('CVarOps.hex', 'function_def_raw.block.funccall[0]', defs.FuncCall, 'std::format("%p", (p));'),
		('CVarOps.hex', 'function_def_raw.block.funccall[1]', defs.FuncCall, 'std::format("%p", ((&(n))));'),

		('CVarOps.alias_call', 'function_def_raw.block.funccall[0]', defs.FuncCall, 'ap->call();'),
		('CVarOps.alias_call', 'function_def_raw.block.funccall[1]', defs.FuncCall, 'asp->call();'),
		('CVarOps.alias_call', 'function_def_raw.block.funccall[2]', defs.FuncCall, 'aref.call();'),

		('FuncOps.kw_params', 'function_def_raw.block.assign', defs.MoveAssign, 'std::string a = this->kw_params(1, 2);'),

		('AccessOps.__init__', '', defs.Constructor, 'public:\n/** __init__ */\nAccessOps() : Sub(0), sub_s("") {}'),

		('AccessOps.dot', 'function_def_raw.block.funccall[0].arguments.argvalue', defs.Argument, 'a.base_n'),
		('AccessOps.dot', 'function_def_raw.block.funccall[1].arguments.argvalue', defs.Argument, 'a.sub_s'),
		('AccessOps.dot', 'function_def_raw.block.funccall[2].arguments.argvalue', defs.Argument, 'a.sub_s.split'),
		('AccessOps.dot', 'function_def_raw.block.funccall[3].arguments.argvalue', defs.Argument, 'a.call()'),
		('AccessOps.dot', 'function_def_raw.block.funccall[5].arguments.argvalue', defs.Argument, 'dda[1][1].sub_s'),

		('AccessOps.arrow', 'function_def_raw.block.funccall[0].arguments.argvalue', defs.Argument, 'this->base_n'),
		('AccessOps.arrow', 'function_def_raw.block.funccall[1].arguments.argvalue', defs.Argument, 'this->sub_s'),
		('AccessOps.arrow', 'function_def_raw.block.funccall[2].arguments.argvalue', defs.Argument, 'this->call()'),
		('AccessOps.arrow', 'function_def_raw.block.funccall[3].arguments.argvalue', defs.Argument, 'ap->base_n'),
		('AccessOps.arrow', 'function_def_raw.block.funccall[4].arguments.argvalue', defs.Argument, 'ap->sub_s'),
		('AccessOps.arrow', 'function_def_raw.block.funccall[5].arguments.argvalue', defs.Argument, 'ap->call()'),
		('AccessOps.arrow', 'function_def_raw.block.funccall[6].arguments.argvalue', defs.Argument, 'ap->base_prop()'),
		('AccessOps.arrow', 'function_def_raw.block.funccall[7].arguments.argvalue', defs.Argument, 'asp->base_n'),
		('AccessOps.arrow', 'function_def_raw.block.funccall[8].arguments.argvalue', defs.Argument, 'asp->sub_s'),
		('AccessOps.arrow', 'function_def_raw.block.funccall[9].arguments.argvalue', defs.Argument, 'asp->call()'),

		('AccessOps.double_colon', 'function_def_raw.block.funccall[0]', defs.FuncCall, 'Sub::call();'),
		('AccessOps.double_colon', 'function_def_raw.block.funccall[1].arguments.argvalue', defs.Argument, 'Sub::class_base_n'),
		('AccessOps.double_colon', 'function_def_raw.block.funccall[2].arguments.argvalue', defs.Argument, 'Sub::base_class_func()'),
		('AccessOps.double_colon', 'function_def_raw.block.funccall[3].arguments.argvalue', defs.Argument, 'AccessOps::class_base_n'),
		('AccessOps.double_colon', 'function_def_raw.block.funccall[4].arguments.argvalue', defs.Argument, 'Values::A'),
		('AccessOps.double_colon', 'function_def_raw.block.anno_assign', defs.AnnoAssign, 'std::map<Values, std::string> d = {\n\t{Values::A, "A"},\n\t{Values::B, "B"},\n};'),

		('AccessOps.indexer', 'function_def_raw.block.funccall[0].arguments.argvalue', defs.Argument, '(*(arr_p))[0]'),
		('AccessOps.indexer', 'function_def_raw.block.funccall[1].arguments.argvalue', defs.Argument, '(*(arr_sp))[0]'),
		('AccessOps.indexer', 'function_def_raw.block.funccall[2].arguments.argvalue', defs.Argument, 'arr_ar[0]'),

		('Alias.Inner', '', defs.Class, 'public:\n/** Inner2 */\nclass Inner2 {\n\tpublic: inline static int V2 = 0;\n\tpublic:\n\t/** func */\n\tvoid func() {}\n};'),
		('Alias.__init__', '', defs.Constructor, 'public:\n/** __init__ */\nAlias2() : inner_b({}) {}'),
		('Alias.in_param_return', '', defs.Method, BlockExpects.method(access='public', name='in_param_return', return_type='Alias2', params=['Alias2 a'])),
		('Alias.in_param_return2', '', defs.Method, BlockExpects.method(access='public', name='in_param_return2', return_type='Alias2::Inner2', params=['Alias2::Inner2 i'])),
		('Alias.in_local', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'Alias2 a{};'),
		('Alias.in_local', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'Alias2::Inner2 i{};'),
		('Alias.in_class_method', 'function_def_raw.block.funccall', defs.FuncCall, 'Alias2::in_class_method();'),
		('Alias.in_class_method', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'Alias2::Values a = Alias2::Values::A;'),
		('Alias.in_class_method', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'std::map<Alias2::Values, Alias2::Values> d = {\n\t{Alias2::Values::A, Alias2::Values::B},\n\t{Alias2::Values::B, Alias2::Values::A},\n};'),
		('Alias.in_class_method', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'std::map<int, std::vector<int>> d2 = {\n\t{static_cast<int>(Alias2::Values::A), {static_cast<int>(Alias2::Values::B)}},\n\t{static_cast<int>(Alias2::Values::B), {static_cast<int>(Alias2::Values::A)}},\n};'),
		('Alias.InnerB.super_call', 'function_def_raw.block.funccall', defs.FuncCall, 'Alias2::Inner2::func();'),

		('Nullable.params', '', defs.Method, BlockExpects.method(access='public', name='params', params=['Sub* p'])),
		('Nullable.returns', '', defs.Method, BlockExpects.method(access='public', name='returns', return_type='Sub*')),
		('Nullable.var_move', 'function_def_raw.block.anno_assign', defs.AnnoAssign, 'Sub* p = nullptr;'),
		('Nullable.var_move', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'p = (&(base));'),
		('Nullable.var_move', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'p = nullptr;'),
		('Nullable.var_move', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'p = (sp).get();'),
		('Nullable.var_move', 'function_def_raw.block.if_stmt.if_clause.block.return_stmt', defs.Return, 'return (*(p));'),

		('GenericOps.temporal', 'function_def_raw.block.assign', defs.MoveAssign, 'T a = value;'),
		('GenericOps.new', 'function_def_raw.block.assign', defs.MoveAssign, 'GenericOps<int> a{};'),

		('Struct', '', defs.Class, '/** Struct */\nstruct Struct {\n\tpublic: int a;\n\tpublic: std::string b;\n\tpublic:\n\t/** __init__ */\n\tStruct(int a, const std::string& b) : a(a), b(b) {}\n};'),

		('ForCompound.Proto', '', defs.Class, '// class Proto'),
		('ForCompound.DeclProps', '', defs.Class, BlockExpects.DeclProps),
		('ForCompound.AltClass.assign', 'function_def_raw.block.anno_assign', defs.AnnoAssign, 'CSP2<Sub> sp = std::make_shared<Sub>(0);'),
		('ForCompound.ClassMethod.make', '', defs.ClassMethod, BlockExpects.class_method(access='public', name='make', return_type='ClassMethod', statements=['ForCompound::ClassMethod inst = ClassMethod();', 'return inst;'])),
		('ForCompound.ClassMethod.immutable_returns', '', defs.ClassMethod, BlockExpects.class_method(access='public', name='immutable_returns', return_type='const std::string&')),
		('ForCompound.Method.immutable_returns', '', defs.Method, BlockExpects.method(access='public', name='immutable_returns', return_type='const std::string*')),

		('ForCompound.DeclEnum.literalize', 'function_def_raw.block.funccall[0]', defs.FuncCall, 'printf("AS");'),
		('ForCompound.DeclEnum.literalize', 'function_def_raw.block.funccall[1]', defs.FuncCall, 'printf("BS");'),
		('ForCompound.DeclEnum.literalize', 'function_def_raw.block.funccall[2]', defs.FuncCall, 'printf("a");'),
		('ForCompound.DeclEnum.literalize', 'function_def_raw.block.funccall[3]', defs.FuncCall, 'printf("b");'),
		('ForCompound.DeclEnum.literalize', 'function_def_raw.block.funccall[4]', defs.FuncCall, 'printf("AN");'),
		('ForCompound.DeclEnum.literalize', 'function_def_raw.block.funccall[5]', defs.FuncCall, 'printf("BN");'),

		('ForCompound.Operators.__eq__', '', defs.Method, BlockExpects.method(access='public', name='operator==', params=['const ForCompound::Operators& other'], return_type='bool')),
		('ForCompound.Operators.__ne__', '', defs.Method, BlockExpects.method(access='public', name='operator!=', params=['const ForCompound::Operators& other'], return_type='bool')),
		('ForCompound.Operators.__lt__', '', defs.Method, BlockExpects.method(access='public', name='operator<', params=['const ForCompound::Operators& other'], return_type='bool')),
		('ForCompound.Operators.__gt__', '', defs.Method, BlockExpects.method(access='public', name='operator>', params=['const ForCompound::Operators& other'], return_type='bool')),
		('ForCompound.Operators.__le__', '', defs.Method, BlockExpects.method(access='public', name='operator<=', params=['const ForCompound::Operators& other'], return_type='bool')),
		('ForCompound.Operators.__ge__', '', defs.Method, BlockExpects.method(access='public', name='operator>=', params=['const ForCompound::Operators& other'], return_type='bool')),
		('ForCompound.Operators.__add__', '', defs.Method, BlockExpects.method(access='public', name='operator+', params=['const int& value'], return_type='int')),
		('ForCompound.Operators.__sub__', '', defs.Method, BlockExpects.method(access='public', name='operator-', params=['const int& value'], return_type='int')),
		('ForCompound.Operators.__mul__', '', defs.Method, BlockExpects.method(access='public', name='operator*', params=['const int& value'], return_type='int')),
		('ForCompound.Operators.__mod__', '', defs.Method, BlockExpects.method(access='public', name='operator%', params=['const int& value'], return_type='int')),
		('ForCompound.Operators.__truediv__', '', defs.Method, BlockExpects.method(access='public', name='operator/', params=['const int& value'], return_type='int')),
		('ForCompound.Operators.__and__', '', defs.Method, BlockExpects.method(access='public', name='operator&', params=['const int& value'], return_type='int')),
		('ForCompound.Operators.__or__', '', defs.Method, BlockExpects.method(access='public', name='operator|', params=['const int& value'], return_type='int')),
		('ForCompound.Operators.__getitem__', '', defs.Method, BlockExpects.method(access='public', name='operator[]', params=['const std::string& key'], return_type='Sub&')),
		('ForCompound.Operators.__setitem__', '', defs.Method, '// method __setitem__'),

		('ForCompound.Modifier._to_public', '', defs.Method, BlockExpects.method(access='public', name='_to_public')),
		('ForCompound.Modifier.to_protected', '', defs.Method, BlockExpects.method(access='protected', name='to_protected')),
		('ForCompound.Modifier.to_private', '', defs.Method, BlockExpects.method(access='private', name='to_private')),
		('ForCompound.Modifier.pure', '', defs.Method, BlockExpects.method(access='public', name='pure', pure=True)),
		('ForCompound.Modifier.mod_mutable', '', defs.Method, BlockExpects.method(access='public', name='mod_mutable', params=['std::string s_m', 'const std::string& s_i', 'const std::vector<int>& ns_i', 'const std::map<std::string, int>& dsn_i', 'const std::function<void()>& func_i'])),

		('ForCompound.closure.bind_ref', '', defs.Closure, 'auto bind_ref = [&]() -> void {};'),
		('ForCompound.closure.bind_copy', '', defs.Closure, 'auto bind_copy = [this]() mutable -> void {};'),

		('ForClassExpose.Class', '', defs.Class, '// class Class'),
		('ForClassExpose.Enums', '', defs.Enum, '// enum Enums'),
		('ForClassExpose.method', '', defs.Method, '// method method'),
		('ForClassExpose.method_cpp', '', defs.Method, BlockExpects.method(access='public', name='method')),
		('func_expose', '', defs.Function, '// function func_expose'),

		('ForTemplate.TClass.__init__', '', defs.Constructor, 'public:\n/** __init__ */\nTClass(T v) {}'),
		('ForTemplate.TClass.class_method_t', '', defs.ClassMethod, BlockExpects.class_method(access='public', name='class_method_t', return_type='T2', params=['T2 v2'], template='T2')),
		('ForTemplate.TClass.class_method_t_and_class_t', '', defs.ClassMethod, BlockExpects.class_method(access='public', name='class_method_t_and_class_t', return_type='T2', params=['T v', 'T2 v2'], template='T2')),
		('ForTemplate.TClass.method_t', '', defs.Method, BlockExpects.method(access='public', name='method_t', return_type='T2', params=['T2 v2'], template='T2')),
		('ForTemplate.TClass.method_t_and_class_t', '', defs.Method, BlockExpects.method(access='public', name='method_t_and_class_t', return_type='T2', params=['T v', 'T2 v2'], template='T2')),
		('ForTemplate.T2Class', '', defs.Class, 'public:\n/** T2Class */\ntemplate<typename T2>\nclass T2Class {\n\n};'),

		('ForTemplate.unpack_call', 'function_def_raw.block.assign', defs.MoveAssign, 'ForTemplate a = this->unpack(ForTemplate());'),

		('template_unpack', '', defs.Function, '/** template_unpack */\ntemplate<typename T>\nT template_unpack(T v) {}'),
		('template_unpack_call', 'function_def_raw.block.assign', defs.MoveAssign, 'ForTemplate a = template_unpack(ForTemplate());'),

		('ForFlows.if_elif_else', 'function_def_raw.block.if_stmt', defs.If, 'if (1) {\n\n} else if (2) {\n\n} else {\n\n}'),

		('ForFlows.while_only', 'function_def_raw.block.while_stmt', defs.While, 'while (true) {\n\n}'),

		('ForFlows.for_range', 'function_def_raw.block.for_stmt[0]', defs.For, 'for (auto i = 0; i < 2; i++) {\n\n}'),
		('ForFlows.for_range', 'function_def_raw.block.for_stmt[1]', defs.For, 'for (auto i = 0; i < strs.size(); i++) {\n\n}'),

		('ForFlows.for_enumerate', 'function_def_raw.block.for_stmt[0]', defs.For, BlockExpects.for_enumerate(index='index', value='value', iterates='{1}', statements=[])),
		('ForFlows.for_enumerate', 'function_def_raw.block.for_stmt[1]', defs.For, BlockExpects.for_enumerate(index='index', value='value', iterates='strs', statements=[])),

		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[0]', defs.For, 'for (auto& [key, _] : {{"a", 1}}) {\n\n}'),
		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[1]', defs.For, 'for (auto& [_, value] : {{"a", 1}}) {\n\n}'),
		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[2]', defs.For, 'for (auto& [key, value] : {{"a", 1}}) {\n\n}'),
		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[3]', defs.For, 'for (auto& [key, _] : dsn) {\n\n}'),
		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[4]', defs.For, 'for (auto& [_, value] : dsn) {\n\n}'),
		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[5]', defs.For, 'for (auto& [key, value] : dsn) {\n\n}'),
		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[6]', defs.For, 'for (auto& [key, _] : *(psn)) {\n\n}'),
		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[7]', defs.For, 'for (auto& [_, value] : *(psn)) {\n\n}'),
		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[8]', defs.For, 'for (auto& [key, value] : *(psn)) {\n\n}'),
		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[9]', defs.For, 'for (auto& [kp, _] : dpp) {\n\n}'),
		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[10]', defs.For, 'for (auto& [_, vp] : dpp) {\n\n}'),
		('ForFlows.for_dict', 'function_def_raw.block.for_stmt[11]', defs.For, 'for (auto& [kp, vp] : dpp) {\n\n}'),

		('ForFlows.for_each', 'function_def_raw.block.for_stmt[0]', defs.For, 'for (auto& n : {1}) {\n\n}'),
		('ForFlows.for_each', 'function_def_raw.block.for_stmt[1]', defs.For, 'for (auto& s : strs) {\n\n}'),
		('ForFlows.for_each', 'function_def_raw.block.for_stmt[2]', defs.For, 'for (auto& [e1, e2, e3] : ts) {\n\n}'),
		('ForFlows.for_each', 'function_def_raw.block.for_stmt[3]', defs.For, 'for (const auto cp : cps) {\n\n}'),

		('ForFlows.try_catch_throw', 'function_def_raw.block.try_stmt', defs.Try, 'try {\n\n} catch (std::runtime_error e) {\n\tthrow new std::exception();\n} catch (std::exception e) {\n\tthrow e;\n}'),

		('ForAssign.anno', 'function_def_raw.block.anno_assign[0]', defs.AnnoAssign, 'int n = 1;'),
		('ForAssign.anno', 'function_def_raw.block.anno_assign[1]', defs.AnnoAssign, 'std::vector<int> ns = {};'),
		('ForAssign.anno', 'function_def_raw.block.anno_assign[2]', defs.AnnoAssign, 'std::map<std::string, int> dsn = {};'),
		('ForAssign.anno', 'function_def_raw.block.anno_assign[3]', defs.AnnoAssign, 'std::tuple<bool, int, std::string> ts = {true, 1, "a"};'),
		('ForAssign.anno', 'function_def_raw.block.anno_assign[4]', defs.AnnoAssign, 'static std::map<std::string, int> static_dsn = {{"a", 1}};'),

		('ForAssign.move', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'std::string s = "a";'),
		('ForAssign.move', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'std::vector<std::string> ss = {"a"};'),
		('ForAssign.move', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'std::map<std::string, std::vector<int>> dsns = {{"a", {1}}};'),
		('ForAssign.move', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'std::tuple<bool, int, std::string> ts = {true, 1, "b"};'),

		('ForAssign.aug', 'function_def_raw.block.aug_assign[0]', defs.AugAssign, 'n += 1;'),
		('ForAssign.aug', 'function_def_raw.block.aug_assign[1]', defs.AugAssign, 's += std::to_string(n);'),

		('ForAssign.move_unpack', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'auto [tb, tn, tf] = bnf;'),
		('ForAssign.move_unpack', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'auto [ts0, ti1, ti2] = tsiis[0];'),
		('ForAssign.move_unpack', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'std::string s0 = std::get<0>(tsiis[0]);'),
		('ForAssign.move_unpack', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'int i1 = std::get<1>(tsiis[0]);'),
		('ForAssign.move_unpack', 'function_def_raw.block.assign[4]', defs.MoveAssign, 'int i2 = std::get<2>(tsiis[0]);'),

		('ForAssign.for_enum', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'Values ea = Values::A;'),
		('ForAssign.for_enum', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'std::vector<Values> es = {Values::A};'),
		('ForAssign.for_enum', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'std::map<Values, std::string> des = {\n\t{Values::A, "A"},\n\t{Values::B, "B"},\n};'),
		('ForAssign.for_enum', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'Values e = es[0];'),
		('ForAssign.for_enum', 'function_def_raw.block.assign[4]', defs.MoveAssign, 'std::string s = des[Values::A];'),

		('ForSimple.delete_list_dict', 'function_def_raw.block.del_stmt[0]', defs.Delete, 'ns.erase(ns.begin() + 0);'),
		('ForSimple.delete_list_dict', 'function_def_raw.block.del_stmt[1]', defs.Delete, 'ns.erase(ns.begin() + 1);\nns.erase(ns.begin() + 2);'),
		('ForSimple.delete_list_dict', 'function_def_raw.block.del_stmt[2]', defs.Delete, 'dsn.erase("a");'),
		('ForSimple.delete_list_dict', 'function_def_raw.block.del_stmt[3]', defs.Delete, 'dsn.erase("b");\ndsn.erase("c");'),

		('ForSimple.return_none', 'function_def_raw.block.return_stmt', defs.Return, 'return;'),
		('ForSimple.return_value', 'function_def_raw.block.return_stmt', defs.Return, 'return 0;'),

		('ForSimple.asserts', 'function_def_raw.block.assert_stmt[0]', defs.Assert, 'assert(true);'),
		('ForSimple.asserts', 'function_def_raw.block.assert_stmt[1]', defs.Assert, 'assert(1 == 0); // std::exception'),

		('ForSimple.pass_only', 'function_def_raw.block.pass_stmt', defs.Pass, ''),

		('ForSimple.break_continue', 'function_def_raw.block.for_stmt.block.if_stmt[0]', defs.If, 'if (i == 0) {\n\tcontinue;\n}'),
		('ForSimple.break_continue', 'function_def_raw.block.for_stmt.block.if_stmt[1]', defs.If, 'if (i != 0) {\n\tbreak;\n}'),
		('ForSimple.break_continue', 'function_def_raw.block.while_stmt.block.if_stmt[0]', defs.If, 'if (1 == 0) {\n\tcontinue;\n}'),
		('ForSimple.break_continue', 'function_def_raw.block.while_stmt.block.if_stmt[1]', defs.If, 'if (1 != 0) {\n\tbreak;\n}'),

		('ForSimple.comment', 'function_def_raw.block.comment_stmt', defs.Comment, '// abc'),

		('ForIndexer.list_slice', 'function_def_raw.block.getitem[0]', defs.Indexer, BlockExpects.list_slice(symbol='ns', begin='1', end='', step='', var_type='int')),
		('ForIndexer.list_slice', 'function_def_raw.block.getitem[1]', defs.Indexer, BlockExpects.list_slice(symbol='ns', begin='', end='5', step='', var_type='int')),
		('ForIndexer.list_slice', 'function_def_raw.block.getitem[2]', defs.Indexer, BlockExpects.list_slice(symbol='ns', begin='3', end='9', step='2', var_type='int')),

		('ForIndexer.string_slice', 'function_def_raw.block.getitem[0]', defs.Indexer, 's.substr(1, s.size() - (1));'),
		('ForIndexer.string_slice', 'function_def_raw.block.getitem[1]', defs.Indexer, 's.substr(0, 5);'),

		('ForFuncCall.CallableType', '', defs.Class, 'public:\n/** CallableType */\nclass CallableType {\n\tpublic: std::function<bool(int, std::string)> func;\n\tpublic:\n\t/** __init__ */\n\tCallableType(const std::function<bool(int, std::string)>& func) : func(func) {}\n};'),
		('ForFuncCall.move_assign', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'std::function<bool(int, const std::string&)> func = caller.func;'),
		('ForFuncCall.move_assign', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'bool b0 = caller.func(0, "");'),
		('ForFuncCall.move_assign', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'bool b1 = func(0, "");'),

		('ForFuncCall.Func.print', 'function_def_raw.block.funccall', defs.FuncCall, 'printf("message. %d, %f, %s", 1, 1.0, "abc");'),

		('ForFuncCall.Func.c_func', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'static std::map<std::string, int(ForFuncCall::Func::*)(const std::string&)> ds = {{"f", &ForFuncCall::Func::func_self}};'),
		('ForFuncCall.Func.c_func', 'function_def_raw.block.anno_assign[1]', defs.AnnoAssign, 'int n = (this->*(ds["f"]))("a");'),
		('ForFuncCall.Func.c_func', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'static std::map<std::string, std::string(*)(int)> dc = {{"f", &ForFuncCall::Func::func_cls}};'),
		('ForFuncCall.Func.c_func', 'function_def_raw.block.anno_assign[3]', defs.AnnoAssign, 'std::string s = dc["f"](1);'),

		('ForFuncCall.Class.literalize', 'function_def_raw.block.funccall[0]', defs.FuncCall, 'printf("Class2");'),
		('ForFuncCall.Class.literalize', 'function_def_raw.block.funccall[1]', defs.FuncCall, f'printf("{fixture_module_path}");'),
		('ForFuncCall.Class.literalize', 'function_def_raw.block.funccall[2]', defs.FuncCall, f'printf("{fixture_module_path}");'),
		('ForFuncCall.Class.literalize', 'function_def_raw.block.funccall[3]', defs.FuncCall, 'printf("Inner2");'),
		('ForFuncCall.Class.literalize', 'function_def_raw.block.funccall[4]', defs.FuncCall, 'printf("in_local");'),
		('ForFuncCall.Class.literalize', 'function_def_raw.block.funccall[5]', defs.FuncCall, 'printf("Alias2::in_local");'),
		('ForFuncCall.Class.literalize', 'function_def_raw.block.funccall[6]', defs.FuncCall, 'printf("Alias2::Inner2::func");'),
		('ForFuncCall.Class.literalize', 'function_def_raw.block.funccall[7]', defs.FuncCall, 'printf("Alias2");'),
		('ForFuncCall.Class.literalize', 'function_def_raw.block.funccall[8]', defs.FuncCall, 'printf("A");'),

		('ForFuncCall.Cast.cast_binary', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'int f_to_n = static_cast<int>(1.0);'),
		('ForFuncCall.Cast.cast_binary', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'float n_to_f = static_cast<float>(1);'),
		('ForFuncCall.Cast.cast_binary', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'bool n_to_b = static_cast<bool>(1);'),
		('ForFuncCall.Cast.cast_binary', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'int e_to_n = static_cast<int>(Values::A);'),

		('ForFuncCall.Cast.cast_string', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'std::string n_to_s = std::to_string(1);'),
		('ForFuncCall.Cast.cast_string', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'std::string f_to_s = std::to_string(1.0);'),
		('ForFuncCall.Cast.cast_string', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'int s_to_n = std::stoi(n_to_s);'),
		('ForFuncCall.Cast.cast_string', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'float s_to_f = std::stod(f_to_s);'),
		('ForFuncCall.Cast.cast_string', 'function_def_raw.block.assign[4]', defs.MoveAssign, 'std::string s_to_s{""};'),

		('ForFuncCall.Cast.cast_class', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'Base b = static_cast<Base>(sub);'),
		('ForFuncCall.Cast.cast_class', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'Base* bp = static_cast<Base*>(sub_p);'),
		('ForFuncCall.Cast.cast_class', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'std::map<std::string, Base*> dsbp = static_cast<std::map<std::string, Base*>>(dssp);'),

		('ForFuncCall.Cast.cast_enum', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'Values e = static_cast<Values>(0);'),
		('ForFuncCall.Cast.cast_enum', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'int n = static_cast<int>(Values::A);'),

		('ForFuncCall.Copy.__py_copy__', '', defs.Method, 'public:\n/** __py_copy__ */\nCopy(ForFuncCall::Copy& origin) {}'),
		('ForFuncCall.Copy.move_obj', 'function_def_raw.block.funccall', defs.FuncCall, 'to = via;'),
		('ForFuncCall.Copy.move_scalar', 'function_def_raw.block.funccall', defs.FuncCall, 'output = 1;'),

		('ForFuncCall.List.pop', 'function_def_raw.block.funccall[0]', defs.FuncCall, BlockExpects.list_pop(symbol='ns', index='1', var_type='int')),
		('ForFuncCall.List.pop', 'function_def_raw.block.funccall[1]', defs.FuncCall, BlockExpects.list_pop(symbol='ns', index='', var_type='int')),
		('ForFuncCall.List.insert', 'function_def_raw.block.funccall', defs.FuncCall, 'ns.insert(ns.begin() + 1, n);'),
		('ForFuncCall.List.extend', 'function_def_raw.block.funccall', defs.FuncCall, 'ns0.insert(ns0.end(), ns1);'),
		('ForFuncCall.List.clear', 'function_def_raw.block.funccall', defs.FuncCall, 'ns.clear();'),
		('ForFuncCall.List.contains', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'bool b_in = (std::find(ns.begin(), ns.end(), 1) != ns.end());'),
		('ForFuncCall.List.contains', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'bool b_not_in = (std::find(ns.begin(), ns.end(), 1) == ns.end());'),
		('ForFuncCall.List.fill', 'function_def_raw.block.assign', defs.MoveAssign, 'std::vector<int> n_x3 = std::vector<int>(3, n);'),
		('ForFuncCall.List.len', 'function_def_raw.block.funccall', defs.FuncCall, 'ns.size();'),
		('ForFuncCall.List.copy', 'function_def_raw.block.assign', defs.MoveAssign, 'std::vector<int> new_ns = ns;'),

		('ForFuncCall.Dict.pop', 'function_def_raw.block.funccall[0]', defs.FuncCall, BlockExpects.dict_pop(symbol='dsn', key='"a"', var_type='int')),
		('ForFuncCall.Dict.pop', 'function_def_raw.block.funccall[1]', defs.FuncCall, BlockExpects.dict_pop(symbol='dsn', key='"b"', var_type='int')),
		('ForFuncCall.Dict.keys', 'function_def_raw.block.funccall', defs.FuncCall, BlockExpects.dict_keys(symbol='dsn', var_type='std::string')),
		('ForFuncCall.Dict.values', 'function_def_raw.block.funccall', defs.FuncCall, BlockExpects.dict_values(symbol='dsn', var_type='int')),
		('ForFuncCall.Dict.get', 'function_def_raw.block.assign', defs.MoveAssign, 'int n = dsn.contains("a") ? dsn["a"] : 1;'),
		('ForFuncCall.Dict.clear', 'function_def_raw.block.funccall', defs.FuncCall, 'dsn.clear();'),
		('ForFuncCall.Dict.contains', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'bool b_in = dsn.contains("a");'),
		('ForFuncCall.Dict.contains', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'bool b_not_in = (!dsn.contains("a"));'),
		('ForFuncCall.Dict.len', 'function_def_raw.block.funccall', defs.FuncCall, 'dsn.size();'),
		('ForFuncCall.Dict.copy', 'function_def_raw.block.assign', defs.MoveAssign, 'std::map<std::string, int> new_dsn = dsn;'),

		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[0]', defs.FuncCall, 'std::string("").split(",");'),
		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[1]', defs.FuncCall, 'std::string("").join({"a"});'),
		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[2]', defs.FuncCall, 'std::string("").replace("from", "to");'),
		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[3]', defs.FuncCall, 'std::string("").lstrip(" ");'),
		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[4]', defs.FuncCall, 'std::string("").rstrip(" ");'),
		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[5]', defs.FuncCall, 'std::string("").strip(" ");'),
		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[6]', defs.FuncCall, 's.split(",");'),
		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[7]', defs.FuncCall, 's.join({"a"});'),
		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[8]', defs.FuncCall, 's.replace("from", "to");'),
		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[9]', defs.FuncCall, 's.lstrip(" ");'),
		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[10]', defs.FuncCall, 's.rstrip(" ");'),
		('ForFuncCall.String.mod_methods', 'function_def_raw.block.funccall[11]', defs.FuncCall, 's.strip(" ");'),
		('ForFuncCall.String.find_methods', 'function_def_raw.block.funccall[0]', defs.FuncCall, 'std::string("").find("a");'),
		('ForFuncCall.String.find_methods', 'function_def_raw.block.funccall[1]', defs.FuncCall, 'std::string("").find_last_of("a");'),
		('ForFuncCall.String.find_methods', 'function_def_raw.block.funccall[2]', defs.FuncCall, 'std::string("").count(".");'),
		('ForFuncCall.String.find_methods', 'function_def_raw.block.funccall[3]', defs.FuncCall, 'std::string("").starts_with("");'),
		('ForFuncCall.String.find_methods', 'function_def_raw.block.funccall[4]', defs.FuncCall, 'std::string("").ends_with("");'),
		('ForFuncCall.String.find_methods', 'function_def_raw.block.funccall[5]', defs.FuncCall, 's.find("a");'),
		('ForFuncCall.String.find_methods', 'function_def_raw.block.funccall[6]', defs.FuncCall, 's.find_last_of("a");'),
		('ForFuncCall.String.find_methods', 'function_def_raw.block.funccall[7]', defs.FuncCall, 's.count(".");'),
		('ForFuncCall.String.find_methods', 'function_def_raw.block.funccall[8]', defs.FuncCall, 's.starts_with("");'),
		('ForFuncCall.String.find_methods', 'function_def_raw.block.funccall[9]', defs.FuncCall, 's.ends_with("");'),
		('ForFuncCall.String.format', 'function_def_raw.block.funccall[0]', defs.FuncCall, 'std::format("%d, %f, %d, %s, %s, %p", 1, 2.0, true, "3", (s).c_str(), this);'),
		('ForFuncCall.String.format', 'function_def_raw.block.funccall[1]', defs.FuncCall, 'std::format(s, 1, 2, 3);'),
		('ForFuncCall.String.encode', 'function_def_raw.block.funccall[0]', defs.FuncCall, '(s).c_str();'),
		('ForFuncCall.String.encode', 'function_def_raw.block.funccall[1]', defs.FuncCall, '("");'),
		('ForFuncCall.String.decode', 'function_def_raw.block.funccall', defs.FuncCall, 'b.decode();'),  # FIXME 現状は一旦decodeのまま出力
		('ForFuncCall.String.len', 'function_def_raw.block.funccall', defs.FuncCall, 's.size();'),

		('ForBinaryOperator.char_op_by_str', 'function_def_raw.block.assign[0]', defs.MoveAssign, "bool a = string[0] >= 'A';"),
		('ForBinaryOperator.char_op_by_str', 'function_def_raw.block.assign[1]', defs.MoveAssign, "bool b = string[0] <= 'Z';"),
		('ForBinaryOperator.char_op_by_str', 'function_def_raw.block.assign[2]', defs.MoveAssign, "char c = string[0];"),
		('ForBinaryOperator.decimal_mod', 'function_def_raw.block.funccall', defs.FuncCall, "printf(fmod((fmod(1.0, 1)), (fmod(1, 1.0))));"),
		('ForBinaryOperator.comparison', 'function_def_raw.block.assign[0]', defs.MoveAssign, "bool v_eq = (v1 == v2) && (v1 != v2) && !v1;"),
		('ForBinaryOperator.comparison', 'function_def_raw.block.assign[1]', defs.MoveAssign, "bool c_eq = (c1 == c2) && (c1 != c2) && !c1;"),

		('ForTemplateClass.Delegate', '', defs.Class, BlockExpects.ForTemplateClass_Delegate),
		('ForTemplateClass.bind_call', 'function_def_raw.block.assign', defs.MoveAssign, 'ForTemplateClass::Delegate<bool, int> d{};'),
		('ForTemplateClass.bind_call', 'function_def_raw.block.funccall[1]', defs.FuncCall, 'd.bind(a, &ForTemplateClass::A::func);'),
		('ForTemplateClass.bind_call', 'function_def_raw.block.funccall[2]', defs.FuncCall, 'd.invoke(true, 1);'),
		('ForTemplateClass.boundary_call', '', defs.Method, BlockExpects.method(access='public', name='boundary_call', return_type='T_Base', statements=['return T_Base();'], template='T_Base')),

		('ForComp.list_comp_from_list', 'function_def_raw.block.list_comp[0]', defs.ListComp, BlockExpects.list_comp(proj_value='l[0]', proj_type='int', iterates='{{1}}', proj_symbols='l')),
		('ForComp.list_comp_from_list', 'function_def_raw.block.list_comp[1]', defs.ListComp, BlockExpects.list_comp(proj_value='n', proj_type='int', iterates='ns')),
		('ForComp.list_comp_from_list', 'function_def_raw.block.list_comp[2]', defs.ListComp, BlockExpects.list_comp(proj_value='cp', proj_type='const int*', iterates='cps', proj_infer='const auto')),
		('ForComp.list_comp_from_list', 'function_def_raw.block.list_comp[3]', defs.ListComp, BlockExpects.list_comp(proj_value='e0 + e1 + e2', proj_type='int', iterates='ts', proj_symbols='[e0, e1, e2]')),
		('ForComp.list_comp_from_list', 'function_def_raw.block.list_comp[4]', defs.ListComp, BlockExpects.list_comp_range(proj_value='i', proj_type='int', size='ns.size()', proj_symbol='i')),
		('ForComp.list_comp_from_list', 'function_def_raw.block.list_comp[5]', defs.ListComp, BlockExpects.list_comp_enumerate(proj_value='{i, n}', proj_type='std::tuple<int, int>', iterates='ns', proj_symbols=['i', 'n'])),

		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[0]', defs.ListComp, BlockExpects.list_comp(proj_value='s', proj_type='std::string', iterates='{{"a", 1}}', proj_symbols='[s, _]')),
		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[1]', defs.ListComp, BlockExpects.list_comp(proj_value='n', proj_type='int', iterates='{{"a", 1}}', proj_symbols='[_, n]')),
		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[2]', defs.ListComp, BlockExpects.list_comp(proj_value='{s, n}', proj_type='std::tuple<std::string, int>', iterates='{{"a", 1}}', proj_symbols='[s, n]')),
		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[3]', defs.ListComp, BlockExpects.list_comp(proj_value='s', proj_type='std::string', iterates='dsn', proj_symbols='[s, _]')),
		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[4]', defs.ListComp, BlockExpects.list_comp(proj_value='n', proj_type='int', iterates='dsn', proj_symbols='[_, n]')),
		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[5]', defs.ListComp, BlockExpects.list_comp(proj_value='{s, n}', proj_type='std::tuple<std::string, int>', iterates='dsn', proj_symbols='[s, n]')),
		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[6]', defs.ListComp, BlockExpects.list_comp(proj_value='s', proj_type='std::string', iterates='*(psn)', proj_symbols='[s, _]')),
		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[7]', defs.ListComp, BlockExpects.list_comp(proj_value='n', proj_type='int', iterates='*(psn)', proj_symbols='[_, n]')),
		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[8]', defs.ListComp, BlockExpects.list_comp(proj_value='{s, n}', proj_type='std::tuple<std::string, int>', iterates='*(psn)', proj_symbols='[s, n]')),
		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[9]', defs.ListComp, BlockExpects.list_comp(proj_value='kp', proj_type='int*', iterates='dpp', proj_symbols='[kp, _]')),
		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[10]', defs.ListComp, BlockExpects.list_comp(proj_value='vp', proj_type='int*', iterates='dpp', proj_symbols='[_, vp]')),
		('ForComp.list_comp_from_dict', 'function_def_raw.block.list_comp[11]', defs.ListComp, BlockExpects.list_comp(proj_value='{kp, vp}', proj_type='std::tuple<int*, int*>', iterates='dpp', proj_symbols='[kp, vp]')),

		('ForComp.dict_comp_from_list', 'function_def_raw.block.dict_comp[0]', defs.DictComp, BlockExpects.dict_comp(proj_key='l[0]', proj_value='l', proj_key_type='int', proj_value_type='std::vector<int>', iterates='{{1}}', proj_symbols='l')),
		('ForComp.dict_comp_from_list', 'function_def_raw.block.dict_comp[1]', defs.DictComp, BlockExpects.dict_comp(proj_key='n', proj_value='n', proj_key_type='int', proj_value_type='int', iterates='ns', proj_symbols='n')),
		('ForComp.dict_comp_from_list', 'function_def_raw.block.dict_comp[2]', defs.DictComp, BlockExpects.dict_comp(proj_key='cp', proj_value='cp', proj_key_type='const int*', proj_value_type='const int*', iterates='cps', proj_symbols='cp', proj_infer='const auto')),
		('ForComp.dict_comp_from_list', 'function_def_raw.block.dict_comp[3]', defs.DictComp, BlockExpects.dict_comp(proj_key='e0', proj_value='{e1, e2}', proj_key_type='int', proj_value_type='std::tuple<int, int>', iterates='ts', proj_symbols='[e0, e1, e2]')),

		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[0]', defs.DictComp, BlockExpects.dict_comp(proj_key='s', proj_value='s', proj_key_type='std::string', proj_value_type='std::string', iterates='{{"a", 1}}', proj_symbols='[s, _]')),
		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[1]', defs.DictComp, BlockExpects.dict_comp(proj_key='n', proj_value='n', proj_key_type='int', proj_value_type='int', iterates='{{"a", 1}}', proj_symbols='[_, n]')),
		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[2]', defs.DictComp, BlockExpects.dict_comp(proj_key='s', proj_value='n', proj_key_type='std::string', proj_value_type='int', iterates='{{"a", 1}}', proj_symbols='[s, n]')),
		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[3]', defs.DictComp, BlockExpects.dict_comp(proj_key='s', proj_value='s', proj_key_type='std::string', proj_value_type='std::string', iterates='dsn', proj_symbols='[s, _]')),
		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[4]', defs.DictComp, BlockExpects.dict_comp(proj_key='n', proj_value='n', proj_key_type='int', proj_value_type='int', iterates='dsn', proj_symbols='[_, n]')),
		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[5]', defs.DictComp, BlockExpects.dict_comp(proj_key='s', proj_value='n', proj_key_type='std::string', proj_value_type='int', iterates='dsn', proj_symbols='[s, n]')),
		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[6]', defs.DictComp, BlockExpects.dict_comp(proj_key='s', proj_value='s', proj_key_type='std::string', proj_value_type='std::string', iterates='*(psn)', proj_symbols='[s, _]')),
		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[7]', defs.DictComp, BlockExpects.dict_comp(proj_key='n', proj_value='n', proj_key_type='int', proj_value_type='int', iterates='*(psn)', proj_symbols='[_, n]')),
		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[8]', defs.DictComp, BlockExpects.dict_comp(proj_key='s', proj_value='n', proj_key_type='std::string', proj_value_type='int', iterates='*(psn)', proj_symbols='[s, n]')),
		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[9]', defs.DictComp, BlockExpects.dict_comp(proj_key='kp', proj_value='kp', proj_key_type='int*', proj_value_type='int*', iterates='dpp', proj_symbols='[kp, _]')),
		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[10]', defs.DictComp, BlockExpects.dict_comp(proj_key='vp', proj_value='vp', proj_key_type='int*', proj_value_type='int*', iterates='dpp', proj_symbols='[_, vp]')),
		('ForComp.dict_comp_from_dict', 'function_def_raw.block.dict_comp[11]', defs.DictComp, BlockExpects.dict_comp(proj_key='kp', proj_value='vp', proj_key_type='int*', proj_value_type='int*', iterates='dpp', proj_symbols='[kp, vp]')),

		('ForLambda.expression', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'std::function<int()> f = [&]() -> int { return 1; };'),
		('ForLambda.expression', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'int n = f();'),
		('ForLambda.expression', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'std::string s = ([&]() -> std::string { return "a"; })();'),
		('ForLambda.expression', 'function_def_raw.block.if_stmt', defs.If, 'if (([&]() -> bool { return true; })()) {\n\n}'),
	])
	def test_exec(self, local_path: str, offset_path: str, expected_type: type[Node], expected: str) -> None:
		# local_pathが空の場合はEntrypointを基点ノードとする
		via_node = self.fixture.shared_module.entrypoint
		if local_path:
			via_node = self.fixture.get(Reflections).from_fullyname(ModuleDSN.full_joined(self.fixture_module_path, local_path)).node

		full_path = ModuleDSN.local_joined(via_node.full_path, offset_path)
		node = self.fixture.shared_module.entrypoint.whole_by(full_path).as_a(expected_type)
		actual = self.fixture.get(Py2Cpp).transpile(node)
		self.assertEqual(expected, actual)
