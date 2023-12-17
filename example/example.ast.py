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
#                 assign
#                   getattr
#                     primary
#                       var
#                         name	self
#                     name	x
#                   primary
#                     var
#                       name	x
#               assign_stmt
#                 assign
#                   getattr
#                     primary
#                       var
#                         name	self
#                     name	y
#                   primary
#                     var
#                       name	y
#               assign_stmt
#                 assign
#                   getattr
#                     primary
#                       var
#                         name	self
#                     name	z
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
#               primary
#                 atom
#                   string	"""面インデックスからベクトルに変換
# 
# 		Args:
# 			faceIndex (int): 6面インデックス
# 		Returns:
# 			IntVector: ベクトル
# 		"""
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
#                         primary
#                           atom
#                             group_expr
#                               getattr
#                                 primary
#                                   var
#                                     name	CellMesh
#                                 name	FaceIndexs
#                         arguments
#                           argvalue
#                             primary
#                               var
#                                 name	faceIndex
# 