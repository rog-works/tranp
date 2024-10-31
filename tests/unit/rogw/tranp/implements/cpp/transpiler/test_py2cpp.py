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
from rogw.tranp.lang.module import to_fullyname
from rogw.tranp.lang.profile import profiler
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.test.helper import data_provider
from rogw.tranp.transpiler.types import TranspilerOptions
from rogw.tranp.view.render import Renderer
from tests.test.fixture import Fixture
from tests.unit.rogw.tranp.implements.cpp.transpiler.fixtures.test_py2cpp_expect import BlockExpects


def fixture_translation_mapping(files: IFileLoader) -> TranslationMapping:
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture_translations = {
		alias_dsn(ModuleDSN.full_joined(fixture_module_path, 'Alias')): 'Alias2',
		alias_dsn(ModuleDSN.full_joined(fixture_module_path, 'Alias.inner')): 'inner_b',
		alias_dsn(ModuleDSN.full_joined(fixture_module_path, 'Alias.Inner')): 'Inner2',
		alias_dsn(ModuleDSN.full_joined(fixture_module_path, 'Alias.Inner.V')): 'V2',
	}
	return example_translation_mapping_cpp(files).merge(fixture_translations)


def make_renderer(i18n: I18n) -> Renderer:
	return Renderer([os.path.join(tranp_dir(), 'data/cpp/template')], i18n.t)


