from rogw.tranp.implements.syntax.tranp.ast import ASTTree
from rogw.tranp.implements.syntax.tranp.rule import Rules


class TestRules:
	def from_ast(self, tree: ASTTree) -> None:
		rules = Rules.from_ast(tree)
