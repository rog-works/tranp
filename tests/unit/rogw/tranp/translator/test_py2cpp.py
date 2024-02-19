import os

from unittest import TestCase

from rogw.tranp.analyze.symbols import Symbols
from rogw.tranp.app.io import appdir
from rogw.tranp.ast.dsn import DSN
from rogw.tranp.errors import LogicError
import rogw.tranp.node.definition as defs
from rogw.tranp.node.node import Node
from rogw.tranp.translator.option import TranslatorOptions
from rogw.tranp.translator.py2cpp import Py2Cpp
from rogw.tranp.view.render import Renderer
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


def _ast(before: str, after: str) -> str:
	aliases = {
		'CVarOps.ret_raw.return': 'file_input.class_def[2].class_def_raw.block.function_def[0].function_def_raw.block.return_stmt',
		'CVarOps.ret_cp.return': 'file_input.class_def[2].class_def_raw.block.function_def[1].function_def_raw.block.return_stmt',
		'CVarOps.ret_csp.return': 'file_input.class_def[2].class_def_raw.block.function_def[2].function_def_raw.block.return_stmt',
		'CVarOps.local_move.block': 'file_input.class_def[2].class_def_raw.block.function_def[3].function_def_raw.block',
		'CVarOps.param_move.block': 'file_input.class_def[2].class_def_raw.block.function_def[4].function_def_raw.block',
		'CVarOps.invoke_method.block': 'file_input.class_def[2].class_def_raw.block.function_def[5].function_def_raw.block',
		'FuncOps.print.block': 'file_input.class_def[3].class_def_raw.block.function_def.function_def_raw.block',
		'AccessOps.Values': 'file_input.class_def[5].class_def_raw.block.class_def',
		'AccessOps.__init__': 'file_input.class_def[5].class_def_raw.block.function_def[1]',
		'AccessOps.dot.block': 'file_input.class_def[5].class_def_raw.block.function_def[2].function_def_raw.block',
		'AccessOps.arrow.block': 'file_input.class_def[5].class_def_raw.block.function_def[3].function_def_raw.block',
		'AccessOps.double_colon.block': 'file_input.class_def[5].class_def_raw.block.function_def[4].function_def_raw.block',
		'Alias.Inner': 'file_input.class_def[7].class_def_raw.block.class_def',
		'Alias.__init__': 'file_input.class_def[7].class_def_raw.block.function_def[1]',
		'Alias.in_param_return': 'file_input.class_def[7].class_def_raw.block.function_def[2]',
		'Alias.in_param_return2': 'file_input.class_def[7].class_def_raw.block.function_def[3]',
		'Alias.in_local.block': 'file_input.class_def[7].class_def_raw.block.function_def[4].function_def_raw.block',
		'CompOps.list_comp.block': 'file_input.class_def[8].class_def_raw.block.function_def[1].function_def_raw.block',
		'CompOps.dict_comp.block': 'file_input.class_def[8].class_def_raw.block.function_def[2].function_def_raw.block',
		'ForOps.range.block': 'file_input.class_def[9].class_def_raw.block.function_def[0].function_def_raw.block',
		'ForOps.enumerate.block': 'file_input.class_def[9].class_def_raw.block.function_def[1].function_def_raw.block',
		'ForOps.dict_items.block': 'file_input.class_def[9].class_def_raw.block.function_def[2].function_def_raw.block',
		'ListOps.len.block': 'file_input.class_def[10].class_def_raw.block.function_def[0].function_def_raw.block',
		'ListOps.pop.block': 'file_input.class_def[10].class_def_raw.block.function_def[1].function_def_raw.block',
		'DictOps.len.block': 'file_input.class_def[11].class_def_raw.block.function_def[0].function_def_raw.block',
		'DictOps.pop.block': 'file_input.class_def[11].class_def_raw.block.function_def[1].function_def_raw.block',
		'DictOps.keys.block': 'file_input.class_def[11].class_def_raw.block.function_def[2].function_def_raw.block',
		'DictOps.values.block': 'file_input.class_def[11].class_def_raw.block.function_def[3].function_def_raw.block',
		'CastOps.cast.block': 'file_input.class_def[12].class_def_raw.block.function_def.function_def_raw.block',
		'import.typing': 'file_input.import_stmt[13]',
		'DSI': 'file_input.class_assign',
	}
	return DSN.join(aliases[before], after)


