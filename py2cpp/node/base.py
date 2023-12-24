from typing import TypeVar


class NodeBase:
	"""ノードの基底クラス。主にGeneric型の解決に利用"""
	pass


T_NodeBase = TypeVar('T_NodeBase', bound=NodeBase)


class Plugin:
	"""プラグインの基底クラス。ノード内でのみ使用"""
	pass


T_Plugin = TypeVar('T_Plugin', bound=Plugin)
