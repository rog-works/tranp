import os

from unittest import TestCase

from py2cpp.analyze.symbols import Symbols
from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
import py2cpp.node.definition as defs
from py2cpp.node.node import Node
from py2cpp.translator.option import TranslatorOptions
from py2cpp.translator.py2cpp import Py2Cpp
from py2cpp.view.render import Renderer
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


def _ast(before: str, after: str) -> str:
	aliases = {
		'CVarCheck.ret_raw.return': 'file_input.class_def[2].class_def_raw.block.function_def[0].function_def_raw.block.return_stmt',
		'CVarCheck.ret_cp.return': 'file_input.class_def[2].class_def_raw.block.function_def[1].function_def_raw.block.return_stmt',
		'CVarCheck.ret_csp.return': 'file_input.class_def[2].class_def_raw.block.function_def[2].function_def_raw.block.return_stmt',
		'CVarCheck.local_move.block': 'file_input.class_def[2].class_def_raw.block.function_def[3].function_def_raw.block',
		'CVarCheck.param_move.block': 'file_input.class_def[2].class_def_raw.block.function_def[4].function_def_raw.block',
		'CVarCheck.invoke_method.block': 'file_input.class_def[2].class_def_raw.block.function_def[5].function_def_raw.block',
	}
	return DSN.join(aliases[before], after)


class TestPy2Cpp(TestCase):
	fixture = Fixture.make(__file__)

	def translator(self) -> Py2Cpp:
		renderer = Renderer(os.path.join(Fixture.appdir(), 'example/template'))
		options = TranslatorOptions(verbose=False)
		return Py2Cpp(self.fixture.get(Symbols), renderer, options)

	@data_provider([
		(_ast('CVarCheck.ret_raw.return', ''), defs.Return, 'return A();'),
		(_ast('CVarCheck.ret_cp.return', ''), defs.Return, 'return new A();'),
		(_ast('CVarCheck.ret_csp.return', ''), defs.Return, 'return std::make_shared<A>();'),

		(_ast('CVarCheck.local_move.block', 'anno_assign[0]'), defs.AnnoAssign, 'A a = A();'),
		(_ast('CVarCheck.local_move.block', 'anno_assign[1]'), defs.AnnoAssign, 'A* ap = &(a);'),
		(_ast('CVarCheck.local_move.block', 'anno_assign[2]'), defs.AnnoAssign, 'std::shared_ptr<A> asp = std::make_shared<A>();'),
		(_ast('CVarCheck.local_move.block', 'anno_assign[3]'), defs.AnnoAssign, 'A& ar = a;'),
		(_ast('CVarCheck.local_move.block', 'if_stmt[4].block.assign[0]'), defs.MoveAssign, 'a = a;'),
		(_ast('CVarCheck.local_move.block', 'if_stmt[4].block.assign[1]'), defs.MoveAssign, 'a = *(ap);'),
		(_ast('CVarCheck.local_move.block', 'if_stmt[4].block.assign[2]'), defs.MoveAssign, 'a = *(asp);'),
		(_ast('CVarCheck.local_move.block', 'if_stmt[4].block.assign[3]'), defs.MoveAssign, 'a = ar;'),
		(_ast('CVarCheck.local_move.block', 'if_stmt[5].block.assign[0]'), defs.MoveAssign, 'ap = &(a);'),
		(_ast('CVarCheck.local_move.block', 'if_stmt[5].block.assign[1]'), defs.MoveAssign, 'ap = ap;'),
		(_ast('CVarCheck.local_move.block', 'if_stmt[5].block.assign[2]'), defs.MoveAssign, 'ap = (asp).get();'),
		(_ast('CVarCheck.local_move.block', 'if_stmt[5].block.assign[3]'), defs.MoveAssign, 'ap = &(ar);'),
		(_ast('CVarCheck.local_move.block', 'if_stmt[6].block.assign[2]'), defs.MoveAssign, 'asp = asp;'),

		(_ast('CVarCheck.param_move.block', 'assign[0]'), defs.MoveAssign, 'A a1 = a;'),
		(_ast('CVarCheck.param_move.block', 'anno_assign[1]'), defs.AnnoAssign, 'A a2 = *(ap);'),
		(_ast('CVarCheck.param_move.block', 'anno_assign[2]'), defs.AnnoAssign, 'A a3 = *(asp);'),
		(_ast('CVarCheck.param_move.block', 'anno_assign[3]'), defs.AnnoAssign, 'A a4 = ar;'),
		(_ast('CVarCheck.param_move.block', 'assign[4]'), defs.MoveAssign, 'a = a1;'),
		(_ast('CVarCheck.param_move.block', 'assign[5]'), defs.MoveAssign, 'ap = &(a2);'),

		(_ast('CVarCheck.invoke_method.block', 'funccall[2]'), defs.FuncCall, 'this->invoke_method(*(asp), (asp).get(), asp);'),
	])
	def test_exec(self, full_path: str, expected_type: type[Node], expected: str) -> None:
		translator = self.translator()
		node = self.fixture.shared_nodes.by(full_path).as_a(expected_type)
		actual = translator.exec(node)
		self.assertEqual(actual, expected)

	@data_provider([
		# (_ast('CVarCheck.local_move.block', 'if_stmt[6].block.assign[0]'), defs.MoveAssign),
		(_ast('CVarCheck.local_move.block', 'if_stmt[6].block.assign[1]'), defs.MoveAssign),
		(_ast('CVarCheck.local_move.block', 'if_stmt[6].block.assign[3]'), defs.MoveAssign),

		(_ast('CVarCheck.param_move.block', 'assign[6]'), defs.MoveAssign),
		(_ast('CVarCheck.param_move.block', 'assign[7]'), defs.MoveAssign),

		(_ast('CVarCheck.invoke_method.block', 'funccall[0]'), defs.FuncCall),
		(_ast('CVarCheck.invoke_method.block', 'funccall[1]'), defs.FuncCall),
	])
	def test_exec_error(self, full_path: str, expected_type: type[Node]) -> None:
		translator = self.translator()
		node = self.fixture.shared_nodes.by(full_path).as_a(expected_type)
		with self.assertRaisesRegex(LogicError, r'^Unacceptable value move.'):
			translator.exec(node)