class BlockExpects:
	CompOps_list_comp_assign_values1 = \
"""std::vector<int> values1 = [this, &]() -> std::vector<int> {
	std::vector<int> __ret;
	for (auto& value : values0) {
		__ret.push_back(value);
	}
	return __ret;
}();"""

	CompOps_dict_comp_assign_kvs1 = \
"""std::map<std::string, CompOps::C> kvs1 = [this, &]() -> std::map<std::string, CompOps::C> {
	std::map<std::string, CompOps::C> __ret;
	for (auto& [key, value] : kvs0.items()) {
		__ret.emplace({key, value});
	}
	return __ret;
}();"""

	ForOps_enumerate_for_index_key = \
"""auto __for_iterates_1572 = [&]() -> std::map<int, std::string> {
	std::map<int, std::string> __ret;
	int __index = 0;
	for (auto& __entry : keys) {
		__ret.emplace(__index++, __entry);
	}
	return __ret;
}();
for (auto& [index, key] : __for_iterates_1572) {
	print(index, key);
}"""

	ForOps_dict_items_for_key_value = \
"""for (auto& [key, value] : kvs) {
	print(key, value);
}"""

	ListOps_pop_assign_value0 = \
"""int value0 = [&]() -> int {
	auto __iter = values.begin() + 1;
	auto __copy = *__iter;
	values.erase(__iter);
	return __copy;
}();"""

	ListOps_pop_assign_value1 = \
"""int value1 = [&]() -> int {
	auto __iter = values.end() - 1;
	auto __copy = *__iter;
	values.erase(__iter);
	return __copy;
}();"""

	DictOps_pop_assign_value0 = \
"""int value0 = [&]() -> int {
	auto __copy = values["a"];
	values.erase("a");
	return __copy;
}();"""

	DictOps_pop_assign_value1 = \
"""int value1 = [&]() -> int {
	auto __copy = values["b"];
	values.erase("b");
	return __copy;
}();"""

	DictOps_keys_assign_keys = \
"""std::vector<std::string> keys = [&]() -> std::vector<std::string> {
	std::vector<std::string> __ret;
	for (auto [__key, _] : kvs) {
		__ret.push_back(__key);
	}
	return __ret;
}();"""

	DictOps_values_assign_values = \
"""std::vector<int> values = [&]() -> std::vector<int> {
	std::vector<int> __ret;
	for (auto [_, __value] : kvs) {
		__ret.push_back(__value);
	}
	return __ret;
}();"""


