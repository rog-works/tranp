# from typing import Any, Iterator
# FIXME 実装を簡単にするため一旦インポートはせず、警告も無視する

@__alias__('int')
class Integer: pass


@__alias__('float')
class Float: pass


@__alias__('str')
class String: pass


@__alias__('bool')
class Boolean: pass


@__alias__('tuple')
class Tuple: pass


@__alias__('pair_')
class Pair: pass


@__alias__('list')
class List: pass


@__alias__('dict')
class Dict: pass


@__alias__('None')
class Null: pass


class Unknown: pass


@__alias__('super')
class Super: pass
