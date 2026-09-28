class Errors:
	"""エラーの名前空間"""

	# ----- Base

	class Error(Exception): """アプリケーション例外の基底クラス"""
	class Never(Error): """未到達。設計ミス"""
	class Fatal(Error): """致命的。原因不明のエラー"""
	class Logic(Error): """実装不備。ランタイムエラー"""

	# ----- General

	class InvalidSchema(Logic): """スキーマ・書式が不正。外因によるエラー"""

	# ----- Transpiler

	class Syntax(Logic): """シンタックスエラー"""
	class Semantics(Logic): """意味解析由来のエラー(基底)"""

	class NodeError(Semantics): """ノード由来のエラー(基底)"""
	class NodeNotFound(NodeError): """指定したノードが存在しない"""
	class UnresolvedNode(NodeError): """ASTエントリーからノードの解決に失敗"""
	class IllegalConvertion(NodeError): """派生クラスへの変換時に不正な変換先を指定"""
	class InvalidRelation(NodeError): """ノード間の不正なリレーション"""

	class ReflectionError(Semantics): """リフレクション由来のエラー(基底)"""
	class UnresolvedSymbol(ReflectionError): """シンボルの解決に失敗。シンボル解決が対象"""
	class MustBeImplemented(ReflectionError): """必須の機能(クラス/ファンクション)の実装漏れ"""
	class SymbolNotDefined(ReflectionError): """未定義のシンボルを検索。シンボル検索が対象"""
	class OperationNotAllowed(ReflectionError): """許可されない(または未実装)の操作(演算/代入など)を指定"""
	class NotSupported(ReflectionError): """非対応の機能を使用"""