class TestPy2Cpp(TestCase):
	fixture = Fixture.make(__file__)

	def translator(self) -> Py2Cpp:
		renderer = Renderer(os.path.abspath(os.path.join(appdir(), 'example/template')))
		options = TranslatorOptions(verbose=False)
		return Py2Cpp(self.fixture.get(Symbols), renderer, options)

	@data_provider([
		(_ast('CVarOps.ret_raw.return', ''), defs.Return, 'return Base();'),
		(_ast('CVarOps.ret_cp.return', ''), defs.Return, 'return new Base();'),
		(_ast('CVarOps.ret_csp.return', ''), defs.Return, 'return std::make_shared<Base>();'),

		(_ast('CVarOps.local_move.block', 'anno_assign[0]'), defs.AnnoAssign, 'Base a = Base();'),
		(_ast('CVarOps.local_move.block', 'anno_assign[1]'), defs.AnnoAssign, 'Base* ap = &(a);'),
		(_ast('CVarOps.local_move.block', 'anno_assign[2]'), defs.AnnoAssign, 'std::shared_ptr<Base> asp = std::make_shared<Base>();'),
		(_ast('CVarOps.local_move.block', 'anno_assign[3]'), defs.AnnoAssign, 'Base& ar = a;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].block.assign[0]'), defs.MoveAssign, 'a = a;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].block.assign[1]'), defs.MoveAssign, 'a = *(ap);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].block.assign[2]'), defs.MoveAssign, 'a = *(asp);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[4].block.assign[3]'), defs.MoveAssign, 'a = ar;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].block.assign[0]'), defs.MoveAssign, 'ap = &(a);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].block.assign[1]'), defs.MoveAssign, 'ap = ap;'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].block.assign[2]'), defs.MoveAssign, 'ap = (asp).get();'),
		(_ast('CVarOps.local_move.block', 'if_stmt[5].block.assign[3]'), defs.MoveAssign, 'ap = &(ar);'),
		(_ast('CVarOps.local_move.block', 'if_stmt[6].block.assign[2]'), defs.MoveAssign, 'asp = asp;'),

		(_ast('CVarOps.param_move.block', 'assign[0]'), defs.MoveAssign, 'Base a1 = a;'),
		(_ast('CVarOps.param_move.block', 'anno_assign[1]'), defs.AnnoAssign, 'Base a2 = *(ap);'),
		(_ast('CVarOps.param_move.block', 'anno_assign[2]'), defs.AnnoAssign, 'Base a3 = *(asp);'),
		(_ast('CVarOps.param_move.block', 'anno_assign[3]'), defs.AnnoAssign, 'Base a4 = ar;'),
		(_ast('CVarOps.param_move.block', 'assign[4]'), defs.MoveAssign, 'a = a1;'),
		(_ast('CVarOps.param_move.block', 'assign[5]'), defs.MoveAssign, 'ap = &(a2);'),

		(_ast('CVarOps.invoke_method.block', 'funccall[2]'), defs.FuncCall, 'this->invoke_method(*(asp), (asp).get(), asp);'),

		(_ast('FuncOps.print.block', 'funccall'), defs.FuncCall, 'print("%d, %d, %d", 1, 2, 3);'),

		(_ast('AccessOps.Values', ''), defs.Enum, '/** Values */\npublic: enum class Values {\n\tA = 0,\n\tB = 1,\n};'),

		(_ast('AccessOps.__init__', ''), defs.Constructor, '/** Constructor */\npublic: AccessOps() : Base(0), sub_s("") {\n}'),

		(_ast('AccessOps.dot.block', 'funccall[0].arguments.argvalue'), defs.Argument, 'a.base_n'),
		(_ast('AccessOps.dot.block', 'funccall[1].arguments.argvalue'), defs.Argument, 'a.sub_s'),
		(_ast('AccessOps.dot.block', 'funccall[2].arguments.argvalue'), defs.Argument, 'a.call()'),

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
		(_ast('AccessOps.double_colon.block', 'funccall[3].arguments.argvalue'), defs.Argument, 'AccessOps::Values::A'),
		(_ast('AccessOps.double_colon.block', 'anno_assign'), defs.AnnoAssign, 'std::map<AccessOps::Values, std::string> d = {\n\t{AccessOps::Values::A, "A"},\n\t{AccessOps::Values::B, "B"},\n};'),

		(_ast('Alias.Inner', ''), defs.Class, '/** Inner2 */\nclass Inner2 {\n\n};'),
		(_ast('Alias.__init__', ''), defs.Constructor, '/** Constructor */\npublic: Alias2() : inner(Alias2::Inner2()) {\n}'),
		(_ast('Alias.in_param_return', ''), defs.Method, '/** in_param_return */\npublic: Alias2 in_param_return(Alias2 a) {\n\n}'),
		(_ast('Alias.in_param_return2', ''), defs.Method, '/** in_param_return2 */\npublic: Alias2::Inner2 in_param_return2(Alias2::Inner2 i) {\n\n}'),
		(_ast('Alias.in_local.block', 'assign[0]'), defs.MoveAssign, 'Alias2 a = Alias2();'),
		(_ast('Alias.in_local.block', 'assign[1]'), defs.MoveAssign, 'Alias2::Inner2 i = Alias2::Inner2();'),

		(_ast('CompOps.list_comp.block', 'assign[1]'), defs.MoveAssign, BlockExpects.CompOps_list_comp_assign_values1),
		(_ast('CompOps.dict_comp.block', 'assign[1]'), defs.MoveAssign, BlockExpects.CompOps_dict_comp_assign_kvs1),

		(_ast('ForOps.range.block', 'for_stmt'), defs.For, 'for (auto i = 0; i < 10; i++) {\n\tprint(i);\n}'),
		(_ast('ForOps.enumerate.block', 'for_stmt'), defs.For, BlockExpects.ForOps_enumerate_for_index_key),
		(_ast('ForOps.dict_items.block', 'for_stmt'), defs.For, BlockExpects.ForOps_dict_items_for_key_value),

		(_ast('ListOps.len.block', 'assign[1]'), defs.MoveAssign, 'int size_values = values.size();'),
		(_ast('ListOps.pop.block', 'assign[1]'), defs.MoveAssign, BlockExpects.ListOps_pop_assign_value0),
		(_ast('ListOps.pop.block', 'assign[2]'), defs.MoveAssign, BlockExpects.ListOps_pop_assign_value1),

		(_ast('DictOps.len.block', 'assign[1]'), defs.MoveAssign, 'int size_kvs = kvs.size();'),
		(_ast('DictOps.pop.block', 'assign[1]'), defs.MoveAssign, BlockExpects.DictOps_pop_assign_value0),
		(_ast('DictOps.pop.block', 'assign[2]'), defs.MoveAssign, BlockExpects.DictOps_pop_assign_value1),
		(_ast('DictOps.keys.block', 'assign[1]'), defs.MoveAssign, BlockExpects.DictOps_keys_assign_keys),
		(_ast('DictOps.values.block', 'assign[1]'), defs.MoveAssign, BlockExpects.DictOps_values_assign_values),

		(_ast('CastOps.cast.block', 'assign[0]'), defs.MoveAssign, 'int n = (int)(1.0);'),
		(_ast('CastOps.cast.block', 'assign[1]'), defs.MoveAssign, 'float f = (float)(1);'),
		(_ast('CastOps.cast.block', 'assign[2]'), defs.MoveAssign, 'bool b = (bool)(1);'),

		(_ast('import.typing', ''), defs.Import, '// #include "typing.h"'),

		(_ast('DSI', ''), defs.AltClass, 'using DSI = std::map<std::string, int>;'),
	])
	def test_exec(self, full_path: str, expected_type: type[Node], expected: str) -> None:
		translator = self.translator()
		node = self.fixture.shared_nodes.by(full_path).as_a(expected_type)
		actual = translator.exec(node)
		self.assertEqual(actual, expected)

	@data_provider([
		(_ast('CVarOps.local_move.block', 'if_stmt[6].block.assign[0]'), defs.MoveAssign),
		(_ast('CVarOps.local_move.block', 'if_stmt[6].block.assign[1]'), defs.MoveAssign),
		(_ast('CVarOps.local_move.block', 'if_stmt[6].block.assign[3]'), defs.MoveAssign),
		(_ast('CVarOps.local_move.block', 'if_stmt[7].block.assign[0]'), defs.MoveAssign),
		(_ast('CVarOps.local_move.block', 'if_stmt[7].block.assign[1]'), defs.MoveAssign),
		(_ast('CVarOps.local_move.block', 'if_stmt[7].block.assign[2]'), defs.MoveAssign),
		(_ast('CVarOps.local_move.block', 'if_stmt[7].block.assign[3]'), defs.MoveAssign),

		(_ast('CVarOps.param_move.block', 'assign[6]'), defs.MoveAssign),
		(_ast('CVarOps.param_move.block', 'assign[7]'), defs.MoveAssign),

		(_ast('CVarOps.invoke_method.block', 'funccall[0]'), defs.FuncCall),
		(_ast('CVarOps.invoke_method.block', 'funccall[1]'), defs.FuncCall),
	])
	def test_exec_error(self, full_path: str, expected_type: type[Node]) -> None:
		translator = self.translator()
		node = self.fixture.shared_nodes.by(full_path).as_a(expected_type)
		with self.assertRaisesRegex(LogicError, r'^Unacceptable value move.'):
			translator.exec(node)
