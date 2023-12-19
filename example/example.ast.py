from lark import Tree, Token
def fixture() -> Tree:
	return Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'py2cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'directive')])]), Tree(Token('RULE', 'import_names'), [Tree(Token('RULE', 'name'), [Token('NAME', 'pragma')])])]), Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'py2cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'enum')])]), Tree(Token('RULE', 'import_names'), [Tree(Token('RULE', 'name'), [Token('NAME', 'CEnum')])])]), Tree('funccall', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'pragma')])])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'string'), [Token('STRING', "'once'")])])])])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', '__init__')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'x')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'y')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'z')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])])]), None])]), Tree(Token('RULE', 'primary'), [Tree('const_none', [])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])])])])])])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', '__init__')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'x')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'y')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'z')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])]), None])]), Tree(Token('RULE', 'primary'), [Tree('const_none', [])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])])])])])])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'enum_def'), [Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Left')])])]), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Right')])])]), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Back')])])]), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Front')])])]), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '3')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Bottom')])])]), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '4')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Top')])])]), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '5')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Max')])])]), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '6')])])])])])])]), Tree(Token('RULE', 'function_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'classmethod')])]), None])]), Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'fromCell')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])]), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '100')])])])])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])]), Tree(Token('RULE', 'term'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])]), Token('STAR', '*'), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])]), Tree(Token('RULE', 'term'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])]), Token('STAR', '*'), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])]), Tree(Token('RULE', 'term'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])]), Token('STAR', '*'), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fx')])])]), Tree('funccall', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fy')])])]), Tree('funccall', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fz')])])]), Tree('funccall', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])])])]), Tree(Token('RULE', 'return_stmt'), [Tree('funccall', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fx')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fy')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fz')])])])])])])])])])]), Tree(Token('RULE', 'function_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'classmethod')])]), None])]), Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'faceIndexToVector')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'faceIndex')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])]), None])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'map')])])]), Tree('getitem', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'dict')])])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])])]), Tree(Token('RULE', 'slice'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])])])])]), Tree(Token('RULE', 'primary'), [Tree('dict', [Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Left')])]), Tree('funccall', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Right')])]), Tree('funccall', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Back')])]), Tree('funccall', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Front')])]), Tree('funccall', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Bottom')])]), Tree('funccall', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Top')])]), Tree('funccall', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])])])])])])])]), Tree(Token('RULE', 'return_stmt'), [Tree('getitem', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'map')])])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('funccall', [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'faceIndex')])])])])])])])])])])])])])])])])])
# ==========
# file_input
#   import_stmt
#     dotted_name
#       name	py2cpp
#       name	cpp
#       name	directive
#     import_names
#       name	pragma
#   import_stmt
#     dotted_name
#       name	py2cpp
#       name	cpp
#       name	enum
#     import_names
#       name	CEnum
#   funccall
#     primary
#       var
#         name	pragma
#     arguments
#       argvalue
#         primary
#           atom
#             string	'once'
#   class_def
#     None
#     class_def_raw
#       name	Vector
#       None
#       block
#         function_def
#           None
#           function_def_raw
#             name	__init__
#             parameters
#               paramvalue
#                 typedparam
#                   name	self
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	x
#                   primary
#                     var
#                       name	float
#                 None
#               paramvalue
#                 typedparam
#                   name	y
#                   primary
#                     var
#                       name	float
#                 None
#               paramvalue
#                 typedparam
#                   name	z
#                   primary
#                     var
#                       name	float
#                 None
#             primary
#               const_none
#             block
#               assign_stmt
#                 anno_assign
#                   getattr
#                     primary
#                       var
#                         name	self
#                     name	x
#                   primary
#                     var
#                       name	float
#                   primary
#                     var
#                       name	x
#               assign_stmt
#                 anno_assign
#                   getattr
#                     primary
#                       var
#                         name	self
#                     name	y
#                   primary
#                     var
#                       name	float
#                   primary
#                     var
#                       name	y
#               assign_stmt
#                 anno_assign
#                   getattr
#                     primary
#                       var
#                         name	self
#                     name	z
#                   primary
#                     var
#                       name	float
#                   primary
#                     var
#                       name	z
#   class_def
#     None
#     class_def_raw
#       name	IntVector
#       None
#       block
#         function_def
#           None
#           function_def_raw
#             name	__init__
#             parameters
#               paramvalue
#                 typedparam
#                   name	self
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	x
#                   primary
#                     var
#                       name	int
#                 None
#               paramvalue
#                 typedparam
#                   name	y
#                   primary
#                     var
#                       name	int
#                 None
#               paramvalue
#                 typedparam
#                   name	z
#                   primary
#                     var
#                       name	int
#                 None
#             primary
#               const_none
#             block
#               assign_stmt
#                 anno_assign
#                   getattr
#                     primary
#                       var
#                         name	self
#                     name	x
#                   primary
#                     var
#                       name	int
#                   primary
#                     var
#                       name	x
#               assign_stmt
#                 anno_assign
#                   getattr
#                     primary
#                       var
#                         name	self
#                     name	y
#                   primary
#                     var
#                       name	int
#                   primary
#                     var
#                       name	y
#               assign_stmt
#                 anno_assign
#                   getattr
#                     primary
#                       var
#                         name	self
#                     name	z
#                   primary
#                     var
#                       name	int
#                   primary
#                     var
#                       name	z
#   class_def
#     None
#     class_def_raw
#       name	CellMesh
#       None
#       block
#         enum_def
#           name	FaceIndexs
#           block
#             assign_stmt
#               assign
#                 primary
#                   var
#                     name	Left
#                 primary
#                   atom
#                     number	0
#             assign_stmt
#               assign
#                 primary
#                   var
#                     name	Right
#                 primary
#                   atom
#                     number	1
#             assign_stmt
#               assign
#                 primary
#                   var
#                     name	Back
#                 primary
#                   atom
#                     number	2
#             assign_stmt
#               assign
#                 primary
#                   var
#                     name	Front
#                 primary
#                   atom
#                     number	3
#             assign_stmt
#               assign
#                 primary
#                   var
#                     name	Bottom
#                 primary
#                   atom
#                     number	4
#             assign_stmt
#               assign
#                 primary
#                   var
#                     name	Top
#                 primary
#                   atom
#                     number	5
#             assign_stmt
#               assign
#                 primary
#                   var
#                     name	Max
#                 primary
#                   atom
#                     number	6
#         function_def
#           decorators
#             decorator
#               dotted_name
#                 name	classmethod
#               None
#           function_def_raw
#             name	fromCell
#             parameters
#               paramvalue
#                 typedparam
#                   name	cls
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	cell
#                   primary
#                     var
#                       name	IntVector
#                 None
#               paramvalue
#                 typedparam
#                   name	unit
#                   primary
#                     var
#                       name	int
#                 primary
#                   atom
#                     number	100
#             primary
#               var
#                 name	Vector
#             block
#               assign_stmt
#                 assign
#                   getattr
#                     primary
#                       var
#                         name	cell
#                     name	x
#                   term
#                     getattr
#                       primary
#                         var
#                           name	cell
#                       name	x
#                     *
#                     primary
#                       var
#                         name	unit
#               assign_stmt
#                 assign
#                   getattr
#                     primary
#                       var
#                         name	cell
#                     name	y
#                   term
#                     getattr
#                       primary
#                         var
#                           name	cell
#                       name	y
#                     *
#                     primary
#                       var
#                         name	unit
#               assign_stmt
#                 assign
#                   getattr
#                     primary
#                       var
#                         name	cell
#                     name	z
#                   term
#                     getattr
#                       primary
#                         var
#                           name	cell
#                       name	z
#                     *
#                     primary
#                       var
#                         name	unit
#               assign_stmt
#                 assign
#                   primary
#                     var
#                       name	fx
#                   funccall
#                     primary
#                       var
#                         name	float
#                     arguments
#                       argvalue
#                         getattr
#                           primary
#                             var
#                               name	cell
#                           name	x
#               assign_stmt
#                 assign
#                   primary
#                     var
#                       name	fy
#                   funccall
#                     primary
#                       var
#                         name	float
#                     arguments
#                       argvalue
#                         getattr
#                           primary
#                             var
#                               name	cell
#                           name	y
#               assign_stmt
#                 assign
#                   primary
#                     var
#                       name	fz
#                   funccall
#                     primary
#                       var
#                         name	float
#                     arguments
#                       argvalue
#                         getattr
#                           primary
#                             var
#                               name	cell
#                           name	z
#               return_stmt
#                 funccall
#                   primary
#                     var
#                       name	Vector
#                   arguments
#                     argvalue
#                       primary
#                         var
#                           name	fx
#                     argvalue
#                       primary
#                         var
#                           name	fy
#                     argvalue
#                       primary
#                         var
#                           name	fz
#         function_def
#           decorators
#             decorator
#               dotted_name
#                 name	classmethod
#               None
#           function_def_raw
#             name	faceIndexToVector
#             parameters
#               paramvalue
#                 typedparam
#                   name	cls
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	faceIndex
#                   primary
#                     var
#                       name	int
#                 None
#             primary
#               var
#                 name	IntVector
#             block
#               assign_stmt
#                 anno_assign
#                   primary
#                     var
#                       name	map
#                   getitem
#                     primary
#                       var
#                         name	dict
#                     slices
#                       slice
#                         getattr
#                           primary
#                             var
#                               name	CellMesh
#                           name	FaceIndexs
#                       slice
#                         primary
#                           var
#                             name	IntVector
#                   primary
#                     dict
#                       key_value
#                         getattr
#                           getattr
#                             primary
#                               var
#                                 name	CellMesh
#                             name	FaceIndexs
#                           name	Left
#                         funccall
#                           primary
#                             var
#                               name	IntVector
#                           arguments
#                             argvalue
#                               factor
#                                 -
#                                 primary
#                                   atom
#                                     number	1
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                       key_value
#                         getattr
#                           getattr
#                             primary
#                               var
#                                 name	CellMesh
#                             name	FaceIndexs
#                           name	Right
#                         funccall
#                           primary
#                             var
#                               name	IntVector
#                           arguments
#                             argvalue
#                               primary
#                                 atom
#                                   number	1
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                       key_value
#                         getattr
#                           getattr
#                             primary
#                               var
#                                 name	CellMesh
#                             name	FaceIndexs
#                           name	Back
#                         funccall
#                           primary
#                             var
#                               name	IntVector
#                           arguments
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                             argvalue
#                               factor
#                                 -
#                                 primary
#                                   atom
#                                     number	1
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                       key_value
#                         getattr
#                           getattr
#                             primary
#                               var
#                                 name	CellMesh
#                             name	FaceIndexs
#                           name	Front
#                         funccall
#                           primary
#                             var
#                               name	IntVector
#                           arguments
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                             argvalue
#                               primary
#                                 atom
#                                   number	1
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                       key_value
#                         getattr
#                           getattr
#                             primary
#                               var
#                                 name	CellMesh
#                             name	FaceIndexs
#                           name	Bottom
#                         funccall
#                           primary
#                             var
#                               name	IntVector
#                           arguments
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                             argvalue
#                               factor
#                                 -
#                                 primary
#                                   atom
#                                     number	1
#                       key_value
#                         getattr
#                           getattr
#                             primary
#                               var
#                                 name	CellMesh
#                             name	FaceIndexs
#                           name	Top
#                         funccall
#                           primary
#                             var
#                               name	IntVector
#                           arguments
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                             argvalue
#                               primary
#                                 atom
#                                   number	0
#                             argvalue
#                               primary
#                                 atom
#                                   number	1
#               return_stmt
#                 getitem
#                   primary
#                     var
#                       name	map
#                   slices
#                     slice
#                       funccall
#                         getattr
#                           primary
#                             var
#                               name	CellMesh
#                           name	FaceIndexs
#                         arguments
#                           argvalue
#                             primary
#                               var
#                                 name	faceIndex
# 