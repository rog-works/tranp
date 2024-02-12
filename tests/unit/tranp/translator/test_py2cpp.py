import os

from unittest import TestCase

from tranp.analyze.symbols import Symbols
from tranp.ast.dsn import DSN
from tranp.errors import LogicError
import tranp.node.definition as defs
from tranp.node.node import Node
from tranp.translator.option import TranslatorOptions
from tranp.translator.py2cpp import Py2Cpp
from tranp.view.render import Renderer
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
		'import.typing': 'file_input.import_stmt[6]',
		'DSI': 'file_input.class_assign',
	}
	return DSN.join(aliases[before], after)


class TestPy2Cpp(TestCase):
	fixture = Fixture.make(__file__)

	def translator(self) -> Py2Cpp:
		renderer = Renderer(os.path.join(Fixture.appdir(), 'example/template'))
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
		# (_ast('AccessOps.double_colon.block', 'anno_assign'), defs.AnnoAssign, 'std::map<AccessOps::Values, std::string> d = {\n\t{AccessOps::Values::A, "A"},\n\t{AccessOps::Values::B, "B"},\n};'),

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
