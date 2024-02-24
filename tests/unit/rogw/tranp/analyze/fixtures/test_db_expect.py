def expected_symbols() -> dict:
	return {
		'__main__.TypeAlias': 'typing.TypeAlias',
		'__main__.CEnum': 'rogw.tranp.compatible.cpp.enum.CEnum',
		'__main__.Z': 'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.Z',
		'__main__.DSI': '__main__.DSI',
		'__main__.DSI2': '__main__.DSI2',
		'__main__.Z2': '__main__.Z2',
		'__main__.Base': '__main__.Base',
		'__main__.Base.__init__': '__main__.Base.__init__',
		'__main__.Sub': '__main__.Sub',
		'__main__.Sub.C': '__main__.Sub.C',
		'__main__.Sub.C.class_func': '__main__.Sub.C.class_func',
		'__main__.Sub.__init__': '__main__.Sub.__init__',
		'__main__.Sub.local_ref': '__main__.Sub.local_ref',
		'__main__.Sub.member_ref': '__main__.Sub.member_ref',
		'__main__.Sub.member_write': '__main__.Sub.member_write',
		'__main__.Sub.param_ref': '__main__.Sub.param_ref',
		'__main__.Sub.list_ref': '__main__.Sub.list_ref',
		'__main__.Sub.base_ref': '__main__.Sub.base_ref',
		'__main__.Sub.returns': '__main__.Sub.returns',
		'__main__.Sub.invoke_method': '__main__.Sub.invoke_method',
		'__main__.Sub.decl_with_pop': '__main__.Sub.decl_with_pop',
		'__main__.Sub.decl_locals': '__main__.Sub.decl_locals',
		'__main__.Sub.decl_locals.closure': '__main__.Sub.decl_locals.closure',
		'__main__.Sub.assign_with_param': '__main__.Sub.assign_with_param',
		'__main__.Ops': '__main__.Ops',
		'__main__.Ops.sum': '__main__.Ops.sum',
		'__main__.AliasOps': '__main__.AliasOps',
		'__main__.AliasOps.func': '__main__.AliasOps.func',
		'__main__.TupleOps': '__main__.TupleOps',
		'__main__.TupleOps.unpack': '__main__.TupleOps.unpack',
		'__main__.TupleOps.unpack_assign': '__main__.TupleOps.unpack_assign',
		'__main__.CompOps': '__main__.CompOps',
		'__main__.CompOps.list_comp': '__main__.CompOps.list_comp',
		'__main__.CompOps.dict_comp': '__main__.CompOps.dict_comp',
		'__main__.EnumOps': '__main__.EnumOps',
		'__main__.EnumOps.Values': '__main__.EnumOps.Values',
		'__main__.EnumOps.assign': '__main__.EnumOps.assign',
		'__main__.value': 'rogw.tranp.compatible.python.classes.int',
		'__main__.Base.base_str': 'rogw.tranp.compatible.python.classes.str',
		'__main__.Base.__init__.self': '__main__.Base',
		'__main__.Sub.numbers': 'rogw.tranp.compatible.python.classes.list',
		'__main__.Sub.C.value': 'rogw.tranp.compatible.python.classes.str',
		'__main__.Sub.C.class_func.cls': '__main__.Sub.C',
		'__main__.Sub.__init__.self': '__main__.Sub',
		'__main__.Sub.local_ref.self': '__main__.Sub',
		'__main__.Sub.local_ref.value': 'rogw.tranp.compatible.python.classes.bool',
		'__main__.Sub.member_ref.self': '__main__.Sub',
		'__main__.Sub.member_write.self': '__main__.Sub',
		'__main__.Sub.param_ref.self': '__main__.Sub',
		'__main__.Sub.param_ref.param': 'rogw.tranp.compatible.python.classes.int',
		'__main__.Sub.list_ref.self': '__main__.Sub',
		'__main__.Sub.list_ref.subs': 'rogw.tranp.compatible.python.classes.list',
		'__main__.Sub.base_ref.self': '__main__.Sub',
		'__main__.Sub.returns.self': '__main__.Sub',
		'__main__.Sub.invoke_method.self': '__main__.Sub',
		'__main__.Sub.decl_with_pop.self': '__main__.Sub',
		'__main__.Sub.decl_with_pop.poped': 'rogw.tranp.compatible.python.classes.int',
		'__main__.Sub.decl_locals.self': '__main__.Sub',
		'__main__.Sub.decl_locals.a': 'rogw.tranp.compatible.python.classes.int',
		'__main__.Sub.decl_locals.if.for.i': 'rogw.tranp.compatible.python.classes.int',
		'__main__.Sub.decl_locals.if.for.try.e': 'rogw.tranp.compatible.python.classes.Exception',
		'__main__.Sub.decl_locals.closure.b': 'rogw.tranp.compatible.python.classes.list',
		'__main__.Sub.assign_with_param.self': '__main__.Sub',
		'__main__.Sub.assign_with_param.a': 'rogw.tranp.compatible.python.classes.int',
		'__main__.Sub.assign_with_param.a1': 'rogw.tranp.compatible.python.classes.int',
		'__main__.Ops.sum.self': '__main__.Ops',
		'__main__.Ops.sum.n': 'rogw.tranp.compatible.python.classes.int',
		'__main__.Ops.sum.nb0': 'rogw.tranp.compatible.python.classes.int',
		'__main__.Ops.sum.nb1': 'rogw.tranp.compatible.python.classes.int',
		'__main__.Ops.sum.fn0': 'rogw.tranp.compatible.python.classes.float',
		'__main__.Ops.sum.fn1': 'rogw.tranp.compatible.python.classes.float',
		'__main__.Ops.sum.fn2': 'rogw.tranp.compatible.python.classes.float',
		'__main__.Ops.sum.fb0': 'rogw.tranp.compatible.python.classes.float',
		'__main__.Ops.sum.fb1': 'rogw.tranp.compatible.python.classes.float',
		'__main__.AliasOps.func.self': '__main__.AliasOps',
		'__main__.AliasOps.func.z2': '__main__.Z2',
		'__main__.AliasOps.func.d': '__main__.DSI',
		'__main__.AliasOps.func.d_in_v': 'rogw.tranp.compatible.python.classes.int',
		'__main__.AliasOps.func.d2': '__main__.DSI2',
		'__main__.AliasOps.func.d2_in_dsi': '__main__.DSI',
		'__main__.AliasOps.func.d2_in_dsi_in_v': 'rogw.tranp.compatible.python.classes.int',
		'__main__.AliasOps.func.z2_in_x': 'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.X',
		'__main__.AliasOps.func.new_z2_in_x': 'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.X',
		'__main__.TupleOps.unpack.self': '__main__.TupleOps',
		'__main__.TupleOps.unpack.for.key0': 'rogw.tranp.compatible.python.classes.str',
		'__main__.TupleOps.unpack.for.value0': 'rogw.tranp.compatible.python.classes.int',
		'__main__.TupleOps.unpack.for.value1': 'rogw.tranp.compatible.python.classes.int',
		'__main__.TupleOps.unpack.for.key1': 'rogw.tranp.compatible.python.classes.str',
		'__main__.TupleOps.unpack.for.pair0': 'rogw.tranp.compatible.python.classes.Pair',
		'__main__.TupleOps.unpack.d': '__main__.DSI2',
		'__main__.TupleOps.unpack.for.key10': 'rogw.tranp.compatible.python.classes.str',
		'__main__.TupleOps.unpack.for.value10': '__main__.DSI',
		'__main__.TupleOps.unpack.for.value11': '__main__.DSI',
		'__main__.TupleOps.unpack.for.key11': 'rogw.tranp.compatible.python.classes.str',
		'__main__.TupleOps.unpack.for.pair10': 'rogw.tranp.compatible.python.classes.Pair',
		'__main__.TupleOps.unpack_assign.self': '__main__.TupleOps',
		'__main__.TupleOps.unpack_assign.a': 'rogw.tranp.compatible.python.classes.str',
		'__main__.TupleOps.unpack_assign.b': 'rogw.tranp.compatible.python.classes.int',
		'__main__.CompOps.list_comp.self': '__main__.CompOps',
		'__main__.CompOps.list_comp.values0': 'rogw.tranp.compatible.python.classes.list',
		'__main__.CompOps.list_comp.values1': 'rogw.tranp.compatible.python.classes.list',
		'__main__.CompOps.list_comp.values2': 'rogw.tranp.compatible.python.classes.list',
		'__main__.CompOps.list_comp.strs': 'rogw.tranp.compatible.python.classes.list',
		'__main__.CompOps.list_comp.value': 'rogw.tranp.compatible.python.classes.int',
		'__main__.CompOps.list_comp.list_comp@1154.value': 'rogw.tranp.compatible.python.classes.int',
		'__main__.CompOps.list_comp.list_comp@1186.value': 'rogw.tranp.compatible.python.classes.int',
		'__main__.CompOps.list_comp.list_comp@1210.value': 'rogw.tranp.compatible.python.classes.int',
		'__main__.CompOps.list_comp.list_comp@1230.value': 'rogw.tranp.compatible.python.classes.int',
		'__main__.CompOps.list_comp.list_comp@1275.value': 'rogw.tranp.compatible.python.classes.float',
		'__main__.CompOps.dict_comp.self': '__main__.CompOps',
		'__main__.CompOps.dict_comp.kvs0': 'rogw.tranp.compatible.python.classes.dict',
		'__main__.CompOps.dict_comp.kvs1': 'rogw.tranp.compatible.python.classes.dict',
		'__main__.CompOps.dict_comp.kvs2': 'rogw.tranp.compatible.python.classes.dict',
		'__main__.CompOps.dict_comp.dict_comp@1315.index': 'rogw.tranp.compatible.python.classes.int',
		'__main__.CompOps.dict_comp.dict_comp@1315.key': 'rogw.tranp.compatible.python.classes.str',
		'__main__.CompOps.dict_comp.dict_comp@1362.index': 'rogw.tranp.compatible.python.classes.int',
		'__main__.CompOps.dict_comp.dict_comp@1362.key': 'rogw.tranp.compatible.python.classes.str',
		'__main__.CompOps.dict_comp.dict_comp@1398.key': 'rogw.tranp.compatible.python.classes.str',
		'__main__.CompOps.dict_comp.dict_comp@1398.index': 'rogw.tranp.compatible.python.classes.int',
		'__main__.EnumOps.Values.A': 'rogw.tranp.compatible.python.classes.int',
		'__main__.EnumOps.Values.B': 'rogw.tranp.compatible.python.classes.int',
		'__main__.EnumOps.assign.self': '__main__.EnumOps',
		'__main__.EnumOps.assign.a': '__main__.EnumOps.Values',
		'__main__.EnumOps.assign.d': 'rogw.tranp.compatible.python.classes.dict',
		'__main__.EnumOps.assign.da': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.Union': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.Unknown': 'rogw.tranp.compatible.python.classes.Unknown',
		'rogw.tranp.compatible.python.classes.int': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.float': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.str': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.bool': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.tuple': 'rogw.tranp.compatible.python.classes.tuple',
		'rogw.tranp.compatible.python.classes.Pair': 'rogw.tranp.compatible.python.classes.Pair',
		'rogw.tranp.compatible.python.classes.list': 'rogw.tranp.compatible.python.classes.list',
		'rogw.tranp.compatible.python.classes.dict': 'rogw.tranp.compatible.python.classes.dict',
		'rogw.tranp.compatible.python.classes.None': 'rogw.tranp.compatible.python.classes.None',
		'rogw.tranp.compatible.python.classes.object': 'rogw.tranp.compatible.python.classes.object',
		'rogw.tranp.compatible.python.classes.type': 'rogw.tranp.compatible.python.classes.type',
		'rogw.tranp.compatible.python.classes.super': 'rogw.tranp.compatible.python.classes.super',
		'rogw.tranp.compatible.python.classes.Exception': 'rogw.tranp.compatible.python.classes.Exception',
		'rogw.tranp.compatible.python.classes.id': 'rogw.tranp.compatible.python.classes.id',
		'rogw.tranp.compatible.python.classes.print': 'rogw.tranp.compatible.python.classes.print',
		'rogw.tranp.compatible.python.classes.enumerate': 'rogw.tranp.compatible.python.classes.enumerate',
		'rogw.tranp.compatible.python.classes.range': 'rogw.tranp.compatible.python.classes.range',
		'rogw.tranp.compatible.python.classes.len': 'rogw.tranp.compatible.python.classes.len',
		'rogw.tranp.compatible.python.classes.Any': 'typing.Any',
		'rogw.tranp.compatible.python.classes.Generic': 'typing.Generic',
		'rogw.tranp.compatible.python.classes.Iterator': 'typing.Iterator',
		'rogw.tranp.compatible.python.classes.Sequence': 'typing.Sequence',
		'rogw.tranp.compatible.python.classes.__actual__': 'rogw.tranp.compatible.python.embed.__actual__',
		'rogw.tranp.compatible.python.classes.__alias__': 'rogw.tranp.compatible.python.embed.__alias__',
		'rogw.tranp.compatible.python.classes.T_Seq': 'rogw.tranp.compatible.python.template.T_Seq',
		'rogw.tranp.compatible.python.classes.T_Key': 'rogw.tranp.compatible.python.template.T_Key',
		'rogw.tranp.compatible.python.classes.int.__init__': 'rogw.tranp.compatible.python.classes.int.__init__',
		'rogw.tranp.compatible.python.classes.int.__eq__': 'rogw.tranp.compatible.python.classes.int.__eq__',
		'rogw.tranp.compatible.python.classes.int.__ne__': 'rogw.tranp.compatible.python.classes.int.__ne__',
		'rogw.tranp.compatible.python.classes.int.__lt__': 'rogw.tranp.compatible.python.classes.int.__lt__',
		'rogw.tranp.compatible.python.classes.int.__gt__': 'rogw.tranp.compatible.python.classes.int.__gt__',
		'rogw.tranp.compatible.python.classes.int.__not__': 'rogw.tranp.compatible.python.classes.int.__not__',
		'rogw.tranp.compatible.python.classes.int.__add__': 'rogw.tranp.compatible.python.classes.int.__add__',
		'rogw.tranp.compatible.python.classes.int.__sub__': 'rogw.tranp.compatible.python.classes.int.__sub__',
		'rogw.tranp.compatible.python.classes.int.__mul__': 'rogw.tranp.compatible.python.classes.int.__mul__',
		'rogw.tranp.compatible.python.classes.int.__truediv__': 'rogw.tranp.compatible.python.classes.int.__truediv__',
		'rogw.tranp.compatible.python.classes.int.__mod__': 'rogw.tranp.compatible.python.classes.int.__mod__',
		'rogw.tranp.compatible.python.classes.int.__and__': 'rogw.tranp.compatible.python.classes.int.__and__',
		'rogw.tranp.compatible.python.classes.int.__or__': 'rogw.tranp.compatible.python.classes.int.__or__',
		'rogw.tranp.compatible.python.classes.int.__int__': 'rogw.tranp.compatible.python.classes.int.__int__',
		'rogw.tranp.compatible.python.classes.int.__float__': 'rogw.tranp.compatible.python.classes.int.__float__',
		'rogw.tranp.compatible.python.classes.int.__str__': 'rogw.tranp.compatible.python.classes.int.__str__',
		'rogw.tranp.compatible.python.classes.float.__init__': 'rogw.tranp.compatible.python.classes.float.__init__',
		'rogw.tranp.compatible.python.classes.float.__eq__': 'rogw.tranp.compatible.python.classes.float.__eq__',
		'rogw.tranp.compatible.python.classes.float.__ne__': 'rogw.tranp.compatible.python.classes.float.__ne__',
		'rogw.tranp.compatible.python.classes.float.__lt__': 'rogw.tranp.compatible.python.classes.float.__lt__',
		'rogw.tranp.compatible.python.classes.float.__gt__': 'rogw.tranp.compatible.python.classes.float.__gt__',
		'rogw.tranp.compatible.python.classes.float.__not__': 'rogw.tranp.compatible.python.classes.float.__not__',
		'rogw.tranp.compatible.python.classes.float.__add__': 'rogw.tranp.compatible.python.classes.float.__add__',
		'rogw.tranp.compatible.python.classes.float.__sub__': 'rogw.tranp.compatible.python.classes.float.__sub__',
		'rogw.tranp.compatible.python.classes.float.__mul__': 'rogw.tranp.compatible.python.classes.float.__mul__',
		'rogw.tranp.compatible.python.classes.float.__truediv__': 'rogw.tranp.compatible.python.classes.float.__truediv__',
		'rogw.tranp.compatible.python.classes.float.__int__': 'rogw.tranp.compatible.python.classes.float.__int__',
		'rogw.tranp.compatible.python.classes.float.__float__': 'rogw.tranp.compatible.python.classes.float.__float__',
		'rogw.tranp.compatible.python.classes.float.__str__': 'rogw.tranp.compatible.python.classes.float.__str__',
		'rogw.tranp.compatible.python.classes.str.__init__': 'rogw.tranp.compatible.python.classes.str.__init__',
		'rogw.tranp.compatible.python.classes.str.split': 'rogw.tranp.compatible.python.classes.str.split',
		'rogw.tranp.compatible.python.classes.str.join': 'rogw.tranp.compatible.python.classes.str.join',
		'rogw.tranp.compatible.python.classes.str.replace': 'rogw.tranp.compatible.python.classes.str.replace',
		'rogw.tranp.compatible.python.classes.str.find': 'rogw.tranp.compatible.python.classes.str.find',
		'rogw.tranp.compatible.python.classes.str.__eq__': 'rogw.tranp.compatible.python.classes.str.__eq__',
		'rogw.tranp.compatible.python.classes.str.__ne__': 'rogw.tranp.compatible.python.classes.str.__ne__',
		'rogw.tranp.compatible.python.classes.str.__lt__': 'rogw.tranp.compatible.python.classes.str.__lt__',
		'rogw.tranp.compatible.python.classes.str.__gt__': 'rogw.tranp.compatible.python.classes.str.__gt__',
		'rogw.tranp.compatible.python.classes.str.__not__': 'rogw.tranp.compatible.python.classes.str.__not__',
		'rogw.tranp.compatible.python.classes.str.__add__': 'rogw.tranp.compatible.python.classes.str.__add__',
		'rogw.tranp.compatible.python.classes.str.__mul__': 'rogw.tranp.compatible.python.classes.str.__mul__',
		'rogw.tranp.compatible.python.classes.str.__int__': 'rogw.tranp.compatible.python.classes.str.__int__',
		'rogw.tranp.compatible.python.classes.str.__float__': 'rogw.tranp.compatible.python.classes.str.__float__',
		'rogw.tranp.compatible.python.classes.str.__str__': 'rogw.tranp.compatible.python.classes.str.__str__',
		'rogw.tranp.compatible.python.classes.bool.__init__': 'rogw.tranp.compatible.python.classes.bool.__init__',
		'rogw.tranp.compatible.python.classes.bool.__eq__': 'rogw.tranp.compatible.python.classes.bool.__eq__',
		'rogw.tranp.compatible.python.classes.bool.__ne__': 'rogw.tranp.compatible.python.classes.bool.__ne__',
		'rogw.tranp.compatible.python.classes.bool.__lt__': 'rogw.tranp.compatible.python.classes.bool.__lt__',
		'rogw.tranp.compatible.python.classes.bool.__gt__': 'rogw.tranp.compatible.python.classes.bool.__gt__',
		'rogw.tranp.compatible.python.classes.bool.__not__': 'rogw.tranp.compatible.python.classes.bool.__not__',
		'rogw.tranp.compatible.python.classes.bool.__add__': 'rogw.tranp.compatible.python.classes.bool.__add__',
		'rogw.tranp.compatible.python.classes.bool.__sub__': 'rogw.tranp.compatible.python.classes.bool.__sub__',
		'rogw.tranp.compatible.python.classes.bool.__mul__': 'rogw.tranp.compatible.python.classes.bool.__mul__',
		'rogw.tranp.compatible.python.classes.bool.__truediv__': 'rogw.tranp.compatible.python.classes.bool.__truediv__',
		'rogw.tranp.compatible.python.classes.bool.__mod__': 'rogw.tranp.compatible.python.classes.bool.__mod__',
		'rogw.tranp.compatible.python.classes.bool.__int__': 'rogw.tranp.compatible.python.classes.bool.__int__',
		'rogw.tranp.compatible.python.classes.bool.__float__': 'rogw.tranp.compatible.python.classes.bool.__float__',
		'rogw.tranp.compatible.python.classes.bool.__str__': 'rogw.tranp.compatible.python.classes.bool.__str__',
		'rogw.tranp.compatible.python.classes.list.__init__': 'rogw.tranp.compatible.python.classes.list.__init__',
		'rogw.tranp.compatible.python.classes.list.__iter__': 'rogw.tranp.compatible.python.classes.list.__iter__',
		'rogw.tranp.compatible.python.classes.list.__contains__': 'rogw.tranp.compatible.python.classes.list.__contains__',
		'rogw.tranp.compatible.python.classes.list.append': 'rogw.tranp.compatible.python.classes.list.append',
		'rogw.tranp.compatible.python.classes.list.pop': 'rogw.tranp.compatible.python.classes.list.pop',
		'rogw.tranp.compatible.python.classes.dict.__init__': 'rogw.tranp.compatible.python.classes.dict.__init__',
		'rogw.tranp.compatible.python.classes.dict.__iter__': 'rogw.tranp.compatible.python.classes.dict.__iter__',
		'rogw.tranp.compatible.python.classes.dict.__contains__': 'rogw.tranp.compatible.python.classes.dict.__contains__',
		'rogw.tranp.compatible.python.classes.dict.keys': 'rogw.tranp.compatible.python.classes.dict.keys',
		'rogw.tranp.compatible.python.classes.dict.values': 'rogw.tranp.compatible.python.classes.dict.values',
		'rogw.tranp.compatible.python.classes.dict.items': 'rogw.tranp.compatible.python.classes.dict.items',
		'rogw.tranp.compatible.python.classes.dict.pop': 'rogw.tranp.compatible.python.classes.dict.pop',
		'rogw.tranp.compatible.python.classes.object.__init__': 'rogw.tranp.compatible.python.classes.object.__init__',
		'rogw.tranp.compatible.python.classes.Exception.__init__': 'rogw.tranp.compatible.python.classes.Exception.__init__',
		'rogw.tranp.compatible.python.classes.int.__init__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__init__.value': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__eq__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__eq__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__ne__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__ne__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__lt__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__lt__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__gt__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__gt__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__not__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__not__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__add__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__add__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__sub__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__sub__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__mul__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__mul__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__truediv__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__truediv__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__mod__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__mod__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__and__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__and__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__or__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__or__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.int.__int__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__float__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.int.__str__.self': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.float.__init__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__init__.value': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.float.__eq__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__eq__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.float.__ne__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__ne__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.float.__lt__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__lt__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.float.__gt__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__gt__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.float.__not__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__not__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.float.__add__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__add__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.float.__sub__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__sub__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.float.__mul__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__mul__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.float.__truediv__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__truediv__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.float.__int__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__float__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.float.__str__.self': 'rogw.tranp.compatible.python.classes.float',
		'rogw.tranp.compatible.python.classes.str.__init__.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__init__.value': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.str.split.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.split.delimiter': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.join.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.join.iterable': 'typing.Iterator',
		'rogw.tranp.compatible.python.classes.str.replace.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.replace.subject': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.replace.replaced': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.find.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.find.subject': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__eq__.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__eq__.other': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__ne__.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__ne__.other': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__lt__.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__lt__.other': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__gt__.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__gt__.other': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__not__.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__not__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.str.__add__.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__add__.other': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__mul__.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__mul__.other': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.str.__int__.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__float__.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.str.__str__.self': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.classes.bool.__init__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__init__.value': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.bool.__eq__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__eq__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.bool.__ne__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__ne__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.bool.__lt__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__lt__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.bool.__gt__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__gt__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.bool.__not__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__not__.other': 'rogw.tranp.compatible.python.classes.Union',
		'rogw.tranp.compatible.python.classes.bool.__add__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__add__.other': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__sub__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__sub__.other': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__mul__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__mul__.other': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__truediv__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__truediv__.other': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__mod__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__mod__.other': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__int__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__float__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.bool.__str__.self': 'rogw.tranp.compatible.python.classes.bool',
		'rogw.tranp.compatible.python.classes.list.__init__.self': 'rogw.tranp.compatible.python.classes.list',
		'rogw.tranp.compatible.python.classes.list.__init__.iterable': 'typing.Iterator',
		'rogw.tranp.compatible.python.classes.list.__iter__.self': 'rogw.tranp.compatible.python.classes.list',
		'rogw.tranp.compatible.python.classes.list.__contains__.self': 'rogw.tranp.compatible.python.classes.list',
		'rogw.tranp.compatible.python.classes.list.__contains__.key': 'rogw.tranp.compatible.python.template.T_Seq',
		'rogw.tranp.compatible.python.classes.list.append.self': 'rogw.tranp.compatible.python.classes.list',
		'rogw.tranp.compatible.python.classes.list.append.elem': 'rogw.tranp.compatible.python.template.T_Seq',
		'rogw.tranp.compatible.python.classes.list.pop.self': 'rogw.tranp.compatible.python.classes.list',
		'rogw.tranp.compatible.python.classes.list.pop.index': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.dict.__init__.self': 'rogw.tranp.compatible.python.classes.dict',
		'rogw.tranp.compatible.python.classes.dict.__init__.iterable': 'typing.Iterator',
		'rogw.tranp.compatible.python.classes.dict.__iter__.self': 'rogw.tranp.compatible.python.classes.dict',
		'rogw.tranp.compatible.python.classes.dict.__contains__.self': 'rogw.tranp.compatible.python.classes.dict',
		'rogw.tranp.compatible.python.classes.dict.__contains__.key': 'rogw.tranp.compatible.python.template.T_Key',
		'rogw.tranp.compatible.python.classes.dict.keys.self': 'rogw.tranp.compatible.python.classes.dict',
		'rogw.tranp.compatible.python.classes.dict.values.self': 'rogw.tranp.compatible.python.classes.dict',
		'rogw.tranp.compatible.python.classes.dict.items.self': 'rogw.tranp.compatible.python.classes.dict',
		'rogw.tranp.compatible.python.classes.dict.pop.self': 'rogw.tranp.compatible.python.classes.dict',
		'rogw.tranp.compatible.python.classes.dict.pop.key': 'rogw.tranp.compatible.python.template.T_Key',
		'rogw.tranp.compatible.python.classes.object.__init__.self': 'rogw.tranp.compatible.python.classes.object',
		'rogw.tranp.compatible.python.classes.Exception.__init__.self': 'rogw.tranp.compatible.python.classes.Exception',
		'rogw.tranp.compatible.python.classes.Exception.__init__.args': 'typing.Any',
		'rogw.tranp.compatible.python.classes.id.instance': 'typing.Any',
		'rogw.tranp.compatible.python.classes.print.args': 'typing.Any',
		'rogw.tranp.compatible.python.classes.enumerate.iterable': 'typing.Sequence',
		'rogw.tranp.compatible.python.classes.range.size': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.classes.len.iterable': 'typing.Sequence',
		'typing.Any': 'typing.Any',
		'typing.Callable': 'typing.Callable',
		'typing.Generic': 'typing.Generic',
		'typing.Sequence': 'typing.Sequence',
		'typing.TypeAlias': 'typing.TypeAlias',
		'typing.TypeVar': 'typing.TypeVar',
		'typing.T_Seq': 'typing.T_Seq',
		'typing.Iterator': 'typing.Iterator',
		'typing.Iterator.__next__': 'typing.Iterator.__next__',
		'typing.Iterator.__next__.self': 'typing.Iterator',
		'rogw.tranp.compatible.cpp.enum.Enum': 'enum.Enum',
		'rogw.tranp.compatible.cpp.enum.Any': 'typing.Any',
		'rogw.tranp.compatible.cpp.enum.CEnum': 'rogw.tranp.compatible.cpp.enum.CEnum',
		'rogw.tranp.compatible.cpp.enum.CEnum.__int__': 'rogw.tranp.compatible.cpp.enum.CEnum.__int__',
		'rogw.tranp.compatible.cpp.enum.CEnum.__eq__': 'rogw.tranp.compatible.cpp.enum.CEnum.__eq__',
		'rogw.tranp.compatible.cpp.enum.CEnum.__hash__': 'rogw.tranp.compatible.cpp.enum.CEnum.__hash__',
		'rogw.tranp.compatible.cpp.enum.CEnum.__int__.self': 'rogw.tranp.compatible.cpp.enum.CEnum',
		'rogw.tranp.compatible.cpp.enum.CEnum.__eq__.self': 'rogw.tranp.compatible.cpp.enum.CEnum',
		'rogw.tranp.compatible.cpp.enum.CEnum.__eq__.other': 'typing.Any',
		'rogw.tranp.compatible.cpp.enum.CEnum.__hash__.self': 'rogw.tranp.compatible.cpp.enum.CEnum',
		'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.X': 'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.X',
		'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.Y': 'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.Y',
		'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.Z': 'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.Z',
		'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.X.nx': 'rogw.tranp.compatible.python.classes.int',
		'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.Y.ny': 'rogw.tranp.compatible.python.classes.int',
		'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.Y.x': 'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.X',
		'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz.Z.nz': 'rogw.tranp.compatible.python.classes.int',
		'rogw.tranp.compatible.python.embed.Callable': 'typing.Callable',
		'rogw.tranp.compatible.python.embed.TypeVar': 'typing.TypeVar',
		'rogw.tranp.compatible.python.embed.T': 'rogw.tranp.compatible.python.embed.T',
		'rogw.tranp.compatible.python.embed.__actual__': 'rogw.tranp.compatible.python.embed.__actual__',
		'rogw.tranp.compatible.python.embed.__actual__.decorator': 'rogw.tranp.compatible.python.embed.__actual__.decorator',
		'rogw.tranp.compatible.python.embed.__alias__': 'rogw.tranp.compatible.python.embed.__alias__',
		'rogw.tranp.compatible.python.embed.__alias__.decorator': 'rogw.tranp.compatible.python.embed.__alias__.decorator',
		'rogw.tranp.compatible.python.embed.__actual__.name': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.embed.__actual__.decorator.wrapped': 'rogw.tranp.compatible.python.embed.T',
		'rogw.tranp.compatible.python.embed.__alias__.name': 'rogw.tranp.compatible.python.classes.str',
		'rogw.tranp.compatible.python.embed.__alias__.decorator.wrapped': 'rogw.tranp.compatible.python.embed.T',
		'rogw.tranp.compatible.python.template.TypeVar': 'typing.TypeVar',
		'rogw.tranp.compatible.python.template.T_Seq': 'rogw.tranp.compatible.python.template.T_Seq',
		'rogw.tranp.compatible.python.template.T_Key': 'rogw.tranp.compatible.python.template.T_Key',
		'rogw.tranp.compatible.python.template.T_Self': 'rogw.tranp.compatible.python.template.T_Self',
		'enum.T_Self': 'rogw.tranp.compatible.python.template.T_Self',
		'enum.Enum': 'enum.Enum',
		'enum.Enum.__init__': 'enum.Enum.__init__',
		'enum.Enum.__init__.self': 'enum.Enum',
		'enum.Enum.__init__.value': 'rogw.tranp.compatible.python.classes.int',
	}
