from lark import Tree, Token
def fixture() -> Tree:
	return Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'py2cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'directive')])]), Tree(Token('RULE', 'import_names'), [Tree(Token('RULE', 'name'), [Token('NAME', 'pragma')])])]), Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'py2cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'enum')])]), Tree(Token('RULE', 'import_names'), [Tree(Token('RULE', 'name'), [Token('NAME', 'CEnum')])])]), Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'FW')]), Tree(Token('RULE', 'name'), [Token('NAME', 'compatible')])]), Tree(Token('RULE', 'import_names'), [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')]), Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')]), Tree(Token('RULE', 'name'), [Token('NAME', 'Mesh')]), Tree(Token('RULE', 'name'), [Token('NAME', 'MeshRaw')])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'pragma')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'string'), [Token('STRING', "'once'")])])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'Box3d')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', '__init__')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'min')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'max')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])])]), None])]), Tree('const_none', []), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])])])])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'contains')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'location')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])])]), None])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'bool')])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'raise_stmt'), [Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'NotImplementedError')])]), None]), None])])])])])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'enum_def'), [Tree(Token('RULE', 'name'), [Token('NAME', 'VertexIndexs')]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'BottomBackLeft')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'BottomBackRight')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'BottomFrontLeft')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'BottomFrontRight')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '3')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'TopBackLeft')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '4')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'TopBackRight')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '5')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'TopFrontLeft')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '6')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'TopFrontRight')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '7')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Max')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '8')])])])])]), Tree(Token('RULE', 'enum_def'), [Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Left')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Right')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Back')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Front')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '3')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Bottom')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '4')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Top')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '5')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Max')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '6')])])])])]), Tree(Token('RULE', 'function_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'classmethod')])]), None])]), Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'from_cell')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '100')])])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])]), Tree(Token('RULE', 'term'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])]), Token('STAR', '*'), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])]), Tree(Token('RULE', 'term'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])]), Token('STAR', '*'), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])]), Tree(Token('RULE', 'term'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])]), Token('STAR', '*'), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fx')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fy')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fz')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])])])]), Tree(Token('RULE', 'return_stmt'), [Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fx')])])]), Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fy')])])]), Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fz')])])])])])])])])]), Tree(Token('RULE', 'function_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'classmethod')])]), None])]), Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'face_index_to_vector')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'faceIndex')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), None])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'map')])]), Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'dict')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])])]), Tree(Token('RULE', 'slice'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])])])]), Tree('dict', [Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Left')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Right')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Back')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Front')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Bottom')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Top')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])])])])]), Tree(Token('RULE', 'return_stmt'), [Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'map')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'faceIndex')])])])])])])])])])])])]), Tree(Token('RULE', 'function_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'classmethod')])]), None])]), Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'to_cell_box')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), None])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Box3d')])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'minLocation')])]), Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'from_cell')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])])]), Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'maxLocation')])]), Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'from_cell')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'sum'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Token('PLUS', '+'), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])])]), Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])])])]), Tree(Token('RULE', 'return_stmt'), [Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Box3d')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'minLocation')])])]), Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'maxLocation')])])])])])])])])]), Tree(Token('RULE', 'function_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'classmethod')])]), None])]), Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'to_vertex_boxs')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cellBox')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Box3d')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), None])]), Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'list')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Box3d')])])])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'offset')])]), Tree(Token('RULE', 'term'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])]), Token('SLASH', '/'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '10')])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cellBox')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'min')])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cellBox')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'max')])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'positions')])]), Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'list')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])])])])]), Tree('list', [Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'min')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'max')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'out')])]), Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'list')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Box3d')])])])])]), Tree('list', [])])]), Tree(Token('RULE', 'for_stmt'), [Tree(Token('RULE', 'name'), [Token('NAME', 'position')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'positions')])]), Tree(Token('RULE', 'block'), [Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'out')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'append')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Box3d')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'sum'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'position')])]), Token('MINUS', '-'), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'offset')])])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'sum'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'position')])]), Token('PLUS', '+'), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'offset')])])])])])])])])])])]), Tree(Token('RULE', 'return_stmt'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'out')])])])])])]), Tree(Token('RULE', 'function_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'classmethod')])]), None])]), Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'by_vertex_ids')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'mesh')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Mesh')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), None])]), Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'list')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'outIds')])]), Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'list')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])])]), Tree('list', [Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'closure')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'origin')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'MeshRaw')])])]), None])]), Tree('const_none', []), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cellBox')])]), Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'to_cell_box')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])])]), Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'boxs')])]), Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'to_vertex_boxs')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cellBox')])])]), Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])])])]), Tree(Token('RULE', 'for_stmt'), [Tree(Token('RULE', 'name'), [Token('NAME', 'i')]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'range')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'VertexIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Max')])])])])])])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'box')])]), Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'boxs')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'i')])])])])])])]), Tree(Token('RULE', 'for_stmt'), [Tree(Token('RULE', 'name'), [Token('NAME', 'vi')]), Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'origin')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'vertex_indices_itr')])]), None]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'if_stmt'), [Tree('not_test', [Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'origin')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'is_vertex')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'vi')])])])])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'continue_stmt'), [])]), Tree(Token('RULE', 'elifs'), []), None]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'origin')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'get_vertex')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'vi')])])])])])])]), Tree(Token('RULE', 'if_stmt'), [Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'box')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'contains')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])])])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'outIds')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'i')])])])])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'vi')])])])]), Tree(Token('RULE', 'break_stmt'), [])]), Tree(Token('RULE', 'elifs'), []), None])])])])])])])]), Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'mesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'process_mesh')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'closure')])])])])]), Tree(Token('RULE', 'return_stmt'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'outIds')])])])])])])])])])])
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
#   import_stmt
#     dotted_name
#       name	FW
#       name	compatible
#     import_names
#       name	IntVector
#       name	Vector
#       name	Mesh
#       name	MeshRaw
#   funccall
#     var
#       name	pragma
#     arguments
#       argvalue
#         string	'once'
#   class_def
#     None
#     class_def_raw
#       name	Box3d
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
#                   name	min
#                   var
#                     name	Vector
#                 None
#               paramvalue
#                 typedparam
#                   name	max
#                   var
#                     name	Vector
#                 None
#             const_none
#             block
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	min
#                   var
#                     name	Vector
#                   var
#                     name	min
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	max
#                   var
#                     name	Vector
#                   var
#                     name	max
#         function_def
#           None
#           function_def_raw
#             name	contains
#             parameters
#               paramvalue
#                 typedparam
#                   name	self
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	location
#                   var
#                     name	Vector
#                 None
#             var
#               name	bool
#             block
#               raise_stmt
#                 funccall
#                   var
#                     name	NotImplementedError
#                   None
#                 None
#   class_def
#     None
#     class_def_raw
#       name	CellMesh
#       None
#       block
#         enum_def
#           name	VertexIndexs
#           block
#             assign_stmt
#               assign
#                 var
#                   name	BottomBackLeft
#                 number	0
#             assign_stmt
#               assign
#                 var
#                   name	BottomBackRight
#                 number	1
#             assign_stmt
#               assign
#                 var
#                   name	BottomFrontLeft
#                 number	2
#             assign_stmt
#               assign
#                 var
#                   name	BottomFrontRight
#                 number	3
#             assign_stmt
#               assign
#                 var
#                   name	TopBackLeft
#                 number	4
#             assign_stmt
#               assign
#                 var
#                   name	TopBackRight
#                 number	5
#             assign_stmt
#               assign
#                 var
#                   name	TopFrontLeft
#                 number	6
#             assign_stmt
#               assign
#                 var
#                   name	TopFrontRight
#                 number	7
#             assign_stmt
#               assign
#                 var
#                   name	Max
#                 number	8
#         enum_def
#           name	FaceIndexs
#           block
#             assign_stmt
#               assign
#                 var
#                   name	Left
#                 number	0
#             assign_stmt
#               assign
#                 var
#                   name	Right
#                 number	1
#             assign_stmt
#               assign
#                 var
#                   name	Back
#                 number	2
#             assign_stmt
#               assign
#                 var
#                   name	Front
#                 number	3
#             assign_stmt
#               assign
#                 var
#                   name	Bottom
#                 number	4
#             assign_stmt
#               assign
#                 var
#                   name	Top
#                 number	5
#             assign_stmt
#               assign
#                 var
#                   name	Max
#                 number	6
#         function_def
#           decorators
#             decorator
#               dotted_name
#                 name	classmethod
#               None
#           function_def_raw
#             name	from_cell
#             parameters
#               paramvalue
#                 typedparam
#                   name	cls
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	cell
#                   var
#                     name	IntVector
#                 None
#               paramvalue
#                 typedparam
#                   name	unit
#                   var
#                     name	int
#                 number	100
#             var
#               name	Vector
#             block
#               assign_stmt
#                 assign
#                   getattr
#                     var
#                       name	cell
#                     name	x
#                   term
#                     getattr
#                       var
#                         name	cell
#                       name	x
#                     *
#                     var
#                       name	unit
#               assign_stmt
#                 assign
#                   getattr
#                     var
#                       name	cell
#                     name	y
#                   term
#                     getattr
#                       var
#                         name	cell
#                       name	y
#                     *
#                     var
#                       name	unit
#               assign_stmt
#                 assign
#                   getattr
#                     var
#                       name	cell
#                     name	z
#                   term
#                     getattr
#                       var
#                         name	cell
#                       name	z
#                     *
#                     var
#                       name	unit
#               assign_stmt
#                 assign
#                   var
#                     name	fx
#                   funccall
#                     var
#                       name	float
#                     arguments
#                       argvalue
#                         getattr
#                           var
#                             name	cell
#                           name	x
#               assign_stmt
#                 assign
#                   var
#                     name	fy
#                   funccall
#                     var
#                       name	float
#                     arguments
#                       argvalue
#                         getattr
#                           var
#                             name	cell
#                           name	y
#               assign_stmt
#                 assign
#                   var
#                     name	fz
#                   funccall
#                     var
#                       name	float
#                     arguments
#                       argvalue
#                         getattr
#                           var
#                             name	cell
#                           name	z
#               return_stmt
#                 funccall
#                   var
#                     name	Vector
#                   arguments
#                     argvalue
#                       var
#                         name	fx
#                     argvalue
#                       var
#                         name	fy
#                     argvalue
#                       var
#                         name	fz
#         function_def
#           decorators
#             decorator
#               dotted_name
#                 name	classmethod
#               None
#           function_def_raw
#             name	face_index_to_vector
#             parameters
#               paramvalue
#                 typedparam
#                   name	cls
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	faceIndex
#                   var
#                     name	int
#                 None
#             var
#               name	IntVector
#             block
#               assign_stmt
#                 anno_assign
#                   var
#                     name	map
#                   getitem
#                     var
#                       name	dict
#                     slices
#                       slice
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                       slice
#                         var
#                           name	IntVector
#                   dict
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Left
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             factor
#                               -
#                               number	1
#                           argvalue
#                             number	0
#                           argvalue
#                             number	0
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Right
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             number	1
#                           argvalue
#                             number	0
#                           argvalue
#                             number	0
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Back
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             number	0
#                           argvalue
#                             factor
#                               -
#                               number	1
#                           argvalue
#                             number	0
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Front
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             number	0
#                           argvalue
#                             number	1
#                           argvalue
#                             number	0
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Bottom
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             number	0
#                           argvalue
#                             number	0
#                           argvalue
#                             factor
#                               -
#                               number	1
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Top
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             number	0
#                           argvalue
#                             number	0
#                           argvalue
#                             number	1
#               return_stmt
#                 getitem
#                   var
#                     name	map
#                   slices
#                     slice
#                       funccall
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         arguments
#                           argvalue
#                             var
#                               name	faceIndex
#         function_def
#           decorators
#             decorator
#               dotted_name
#                 name	classmethod
#               None
#           function_def_raw
#             name	to_cell_box
#             parameters
#               paramvalue
#                 typedparam
#                   name	cls
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	cell
#                   var
#                     name	IntVector
#                 None
#               paramvalue
#                 typedparam
#                   name	unit
#                   var
#                     name	int
#                 None
#             var
#               name	Box3d
#             block
#               assign_stmt
#                 assign
#                   var
#                     name	minLocation
#                   funccall
#                     getattr
#                       var
#                         name	cls
#                       name	from_cell
#                     arguments
#                       argvalue
#                         var
#                           name	cell
#                       argvalue
#                         var
#                           name	unit
#               assign_stmt
#                 assign
#                   var
#                     name	maxLocation
#                   funccall
#                     getattr
#                       var
#                         name	cls
#                       name	from_cell
#                     arguments
#                       argvalue
#                         sum
#                           var
#                             name	cell
#                           +
#                           funccall
#                             var
#                               name	IntVector
#                             arguments
#                               argvalue
#                                 number	1
#                               argvalue
#                                 number	1
#                               argvalue
#                                 number	1
#                       argvalue
#                         var
#                           name	unit
#               return_stmt
#                 funccall
#                   var
#                     name	Box3d
#                   arguments
#                     argvalue
#                       var
#                         name	minLocation
#                     argvalue
#                       var
#                         name	maxLocation
#         function_def
#           decorators
#             decorator
#               dotted_name
#                 name	classmethod
#               None
#           function_def_raw
#             name	to_vertex_boxs
#             parameters
#               paramvalue
#                 typedparam
#                   name	cls
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	cellBox
#                   var
#                     name	Box3d
#                 None
#               paramvalue
#                 typedparam
#                   name	unit
#                   var
#                     name	int
#                 None
#             getitem
#               var
#                 name	list
#               slices
#                 slice
#                   var
#                     name	Box3d
#             block
#               assign_stmt
#                 assign
#                   var
#                     name	offset
#                   term
#                     var
#                       name	unit
#                     /
#                     number	10
#               assign_stmt
#                 assign
#                   var
#                     name	min
#                   getattr
#                     var
#                       name	cellBox
#                     name	min
#               assign_stmt
#                 assign
#                   var
#                     name	max
#                   getattr
#                     var
#                       name	cellBox
#                     name	max
#               assign_stmt
#                 anno_assign
#                   var
#                     name	positions
#                   getitem
#                     var
#                       name	list
#                     slices
#                       slice
#                         var
#                           name	Vector
#                   list
#                     funccall
#                       var
#                         name	Vector
#                       arguments
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	x
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	y
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	z
#                     funccall
#                       var
#                         name	Vector
#                       arguments
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	x
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	y
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	z
#                     funccall
#                       var
#                         name	Vector
#                       arguments
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	x
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	y
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	z
#                     funccall
#                       var
#                         name	Vector
#                       arguments
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	x
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	y
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	z
#                     funccall
#                       var
#                         name	Vector
#                       arguments
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	x
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	y
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	z
#                     funccall
#                       var
#                         name	Vector
#                       arguments
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	x
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	y
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	z
#                     funccall
#                       var
#                         name	Vector
#                       arguments
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	x
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	y
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	z
#                     funccall
#                       var
#                         name	Vector
#                       arguments
#                         argvalue
#                           getattr
#                             var
#                               name	min
#                             name	x
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	y
#                         argvalue
#                           getattr
#                             var
#                               name	max
#                             name	z
#               assign_stmt
#                 anno_assign
#                   var
#                     name	out
#                   getitem
#                     var
#                       name	list
#                     slices
#                       slice
#                         var
#                           name	Box3d
#                   list
#               for_stmt
#                 name	position
#                 var
#                   name	positions
#                 block
#                   funccall
#                     getattr
#                       var
#                         name	out
#                       name	append
#                     arguments
#                       argvalue
#                         funccall
#                           var
#                             name	Box3d
#                           arguments
#                             argvalue
#                               sum
#                                 var
#                                   name	position
#                                 -
#                                 var
#                                   name	offset
#                             argvalue
#                               sum
#                                 var
#                                   name	position
#                                 +
#                                 var
#                                   name	offset
#               return_stmt
#                 var
#                   name	out
#         function_def
#           decorators
#             decorator
#               dotted_name
#                 name	classmethod
#               None
#           function_def_raw
#             name	by_vertex_ids
#             parameters
#               paramvalue
#                 typedparam
#                   name	cls
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	mesh
#                   var
#                     name	Mesh
#                 None
#               paramvalue
#                 typedparam
#                   name	cell
#                   var
#                     name	IntVector
#                 None
#               paramvalue
#                 typedparam
#                   name	unit
#                   var
#                     name	int
#                 None
#             getitem
#               var
#                 name	list
#               slices
#                 slice
#                   var
#                     name	int
#             block
#               assign_stmt
#                 anno_assign
#                   var
#                     name	outIds
#                   getitem
#                     var
#                       name	list
#                     slices
#                       slice
#                         var
#                           name	int
#                   list
#                     factor
#                       -
#                       number	1
#                     factor
#                       -
#                       number	1
#                     factor
#                       -
#                       number	1
#                     factor
#                       -
#                       number	1
#                     factor
#                       -
#                       number	1
#                     factor
#                       -
#                       number	1
#                     factor
#                       -
#                       number	1
#                     factor
#                       -
#                       number	1
#               function_def
#                 None
#                 function_def_raw
#                   name	closure
#                   parameters
#                     paramvalue
#                       typedparam
#                         name	origin
#                         var
#                           name	MeshRaw
#                       None
#                   const_none
#                   block
#                     assign_stmt
#                       assign
#                         var
#                           name	cellBox
#                         funccall
#                           getattr
#                             var
#                               name	cls
#                             name	to_cell_box
#                           arguments
#                             argvalue
#                               var
#                                 name	cell
#                             argvalue
#                               var
#                                 name	unit
#                     assign_stmt
#                       assign
#                         var
#                           name	boxs
#                         funccall
#                           getattr
#                             var
#                               name	cls
#                             name	to_vertex_boxs
#                           arguments
#                             argvalue
#                               var
#                                 name	cellBox
#                             argvalue
#                               var
#                                 name	unit
#                     for_stmt
#                       name	i
#                       funccall
#                         var
#                           name	range
#                         arguments
#                           argvalue
#                             funccall
#                               var
#                                 name	int
#                               arguments
#                                 argvalue
#                                   getattr
#                                     getattr
#                                       var
#                                         name	CellMesh
#                                       name	VertexIndexs
#                                     name	Max
#                       block
#                         assign_stmt
#                           assign
#                             var
#                               name	box
#                             getitem
#                               var
#                                 name	boxs
#                               slices
#                                 slice
#                                   var
#                                     name	i
#                         for_stmt
#                           name	vi
#                           funccall
#                             getattr
#                               var
#                                 name	origin
#                               name	vertex_indices_itr
#                             None
#                           block
#                             if_stmt
#                               not_test
#                                 funccall
#                                   getattr
#                                     var
#                                       name	origin
#                                     name	is_vertex
#                                   arguments
#                                     argvalue
#                                       var
#                                         name	vi
#                               block
#                                 continue_stmt
#                               elifs
#                               None
#                             assign_stmt
#                               assign
#                                 var
#                                   name	v
#                                 funccall
#                                   getattr
#                                     var
#                                       name	origin
#                                     name	get_vertex
#                                   arguments
#                                     argvalue
#                                       var
#                                         name	vi
#                             if_stmt
#                               funccall
#                                 getattr
#                                   var
#                                     name	box
#                                   name	contains
#                                 arguments
#                                   argvalue
#                                     var
#                                       name	v
#                               block
#                                 assign_stmt
#                                   assign
#                                     getitem
#                                       var
#                                         name	outIds
#                                       slices
#                                         slice
#                                           var
#                                             name	i
#                                     var
#                                       name	vi
#                                 break_stmt
#                               elifs
#                               None
#               funccall
#                 getattr
#                   var
#                     name	mesh
#                   name	process_mesh
#                 arguments
#                   argvalue
#                     var
#                       name	closure
#               return_stmt
#                 var
#                   name	outIds
# 