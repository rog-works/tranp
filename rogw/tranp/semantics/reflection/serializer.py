from typing import MutableMapping

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.lang.annotation import implements, injectable
import rogw.tranp.lang.sequence as seqs
from rogw.tranp.lang.trait import Traits
from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.semantics.reflection.reflection import Options, Reflection, Symbol
from rogw.tranp.semantics.reflection.serialization import DictSerialized, IReflectionSerializer
from rogw.tranp.syntax.ast.entrypoints import Entrypoints
import rogw.tranp.syntax.node.definition as defs


class ReflectionSerializer(IReflectionSerializer):
	"""シンボルシリアライザー

	Note:
		* リフレクションの実装に強依存しているため、スキーマの変更に注意
		@see rogw.tranp.semantics.reflection.reflection.Symbol
		@see rogw.tranp.semantics.reflection.reflection.Reflection
	"""

	@injectable
	def __init__(self, entrypoints: Entrypoints, traits: Traits) -> None:
		"""インスタンスを生成

		Args:
			entrypoints: エントリーポイントマネージャー @inject
			traits: トレイトマネージャー @inject
		"""
		self._entrypoints = entrypoints
		self._traits = traits

	@implements
	def serialize(self, symbol: IReflection) -> DictSerialized:
		"""シリアライズ

		Args:
			symbol: シンボル
		Returns:
			データ
		"""
		flat_attrs: dict[str, IReflection] = seqs.expand(symbol.attrs, iter_key='attrs')
		attrs = {path: attr.types.fullyname for path, attr in flat_attrs.items()}
		if symbol.node.is_a(defs.ClassDef) and symbol.types == symbol.decl:
			return {
				'class': 'Symbol',
				'types': ModuleDSN.full_joined(symbol.types.module_path, symbol.types.full_path),
				'attrs': attrs,
			}
		else:
			return {
				'class': 'Reflection',
				'node': ModuleDSN.full_joined(symbol.node.module_path, symbol.node.full_path),
				'decl': ModuleDSN.full_joined(symbol.decl.module_path, symbol.decl.full_path),
				'origin': symbol.types.fullyname,
				'via': symbol.via.types.fullyname,
				'attrs': attrs,
			}

	@implements
	def deserialize(self, db: MutableMapping[str, IReflection], data: DictSerialized) -> IReflection:
		"""デシリアライズ

		Args:
			db: シンボルテーブル
			data: データ
		Returns:
			シンボル
		"""
		if data['class'] == 'Symbol':
			types_paths = ModuleDSN.parsed(data['types'])
			types = self._entrypoints.load(types_paths[0]).whole_by(types_paths[1]).as_a(defs.ClassDef)
			symbol = Symbol.instantiate(self._traits, types).stack()
			attrs = self._deserialize_attrs(db, data['attrs'])
			return symbol.extends(*attrs)
		else:
			node_paths = ModuleDSN.parsed(data['node'])
			decl_paths = ModuleDSN.parsed(data['decl'])
			node = self._entrypoints.load(node_paths[0]).whole_by(node_paths[1])
			decl = self._entrypoints.load(decl_paths[0]).whole_by(decl_paths[1]).one_of(*defs.DeclAllTs)
			origin = db[data['origin']]
			via = db[data['via']] if data['origin'] != data['via'] else None
			symbol = Reflection(self._traits, Options(node=node, decl=decl, origin=origin, via=via))
			attrs = self._deserialize_attrs(db, data['attrs'])
			return symbol.extends(*attrs)

	def _deserialize_attrs(self, db: MutableMapping[str, IReflection], data_attrs: dict[str, str]) -> list[IReflection]:
		"""デシリアライズ(属性)

		Args:
			db: シンボルテーブル
			data_attrs: データ(属性)
		Returns:
			属性のシンボルリスト
		"""
		# 階層が浅い順にソート
		paths = sorted(data_attrs.keys(), key=lambda key: key.count('.'))
		attrs: list[IReflection] = []
		index = 0
		while index < len(paths):
			elems = paths[index].split('.')

			# 同じ階層の範囲を検索
			own_path = '.'.join(elems[:-1])
			end = index + 1
			while end < len(paths):
				next_own_path = '.'.join(paths[end].split('.')[:-1])
				if own_path != next_own_path:
					break

				end += 1

			# 参照属性を抽出 XXX 必ずstackしているが、本来属性を追加するシンボル以外に必要はない処理。害はないが若干無駄であり、不具合の原因になり兼ねないので改善を検討
			new_attrs = [db[data_attrs[path]].stack() for path in paths[index:end]]
			index = end

			# 1階層目
			if len(elems) == 1:
				attrs.extend(new_attrs)
				continue

			# 2階層目以降
			index_keys = [int(index_key) for index_key in own_path.split('.')]
			attr = attrs[index_keys.pop(0)]
			while index_keys:
				attr = attr.attrs[index_keys.pop(0)]

			attr.extends(*new_attrs)

		return attrs