class TestPy2Cpp(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__, {
		to_fullyname(Py2Cpp): Py2Cpp,
		to_fullyname(PluginProvider): cpp_plugin_provider,
		to_fullyname(TranslationMapping): fixture_translation_mapping,
		to_fullyname(TranspilerOptions): lambda: TranspilerOptions(verbose=False),
		to_fullyname(Renderer): make_renderer,
	})

	@profiler(on=False)
	@data_provider([
		('', 'import_stmt[1]', defs.Import, '// #include "typing.h"'),

		('', 'funccall[7]', defs.FuncCall, '#pragma once'),
		('', 'funccall[8]', defs.FuncCall, '#include <memory>'),
		('', 'funccall[9]', defs.FuncCall, 'MACRO()'),

		('T', '', defs.TemplateClass, '// template<typename T>'),
		('T2', '', defs.TemplateClass, '// template<typename T2>'),

		('DSI', '', defs.AltClass, 'using DSI = std::map<std::string, int>;'),
		('TSII', '', defs.AltClass, 'using TSII = std::tuple<std::string, int, int>;'),

		('DeclOps', '', defs.Class, BlockExpects.DeclOps),

		('Base.sub_implements', '', defs.Method, 'public:\n/** sub_implements */\nvirtual void sub_implements() = 0;'),
		('Base.allowed_overrides', '', defs.Method, 'public:\n/** allowed_overrides */\nvirtual int allowed_overrides() {\n\treturn 1;\n}'),
		('Base.base_class_func', '', defs.ClassMethod, 'public:\n/** base_class_func */\nstatic int base_class_func() {}'),
		('Base.base_prop', '', defs.Method, 'public:\n/** base_prop */\nstd::string base_prop() {}'),
		('Base._pure_public_method', '', defs.Method, 'public:\n/** _pure_public_method */\nstd::string _pure_public_method() const {}'),

		('Sub', 'class_def_raw.block.comment_stmt[5]', defs.Comment, '// FIXME other: Any'),

		('CVarOps.ret_raw', 'function_def_raw.block.return_stmt', defs.Return, 'return Sub(0);'),
		('CVarOps.ret_cp', 'function_def_raw.block.return_stmt', defs.Return, 'return new Sub(0);'),
		('CVarOps.ret_csp', 'function_def_raw.block.return_stmt', defs.Return, 'return std::make_shared<Sub>(0);'),

		('CVarOps.local_move', 'function_def_raw.block.anno_assign[0]', defs.AnnoAssign, 'Sub a = Sub(0);'),
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
		('CVarOps.declare', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp = std::shared_ptr<std::vector<int>>(new std::vector<int>({1}));'),
		('CVarOps.declare', 'function_def_raw.block.assign[4]', defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp2 = std::shared_ptr<std::vector<int>>(new std::vector<int>());'),
		('CVarOps.declare', 'function_def_raw.block.assign[5]', defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp3 = std::shared_ptr<std::vector<int>>(new std::vector<int>(2));'),
		('CVarOps.declare', 'function_def_raw.block.assign[6]', defs.MoveAssign, 'std::shared_ptr<std::vector<int>> arr_sp4 = std::shared_ptr<std::vector<int>>(new std::vector<int>(2, 0));'),
		('CVarOps.declare', 'function_def_raw.block.assign[7]', defs.MoveAssign, 'std::vector<int>& arr_r = arr;'),
		('CVarOps.declare', 'function_def_raw.block.assign[8]', defs.MoveAssign, 'std::shared_ptr<int> n_sp_empty = std::shared_ptr<int>();'),
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

		('FuncOps.print', 'function_def_raw.block.funccall', defs.FuncCall, 'printf("message. %d, %f, %s", 1, 1.0, "abc");'),
		('FuncOps.kw_params', 'function_def_raw.block.assign', defs.MoveAssign, 'std::string a = this->kw_params(1, 2);'),

		('EnumOps.Values', '', defs.Enum, '/** Values */\npublic: enum class Values {\n\tA = 0,\n\tB = 1,\n};'),
		('EnumOps.assign', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'EnumOps::Values a = EnumOps::Values::A;'),
		('EnumOps.assign', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'std::map<EnumOps::Values, std::string> d = {\n\t{EnumOps::Values::A, "A"},\n\t{EnumOps::Values::B, "B"},\n};'),
		('EnumOps.assign', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'std::string da = d[EnumOps::Values::A];'),
		('EnumOps.cast', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'EnumOps::Values e = static_cast<EnumOps::Values>(0);'),
		('EnumOps.cast', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'int n = static_cast<int>(EnumOps::Values::A);'),

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
		('AccessOps.double_colon', 'function_def_raw.block.funccall[4].arguments.argvalue', defs.Argument, 'EnumOps::Values::A'),
		('AccessOps.double_colon', 'function_def_raw.block.anno_assign', defs.AnnoAssign, 'std::map<EnumOps::Values, std::string> d = {\n\t{EnumOps::Values::A, "A"},\n\t{EnumOps::Values::B, "B"},\n};'),

		('AccessOps.indexer', 'function_def_raw.block.funccall[0].arguments.argvalue', defs.Argument, 'arr_p[0]'),
		('AccessOps.indexer', 'function_def_raw.block.funccall[1].arguments.argvalue', defs.Argument, 'arr_sp[0]'),
		('AccessOps.indexer', 'function_def_raw.block.funccall[2].arguments.argvalue', defs.Argument, 'arr_ar[0]'),

		('Alias.Inner', '', defs.Class, '/** Inner2 */\nclass Inner2 {\n\tpublic: inline static int V2 = 0;\n\tpublic:\n\t/** func */\n\tvoid func() {}\n};'),
		('Alias.__init__', '', defs.Constructor, 'public:\n/** __init__ */\nAlias2() : inner_b(Alias2::Inner2()) {}'),
		('Alias.in_param_return', '', defs.Method, 'public:\n/** in_param_return */\nAlias2 in_param_return(Alias2 a) {}'),
		('Alias.in_param_return2', '', defs.Method, 'public:\n/** in_param_return2 */\nAlias2::Inner2 in_param_return2(Alias2::Inner2 i) {}'),
		('Alias.in_local', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'Alias2 a = Alias2();'),
		('Alias.in_local', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'Alias2::Inner2 i = Alias2::Inner2();'),
		('Alias.in_class_method', 'function_def_raw.block.funccall', defs.FuncCall, 'Alias2::in_class_method();'),
		('Alias.in_class_method', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'Alias2::Values a = Alias2::Values::A;'),
		('Alias.in_class_method', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'std::map<Alias2::Values, Alias2::Values> d = {\n\t{Alias2::Values::A, Alias2::Values::B},\n\t{Alias2::Values::B, Alias2::Values::A},\n};'),
		('Alias.in_class_method', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'std::map<int, std::vector<int>> d2 = {\n\t{static_cast<int>(Alias2::Values::A), {static_cast<int>(Alias2::Values::B)}},\n\t{static_cast<int>(Alias2::Values::B), {static_cast<int>(Alias2::Values::A)}},\n};'),
		('Alias.InnerB.super_call', 'function_def_raw.block.funccall', defs.FuncCall, 'Alias2::Inner2::func();'),
		('Alias.litelize', 'function_def_raw.block.funccall[0]', defs.FuncCall, 'printf("Alias2");'),
		('Alias.litelize', 'function_def_raw.block.funccall[1]', defs.FuncCall, f'printf("{fixture_module_path}");'),
		('Alias.litelize', 'function_def_raw.block.funccall[2]', defs.FuncCall, f'printf("{fixture_module_path}");'),
		('Alias.litelize', 'function_def_raw.block.funccall[3]', defs.FuncCall, 'printf("Inner2");'),
		('Alias.litelize', 'function_def_raw.block.funccall[4]', defs.FuncCall, 'printf("in_local");'),
		('Alias.litelize', 'function_def_raw.block.funccall[5]', defs.FuncCall, 'printf("Alias2::in_local");'),
		('Alias.litelize', 'function_def_raw.block.funccall[6]', defs.FuncCall, 'printf("Alias2::Inner2::func");'),

		('CompOps.list_comp', 'function_def_raw.block.assign[1]', defs.MoveAssign, BlockExpects.CompOps_list_comp_assign_values1),
		('CompOps.dict_comp', 'function_def_raw.block.assign[1]', defs.MoveAssign, BlockExpects.CompOps_dict_comp_assign_kvs0_1),
		('CompOps.dict_comp', 'function_def_raw.block.assign[3]', defs.MoveAssign, BlockExpects.CompOps_dict_comp_assign_kvsp_1),
		('CompOps.dict_comp', 'function_def_raw.block.assign[5]', defs.MoveAssign, BlockExpects.CompOps_dict_comp_assign_kvs2),

		('ForOps.range', 'function_def_raw.block.for_stmt', defs.For, 'for (auto i = 0; i < 10; i++) {\n\n}'),
		('ForOps.enumerate', 'function_def_raw.block.for_stmt', defs.For, BlockExpects.ForOps_enumerate_for_index_key),
		('ForOps.dict_items', 'function_def_raw.block.for_stmt[1]', defs.For, 'for (auto& [key, value] : kvs) {\n\n}'),
		('ForOps.dict_items', 'function_def_raw.block.for_stmt[3]', defs.For, 'for (auto& [key, value] : *(kvs_p)) {\n\n}'),

		('ListOps.len', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'int size_values = values.size();'),
		('ListOps.pop', 'function_def_raw.block.assign[1]', defs.MoveAssign, BlockExpects.ListOps_pop_assign_value0),
		('ListOps.pop', 'function_def_raw.block.assign[2]', defs.MoveAssign, BlockExpects.ListOps_pop_assign_value1),
		('ListOps.contains', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'bool b_in = (std::find(values.begin(), values.end(), 1) != values.end());'),
		('ListOps.contains', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'bool b_not_in = (std::find(values.begin(), values.end(), 1) == values.end());'),
		('ListOps.fill', 'function_def_raw.block.assign', defs.MoveAssign, 'std::vector<int> n_x3 = std::vector<int>(3, n);'),
		('ListOps.slice', 'function_def_raw.block.assign[0]', defs.MoveAssign, BlockExpects.ListOps_slice_assign_ns0),
		('ListOps.slice', 'function_def_raw.block.assign[1]', defs.MoveAssign, BlockExpects.ListOps_slice_assign_ns1),
		('ListOps.slice', 'function_def_raw.block.assign[2]', defs.MoveAssign, BlockExpects.ListOps_slice_assign_ns2),
		('ListOps.delete', 'function_def_raw.block.del_stmt', defs.Delete, 'ns.erase(ns.begin() + 1);\nns.erase(ns.begin() + 2);'),
		('ListOps.insert', 'function_def_raw.block.funccall', defs.FuncCall, 'ns.insert(ns.begin() + 1, n);'),
		('ListOps.extend', 'function_def_raw.block.funccall', defs.FuncCall, 'ns0.insert(ns0.end(), ns1);'),
		('ListOps.clear', 'function_def_raw.block.funccall', defs.FuncCall, 'arr.clear();'),

		('DictOps.len', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'int size_kvs = kvs.size();'),
		('DictOps.pop', 'function_def_raw.block.assign[1]', defs.MoveAssign, BlockExpects.DictOps_pop_assign_value0),
		('DictOps.pop', 'function_def_raw.block.assign[2]', defs.MoveAssign, BlockExpects.DictOps_pop_assign_value1),
		('DictOps.keys', 'function_def_raw.block.assign[1]', defs.MoveAssign, BlockExpects.DictOps_keys_assign_keys),
		('DictOps.values', 'function_def_raw.block.assign[1]', defs.MoveAssign, BlockExpects.DictOps_values_assign_values),
		('DictOps.decl', 'function_def_raw.block.assign', defs.MoveAssign, 'std::map<int, std::vector<int>> d = {{1, {\n\t{1},\n\t{2},\n\t{3},\n}}};'),
		('DictOps.contains', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'bool b_in = d.contains("a");'),
		('DictOps.contains', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'bool b_not_in = (!d.contains("a"));'),
		('DictOps.delete', 'function_def_raw.block.del_stmt', defs.Delete, 'dsn.erase("a");\ndsn.erase("b");'),
		('DictOps.clear', 'function_def_raw.block.funccall', defs.FuncCall, 'dsn.clear();'),

		('CastOps.cast_binary', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'int f_to_n = static_cast<int>(1.0);'),
		('CastOps.cast_binary', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'float n_to_f = static_cast<float>(1);'),
		('CastOps.cast_binary', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'bool n_to_b = static_cast<bool>(1);'),
		('CastOps.cast_binary', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'int e_to_n = static_cast<int>(EnumOps::Values::A);'),

		('CastOps.cast_string', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'std::string n_to_s = std::to_string(1);'),
		('CastOps.cast_string', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'std::string f_to_s = std::to_string(1.0);'),
		('CastOps.cast_string', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'int s_to_n = atoi(n_to_s);'),
		('CastOps.cast_string', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'float s_to_f = atof(f_to_s);'),
		('CastOps.cast_string', 'function_def_raw.block.assign[4]', defs.MoveAssign, 'std::string s_to_s = std::string("");'),

		('CastOps.cast_class', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'Base b = static_cast<Base>(sub);'),
		('CastOps.cast_class', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'Base* bp = static_cast<Base*>(sub_p);'),
		('CastOps.cast_class', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'std::map<std::string, Base*> dsbp = static_cast<std::map<std::string, Base*>>(dssp);'),

		('Nullable.params', '', defs.Method, 'public:\n/** params */\nvoid params(Sub* p) {}'),
		('Nullable.returns', '', defs.Method, 'public:\n/** returns */\nSub* returns() {}'),
		('Nullable.var_move', 'function_def_raw.block.anno_assign', defs.AnnoAssign, 'Sub* p = nullptr;'),
		('Nullable.var_move', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'p = (&(base));'),
		('Nullable.var_move', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'p = nullptr;'),
		('Nullable.var_move', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'p = (sp).get();'),
		('Nullable.var_move', 'function_def_raw.block.if_stmt.if_clause.block.return_stmt', defs.Return, 'return (*(p));'),

		('Template.T2Class', '', defs.Class, '/** T2Class */\ntemplate<typename T2>\nclass T2Class {\n\n};'),
		('Template.__init__', '', defs.Constructor, 'public:\n/** __init__ */\nTemplate(T v) {}'),
		('Template.class_method_t', '', defs.ClassMethod, 'public:\n/** class_method_t */\ntemplate<typename T2>\nstatic T2 class_method_t(T2 v2) {}'),
		('Template.class_method_t_and_class_t', '', defs.ClassMethod, 'public:\n/** class_method_t_and_class_t */\ntemplate<typename T2>\nstatic T2 class_method_t_and_class_t(T v, T2 v2) {}'),
		('Template.method_t', '', defs.Method, 'public:\n/** method_t */\ntemplate<typename T2>\nT2 method_t(T2 v2) {}'),
		('Template.method_t_and_class_t', '', defs.Method, 'public:\n/** method_t_and_class_t */\ntemplate<typename T2>\nT2 method_t_and_class_t(T v, T2 v2) {}'),

		('GenericOps.temporal', 'function_def_raw.block.assign', defs.MoveAssign, 'T a = value;'),
		('GenericOps.new', 'function_def_raw.block.assign', defs.MoveAssign, 'GenericOps<int> a = GenericOps<int>();'),

		('Struct', '', defs.Class, '/** Struct */\nstruct Struct {\n\tpublic: int a;\n\tpublic: std::string b;\n\tpublic:\n\t/** __init__ */\n\tStruct(int a, std::string b) : a(a), b(b) {}\n};'),

		('StringOps.methods', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'bool a = s.starts_with("");'),
		('StringOps.methods', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'bool b = s.ends_with("");'),
		('StringOps.slice', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'std::string a = s.substr(1, s.size() - (1));'),
		('StringOps.slice', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'std::string b = s.substr(0, 5);'),
		('StringOps.len', 'function_def_raw.block.assign', defs.MoveAssign, 'int a = s.size();'),
		('StringOps.format', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'std::string a = std::format("%d, %f, %d, %s, %s, %p", 1, 2.0, true, "3", (s).c_str(), this);'),
		('StringOps.format', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'std::string b = std::format(s, 1, 2, 3);'),

		('AssignOps.assign', 'function_def_raw.block.anno_assign', defs.AnnoAssign, 'int a = 1;'),
		('AssignOps.assign', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'std::string b = "b";'),
		('AssignOps.assign', 'function_def_raw.block.aug_assign', defs.AugAssign, 'b += std::to_string(a);'),
		('AssignOps.assign', 'function_def_raw.block.assign[3]', defs.MoveAssign, 'std::vector<TSII> tsiis2 = tsiis;'),
		('AssignOps.assign', 'function_def_raw.block.assign[4]', defs.MoveAssign, 'TSII tsii = tsiis[0];'),
		('AssignOps.assign', 'function_def_raw.block.assign[5]', defs.MoveAssign, 'auto [ts, ti1, ti2] = tsii;'),

		('template_func', '', defs.Function, '/** template_func */\ntemplate<typename T>\nT template_func(T v) {}'),

		('ForClassMethod.make', '', defs.ClassMethod, 'public:\n/** make */\nstatic ForClassMethod make() {\n\tForClassMethod inst = ForClassMethod();\n\treturn inst;\n}'),

		('ForFuncCall.CallableType', '', defs.Class, '/** CallableType */\nclass CallableType {\n\tpublic: std::function<bool(int, std::string)> func;\n\tpublic:\n\t/** __init__ */\n\tCallableType(std::function<bool(int, std::string)> func) : func(func) {}\n};'),

		('ForFuncCall.Copy.__py_copy__', '', defs.Method, 'public:\n/** __py_copy__ */\nCopy(ForFuncCall::Copy& origin) {}'),
		('ForFuncCall.Copy.move_obj', 'function_def_raw.block.funccall', defs.FuncCall, 'to = via;'),
		('ForFuncCall.Copy.move_scalar', 'function_def_raw.block.funccall', defs.FuncCall, 'output = 1;'),

		# FIXME 型推論自体に問題はなく、トランスパイルが期待通りではないと言うだけ
		# FIXME 型を明示すれば回避できる上、C++で関数の代入はまずしない
		# FIXME 本来の期待値 ('ForFuncCall.move_assign', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'std::function<bool(int, std::string))> func = caller.func;'),
		('ForFuncCall.move_assign', 'function_def_raw.block.assign[0]', defs.MoveAssign, 'std::function<int, std::string, bool> func = caller.func;'),
		('ForFuncCall.move_assign', 'function_def_raw.block.assign[1]', defs.MoveAssign, 'bool b0 = caller.func(0, "");'),
		('ForFuncCall.move_assign', 'function_def_raw.block.assign[2]', defs.MoveAssign, 'bool b1 = func(0, "");'),

		('ForBinaryOperator.char_op_by_str', 'function_def_raw.block.assign[0]', defs.MoveAssign, "bool a = string[0] >= 'A';"),
		('ForBinaryOperator.char_op_by_str', 'function_def_raw.block.assign[1]', defs.MoveAssign, "bool b = string[0] <= 'Z';"),
		('ForBinaryOperator.char_op_by_str', 'function_def_raw.block.assign[2]', defs.MoveAssign, "char c = string[0];"),
		('ForBinaryOperator.decimal_mod', 'function_def_raw.block.funccall', defs.FuncCall, "printf(fmod((fmod(1.0, 1)), (fmod(1, 1.0))));"),

		('ForTemplateClass.Delegate', '', defs.Class, BlockExpects.ForTemplateClass_Delegate),
		('ForTemplateClass.bind_call', 'function_def_raw.block.assign', defs.MoveAssign, 'ForTemplateClass::Delegate<bool, int> d = ForTemplateClass::Delegate<bool, int>();'),
		('ForTemplateClass.bind_call', 'function_def_raw.block.funccall[1]', defs.FuncCall, 'd.bind(a, &ForTemplateClass::A::func);'),
		('ForTemplateClass.bind_call', 'function_def_raw.block.funccall[2]', defs.FuncCall, 'd.invoke(true, 1);'),
	])
	def test_exec(self, local_path: str, offset_path: str, expected_type: type[Node], expected: str) -> None:
		# local_pathが空の場合はEntrypointを基点ノードとする
		via_node = self.fixture.shared_module.entrypoint
		if local_path:
			via_node = self.fixture.get(Reflections).from_fullyname(ModuleDSN.full_joined(self.fixture_module_path, local_path)).node

		full_path = ModuleDSN.local_joined(via_node.full_path, offset_path)
		node = self.fixture.shared_module.entrypoint.whole_by(full_path).as_a(expected_type)
		actual = self.fixture.get(Py2Cpp).transpile(node)
		self.assertEqual(actual, expected)
