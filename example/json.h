// @tranp.meta: {"version":"1.0.0","module":{"hash":"82ee91dbd29c33a464b9b286b531c294","path":"example.json"},"transpiler":{"version":"1.0.0","module":"rogw.tranp.implements.cpp.transpiler.py2cpp.Py2Cpp"}}
#pragma once
#include <functional>
// #include "enum.h"
// #include "typing.h"
// #include "rogw/tranp/compatible/cpp/classes.h"
// #include "rogw/tranp/compatible/cpp/object.h"
// #include "rogw/tranp/compatible/python/embed.h"
#include "FW/string.h"
/**
 * JSONエントリーの種別
 */
enum class JsonEntryTypes {
	Unknown = 0,
	Boolean = 1,
	Number = 2,
	String = 3,
	Array = 4,
	Object = 5,
};
using JsonEntryInfo = std::tuple<std::string, int, int>;
/**
 * JSONパーサー
 */
class JsonParser {
	public:
	/**
	 * JSON文字列を解析
	 * @param json_str JSON文字列
	 * @return JSONエントリー情報リスト
	 */
	static std::vector<JsonEntryInfo> parse(const std::string& json_str) {
		return std::get<0>(JsonParser::_parse_entry(json_str, 0, ""));
	}
	protected:
	/**
	 * JSON文字列を解析(エントリー)
	 * @param json_str JSON文字列
	 * @param begin 読み取り開始位置
	 * @param path エントリーパス
	 * @return JSONエントリー情報リスト, 読み取り終了位置
	 */
	static std::tuple<std::vector<JsonEntryInfo>, int> _parse_entry(const std::string& json_str, int begin, const std::string& path) {
		int end = begin;
		std::vector<JsonEntryInfo> info_list = {};
		auto [at_type, begin_value] = JsonParser::_analyze_type(json_str, begin);
		end = begin_value;
		if (at_type == JsonEntryTypes::Boolean) {
			end = JsonParser::_parse_boolean(json_str, begin_value);
			info_list.push_back({path, begin_value, end});
		} else if (at_type == JsonEntryTypes::Number) {
			end = JsonParser::_parse_number(json_str, begin_value);
			info_list.push_back({path, begin_value, end});
		} else if (at_type == JsonEntryTypes::String) {
			end = JsonParser::_parse_string(json_str, begin_value);
			info_list.push_back({path, begin_value, end});
		} else if (at_type == JsonEntryTypes::Array) {
			auto [in_entries, next_pos] = JsonParser::_parse_array(json_str, begin_value, path);
			end = next_pos;
			info_list.push_back({path, begin_value, end});
			info_list.insert(info_list.end(), in_entries);
		} else if (at_type == JsonEntryTypes::Object) {
			auto [in_entries, next_pos] = JsonParser::_parse_object(json_str, begin_value, path);
			end = next_pos;
			info_list.push_back({path, begin_value, end});
			info_list.insert(info_list.end(), in_entries);
		}
		return {info_list, end};
	}
	protected:
	/**
	 * JSON文字列を解析(エントリー/Boolean)
	 * @param json_str JSON文字列
	 * @param begin 読み取り開始位置
	 * @return 読み取り終了位置
	 */
	static int _parse_boolean(const std::string& json_str, int begin) {
		int end = begin;
		std::string string = "";
		while (end < json_str.size()) {
			string += json_str[end];
			if (string == "false" || string == "true") {
				break;
			}
			end += 1;
		}
		return end + 1;
	}
	protected:
	/**
	 * JSON文字列を解析(エントリー/Number)
	 * @param json_str JSON文字列
	 * @param begin 読み取り開始位置
	 * @return 読み取り終了位置
	 */
	static int _parse_number(const std::string& json_str, int begin) {
		int end = begin;
		while (end < json_str.size()) {
			end += 1;
			if (!String::is_number(json_str, begin, end + 1)) {
				break;
			}
		}
		return end;
	}
	protected:
	/**
	 * JSON文字列を解析(エントリー/String)
	 * @param json_str JSON文字列
	 * @param begin 読み取り開始位置
	 * @return 読み取り終了位置
	 */
	static int _parse_string(const std::string& json_str, int begin) {
		int end = json_str.find("\"", begin);
		while (end < json_str.size()) {
			end += 1;
			if (json_str[end - 1] == '\\' && json_str[end] == '"') {
				continue;
			}
			if (json_str[end] == '"') {
				break;
			}
		}
		return end + 1;
	}
	protected:
	/**
	 * JSON文字列を解析(エントリー/Array)
	 * @param json_str JSON文字列
	 * @param begin 読み取り開始位置
	 * @param path エントリーパス
	 * @return JSONエントリー情報リスト, 読み取り終了位置
	 */
	static std::tuple<std::vector<JsonEntryInfo>, int> _parse_array(const std::string& json_str, int begin, const std::string& path) {
		int end = json_str.find("[", begin);
		std::vector<JsonEntryInfo> info_list = {};
		end += 1;
		int element_at = 0;
		while (end < json_str.size()) {
			JsonEntryTypes entry_type = std::get<0>(JsonParser::_analyze_type(json_str, end, "]"));
			if (entry_type == JsonEntryTypes::Unknown || json_str[end] == ']') {
				break;
			}
			auto [in_info_list, next_pos] = JsonParser::_parse_entry(json_str, end, JsonParser::join_path(path, std::to_string(element_at)));
			end = next_pos;
			info_list.insert(info_list.end(), in_info_list);
			element_at += 1;
		}
		return {info_list, end + 1};
	}
	protected:
	/**
	 * JSON文字列を解析(エントリー/Object)
	 * @param json_str JSON文字列
	 * @param begin 読み取り開始位置
	 * @param path エントリーパス
	 * @return JSONエントリー情報リスト, 読み取り終了位置
	 */
	static std::tuple<std::vector<JsonEntryInfo>, int> _parse_object(const std::string& json_str, int begin, const std::string& path) {
		int end = json_str.find("{", begin);
		std::vector<JsonEntryInfo> info_list = {};
		end += 1;
		while (end < json_str.size()) {
			JsonEntryTypes entry_type = std::get<0>(JsonParser::_analyze_type(json_str, end, "}"));
			if (entry_type == JsonEntryTypes::Unknown || json_str[end] == '}') {
				break;
			}
			auto [key, begin_value] = JsonParser::_parse_key(json_str, end);
			auto [in_info_list, next_pos] = JsonParser::_parse_entry(json_str, begin_value, JsonParser::join_path(path, key));
			end = next_pos;
			info_list.insert(info_list.end(), in_info_list);
		}
		return {info_list, end + 1};
	}
	protected:
	/**
	 * JSON文字列を解析(キー)
	 * @param json_str JSON文字列
	 * @param begin 読み取り開始位置
	 * @return キー, 読み取り終了位置
	 */
	static std::tuple<std::string, int> _parse_key(const std::string& json_str, int begin) {
		int key_begin = json_str.find("\"", begin);
		int end = json_str.find("\"", key_begin + 1);
		std::string key = json_str.substr(key_begin + 1, end - (key_begin + 1));
		return {key, end + 1};
	}
	public:
	/**
	 * JSONエントリーの種別を解析
	 * @param json_str JSON文字列
	 * @param begin 読み取り開始位置
	 * @return JSONエントリーの種別
	 * @throw RuntimeError 解析に失敗
	 */
	static JsonEntryTypes analyze_type(const std::string& json_str, int begin) {
		JsonEntryTypes entry_type = std::get<0>(JsonParser::_analyze_type(json_str, begin));
		if (entry_type == JsonEntryTypes::Unknown) {
			throw new std::runtime_error(std::format("Invalid JSON schema. json_str: %s, begin: %d", (json_str).c_str(), begin));
		}
		return entry_type;
	}
	protected:
	/**
	 * JSONエントリーの種別を解析
	 * @param json_str JSON文字列
	 * @param begin 読み取り開始位置
	 * @param end_token 終端記号 (default = '')
	 * @return JSONエントリーの種別, 読み取り終了位置
	 */
	static std::tuple<JsonEntryTypes, int> _analyze_type(const std::string& json_str, int begin, const std::string& end_token = "") {
		int end = begin;
		while (end < json_str.size()) {
			if (json_str[end] == 'f' || json_str[end] == 't') {
				return {JsonEntryTypes::Boolean, end};
			} else if (json_str[end] == '"') {
				return {JsonEntryTypes::String, end};
			} else if (json_str[end] == '[') {
				return {JsonEntryTypes::Array, end};
			} else if (json_str[end] == '{') {
				return {JsonEntryTypes::Object, end};
			} else if (String::is_number(json_str, end, end + 1)) {
				return {JsonEntryTypes::Number, end};
			} else if (end_token.size() > 0 && json_str[end] == end_token[0]) {
				return {JsonEntryTypes::Unknown, -1};
			}
			end += 1;
		}
		return {JsonEntryTypes::Unknown, -1};
	}
	public:
	/**
	 * パスを連結
	 * @param path1 パス0
	 * @param path2 パス1
	 * @return 連結したパス
	 */
	static std::string join_path(const std::string& path0, const std::string& path1) {
		return path0.size() > 0 ? path0 + "." + path1 : path1;
	}
};
/**
 * JSONエントリーの実体を管理
 */
struct JsonEntity {
	public: bool as_bool;
	public: float as_number;
	public: std::string as_string;
	public:
	/**
	 * インスタンスを生成
	 */
	JsonEntity() : as_bool(false), as_number(0), as_string("") {}
	public:
	/**
	 * スカラー型用にインスタンスを生成
	 * @param value_str 文字列
	 * @param entry_type JSONエントリーの種別
	 * @return インスタンス
	 */
	static JsonEntity for_scalar(const std::string& value_str, JsonEntryTypes entry_type) {
		JsonEntity instance{};
		if (entry_type == JsonEntryTypes::Boolean) {
			instance.as_bool = value_str == "true";
		} else if (entry_type == JsonEntryTypes::Number) {
			instance.as_number = std::stod(value_str);
		} else if (entry_type == JsonEntryTypes::String) {
			instance.as_string = String::unescape(value_str.substr(1, value_str.size() - 1 - (1)));
		}
		return instance;
	}
};
/**
 * JSONエントリー
 */
struct JsonEntry {
	public: std::string path;
	public: JsonEntryTypes entry_type;
	public: JsonEntity entity;
	public:
	/**
	 * インスタンスを生成
	 */
	JsonEntry() : path(""), entry_type(JsonEntryTypes::Unknown), entity({}) {}
	public:
	/**
	 * インスタンスを生成
	 * @param path JSONパス
	 * @param entry_type JSONエントリーの種別
	 * @param entity JSONエンティティー
	 * @return インスタンス
	 */
	static JsonEntry make(const std::string& path, JsonEntryTypes entry_type, JsonEntity entity) {
		JsonEntry instance{};
		instance.path = path;
		instance.entry_type = entry_type;
		instance.entity = entity;
		return instance;
	}
};
/**
 * JSON
 */
class Json {
	protected: inline static std::map<JsonEntryTypes, std::string> _to_type_names = {
		{JsonEntryTypes::Boolean, "bool"},
		{JsonEntryTypes::Number, "float"},
		{JsonEntryTypes::String, "std::string"},
		{JsonEntryTypes::Array, "std::vector"},
		{JsonEntryTypes::Object, "Json"},
	};
	protected: std::vector<std::shared_ptr<Json>> _jsons;
	protected: std::vector<JsonEntry> _entries;
	protected: Json* _root;
	protected: int _entry_id;
	public:
	/**
	 * インスタンスを生成
	 */
	Json() : object(), _jsons({}), _entries({}), _root(this), _entry_id(0) {}
	// method __repr__
	public:
	/**
	 * オブジェクト型の空のインスタンスを生成
	 * @return インスタンス
	 */
	static std::shared_ptr<Json> instantiate() {
		return Json::parse("{}");
	}
	public:
	/**
	 * JSON文字列を基にインスタンスを生成
	 * @param json_str JSON文字列
	 * @return インスタンス
	 */
	static std::shared_ptr<Json> parse(const std::string& json_str) {
		std::shared_ptr<Json> root = std::make_shared<Json>();
		std::vector<JsonEntryInfo> info_list = JsonParser::parse(json_str);
		for (auto entry_id = 0; entry_id < info_list.size(); entry_id++) {
			auto [path, begin, end] = info_list[entry_id];
			JsonEntryTypes entry_type = JsonParser::analyze_type(json_str, begin);
			if (entry_type == JsonEntryTypes::Boolean || entry_type == JsonEntryTypes::Number || entry_type == JsonEntryTypes::String) {
				root->_jsons.push_back(root->_make_for_entry(entry_id));
				root->_entries.push_back(JsonEntry::make(path, entry_type, JsonEntity::for_scalar(json_str.substr(begin, end - (begin)), entry_type)));
			} else {
				root->_jsons.push_back(root->_make_for_entry(entry_id));
				root->_entries.push_back(JsonEntry::make(path, entry_type, JsonEntity()));
			}
		}
		return root;
	}
	protected:
	/**
	 * スカラー値からJSONインスタンスに変換(Boolean)
	 * @param value 値
	 * @return インスタンス
	 */
	std::shared_ptr<Json> _jsonify_of_bool(bool value) {
		return Json::parse(value ? "true" : "false");
	}
	protected:
	/**
	 * スカラー値からJSONインスタンスに変換(Number)
	 * @param value 値
	 * @return インスタンス
	 */
	std::shared_ptr<Json> _jsonify_of_number(float value) {
		return Json::parse(std::to_string(value));
	}
	protected:
	/**
	 * スカラー値からJSONインスタンスに変換(String)
	 * @param value 値
	 * @return インスタンス
	 */
	std::shared_ptr<Json> _jsonify_of_string(const std::string& value) {
		return Json::parse("\"" + String::escape(value, '"') + "\"");
	}
	protected:
	/**
	 * エントリー用にインスタンスを生成
	 * @param entry_id エントリーID
	 * @return インスタンス
	 */
	std::shared_ptr<Json> _make_for_entry(int entry_id) {
		std::shared_ptr<Json> under = std::make_shared<Json>();
		under->_root = this;
		under->_entry_id = entry_id;
		return under;
	}
	protected:
	/**
	 * 自身の配下要素のパスか判定
	 * @param path パス
	 * @return True = 配下要素
	 */
	bool _is_under(const std::string& path) {
		if (!(this->path().size() < path.size())) {
			return false;
		}
		if (!this->_starts_with(path, this->path())) {
			return false;
		}
		int dots1 = path.count(".");
		if (this->path().size() == 0) {
			return dots1 == 0;
		}
		int dots0 = this->path().count(".");
		return dots0 + 1 == dots1;
	}
	public:
	/**
	 * 指定のスカラー型か判定。引数を省略した場合は、スカラー型か否かを判定
	 * @param expected_type 判定するJSONエントリーの種別 (default = NotFound)
	 * @return True = スカラー型, False = Array/Object
	 */
	bool scalar_with(JsonEntryTypes expected_type = JsonEntryTypes::Unknown) {
		if (expected_type == JsonEntryTypes::Unknown) {
			return this->entry_type() == JsonEntryTypes::Boolean || this->entry_type() == JsonEntryTypes::Number || this->entry_type() == JsonEntryTypes::String;
		}
		return this->entry_type() == expected_type;
	}
	protected:
	/**
	 * 指定エントリーのJSONを取得
	 * @param entry_id エントリーID
	 * @return JSON
	 */
	Json* _at_json(int entry_id) {
		return (this->root()->_jsons[entry_id]).get();
	}
	public:
	/**
	 *
	 * @return True = ルートオブジェクト
	 */
	inline bool is_root() {
		return this->_root == nullptr;
	}
	public:
	/**
	 *
	 * @return ルートオブジェクト
	 */
	inline Json* root() {
		return this->_root ? this->_root : this;
	}
	public:
	/**
	 *
	 * @return JSONパス
	 */
	inline std::string path() {
		return this->root()->_entries[this->_entry_id].path;
	}
	public:
	/**
	 *
	 * @return シンボル名
	 */
	inline std::string symbol() {
		int index = this->path().find_last_of(".");
		return index != -1 ? this->path().substr(index + 1, this->path().size() - (index + 1)) : this->path();
	}
	public:
	/**
	 *
	 * @return JSONエントリーの種別
	 */
	inline JsonEntryTypes entry_type() {
		return this->root()->_entries[this->_entry_id].entry_type;
	}
	public:
	/**
	 *
	 * @return 型の名前
	 */
	inline std::string type_name() {
		return Json::_to_type_names[this->entry_type()];
	}
	public:
	/**
	 *
	 * @return 実体のアドレス
	 */
	inline void* entity_at() {
		if (this->scalar_with(JsonEntryTypes::Boolean)) {
			return (&(this->root()->_entries[this->_entry_id].entity.as_bool));
		} else if (this->scalar_with(JsonEntryTypes::Number)) {
			return (&(this->root()->_entries[this->_entry_id].entity.as_number));
		} else if (this->scalar_with(JsonEntryTypes::String)) {
			return (&(this->root()->_entries[this->_entry_id].entity.as_string));
		} else {
			return this->_at_json(this->_entry_id);
		}
	}
	public:
	/**
	 * 指定のJSONパスを持つ要素が存在するか判定
	 * @param jsonpath JSONパス
	 * @return True = 存在
	 */
	bool exists(const std::string& jsonpath) {
		for (auto& entry : this->root()->_entries) {
			if (jsonpath == entry.path) {
				return true;
			}
		}
		return false;
	}
	public:
	/**
	 * 指定のキーを持つ配下要素が存在するか判定
	 * @param key キー
	 * @return True = 存在
	 */
	bool has_key(const std::string& key) {
		return this->exists(JsonParser::join_path(this->path(), key));
	}
	public:
	/**
	 * 配下要素を取得
	 * @return 配下要素のリスト
	 */
	std::vector<Json*> unders() {
		std::vector<Json*> under_values = {};
		int remain = this->root()->_entries.size() - this->_entry_id;
		for (auto i = 0; i < remain; i++) {
			int entry_id = i + this->_entry_id;
			Json* entry_json = this->_at_json(entry_id);
			if (this->_is_under(entry_json->path())) {
				under_values.push_back(entry_json);
			}
		}
		return under_values;
	}
	public:
	/**
	 * 配下要素を取得
	 * @param index インデックス
	 * @return インスタンス
	 * @throw RuntimeError 存在しないエントリーを指定
	 */
	Json* at(int index) {
		return this->fetch(JsonParser::join_path(this->path(), std::to_string(index)));
	}
	public:
	/**
	 * 配下要素を取得
	 * @param key シンボル名
	 * @return インスタンス
	 * @throw RuntimeError 存在しないエントリーを指定
	 */
	Json* by(const std::string& key) {
		return this->fetch(JsonParser::join_path(this->path(), key));
	}
	public:
	/**
	 * JSONパスと一致するエントリーを取得
	 * @param jsonpath JSONパス
	 * @return インスタンス
	 * @throw RuntimeError 存在しないエントリーを指定
	 */
	Json* fetch(const std::string& jsonpath) {
		for (auto entry_id = 0; entry_id < this->root()->_entries.size(); entry_id++) {
			Json* entry_json = this->_at_json(entry_id);
			if (jsonpath == entry_json->path()) {
				return entry_json;
			}
		}
		throw new std::runtime_error(std::format("Entry not found. jsonpath: %s", (jsonpath).c_str()));
	}
	public:
	/**
	 * フィルター条件に一致する要素を取得
	 * @param query フィルター関数
	 * @return 要素リスト
	 */
	std::vector<Json*> filter(const std::function<bool(Json*)>& query) {
		return [&]() -> std::vector<Json*> {
			std::vector<Json*> __ret;
			for (auto in_json : this->_jsons) {
				if (query((in_json).get())) {
					__ret.push_back((in_json).get());
				}
			}
			return __ret;
		}();
	}
	public:
	/**
	 * 相違個所のパスを抽出
	 * @param other 比較対象
	 * @return パスリスト
	 * @note パスには自身と比較対象、双方のパスが混在する点に注意
	 */
	std::vector<std::string> diff(Json* other) {
		std::vector<std::string> diff_paths = {};
		if (this->entry_type() != other->entry_type()) {
			diff_paths.push_back(this->path());
		} else if (this->scalar_with(JsonEntryTypes::Boolean) && this->as_bool() != other->as_bool()) {
			diff_paths.push_back(this->path());
		} else if (this->scalar_with(JsonEntryTypes::Number) && this->as_number() != other->as_number()) {
			diff_paths.push_back(this->path());
		} else if (this->scalar_with(JsonEntryTypes::String) && this->as_string() != other->as_string()) {
			diff_paths.push_back(this->path());
		} else if (!this->scalar_with()) {
			for (auto under : this->unders()) {
				if (other->has_key(under->symbol())) {
					diff_paths.insert(diff_paths.end(), under->diff(other->by(under->symbol())));
				} else {
					diff_paths.push_back(under->path());
				}
			}
			for (auto under : other->unders()) {
				if (!this->has_key(under->symbol())) {
					diff_paths.push_back(under->path());
				}
			}
			if (diff_paths.size() > 0) {
				diff_paths.push_back(this->path());
			}
		}
		return diff_paths;
	}
	public:
	/**
	 *
	 * @return 値
	 * @throw RuntimeError Boolean以外で使用
	 */
	inline bool as_bool() {
		if (!this->scalar_with(JsonEntryTypes::Boolean)) {
			throw new std::runtime_error(std::format("Operation not allowed. type_name: %s", (this->type_name()).c_str()));
		}
		return this->root()->_entries[this->_entry_id].entity.as_bool;
	}
	public:
	/**
	 *
	 * @return 値
	 * @throw RuntimeError Number以外で使用
	 */
	inline float as_number() {
		if (!this->scalar_with(JsonEntryTypes::Number)) {
			throw new std::runtime_error(std::format("Operation not allowed. type_name: %s", (this->type_name()).c_str()));
		}
		return this->root()->_entries[this->_entry_id].entity.as_number;
	}
	public:
	/**
	 *
	 * @return 値
	 * @throw RuntimeError String以外で使用
	 */
	inline std::string as_string() {
		if (!this->scalar_with(JsonEntryTypes::String)) {
			throw new std::runtime_error(std::format("Operation not allowed. type_name: %s", (this->type_name()).c_str()));
		}
		return this->root()->_entries[this->_entry_id].entity.as_string;
	}
	public:
	/**
	 * 値を更新(Boolean)
	 * @param value 値
	 */
	void set_bool(bool value) {
		if (this->scalar_with()) {
			this->root()->_entries[this->_entry_id].entity.as_bool = value;
			this->root()->_entries[this->_entry_id].entry_type = JsonEntryTypes::Boolean;
		} else {
			this->_swap_entry(this->_jsonify_of_bool(value));
		}
	}
	public:
	/**
	 * 値を更新(Number)
	 * @param value 値
	 */
	void set_number(float value) {
		if (this->scalar_with()) {
			this->root()->_entries[this->_entry_id].entity.as_number = value;
			this->root()->_entries[this->_entry_id].entry_type = JsonEntryTypes::Number;
		} else {
			this->_swap_entry(this->_jsonify_of_number(value));
		}
	}
	public:
	/**
	 * 値を更新(String)
	 * @param value 値
	 */
	void set_string(const std::string& value) {
		if (this->scalar_with()) {
			this->root()->_entries[this->_entry_id].entity.as_string = value;
			this->root()->_entries[this->_entry_id].entry_type = JsonEntryTypes::String;
		} else {
			this->_swap_entry(this->_jsonify_of_string(value));
		}
	}
	public:
	/**
	 * 値を更新(Array)
	 * @param value 値
	 * @throw RuntimeError Array以外を指定
	 */
	void set_array(Json* value) {
		if (value->entry_type() != JsonEntryTypes::Array) {
			throw new std::runtime_error(std::format("Type not match. type_name: %s", (value->type_name()).c_str()));
		}
		this->_swap_entry(value->isolate());
	}
	public:
	/**
	 * 値を更新(Object)
	 * @param value 値
	 * @throw RuntimeError Object以外を指定
	 */
	void set_object(Json* value) {
		if (value->entry_type() != JsonEntryTypes::Object) {
			throw new std::runtime_error(std::format("Type not match. type_name: %s", (value->type_name()).c_str()));
		}
		this->_swap_entry(value->isolate());
	}
	public:
	/**
	 * 値を更新(汎用)
	 * @param value 値
	 */
	void set_json(Json* value) {
		if (value->scalar_with(JsonEntryTypes::Boolean)) {
			this->set_bool(value->as_bool());
		} else if (value->scalar_with(JsonEntryTypes::Number)) {
			this->set_number(value->as_number());
		} else if (value->scalar_with(JsonEntryTypes::String)) {
			this->set_string(value->as_string());
		} else if (value->scalar_with(JsonEntryTypes::Array)) {
			this->set_array(value);
		} else {
			this->set_object(value);
		}
	}
	public:
	/**
	 * 指定のキーの要素に値を反映。存在しない場合は要素を追加(Boolean)
	 * @param key キー
	 * @param value 値
	 */
	void apply_bool_to(const std::string& key, bool value) {
		std::string jsonpath = JsonParser::join_path(this->path(), key);
		if (this->exists(jsonpath)) {
			this->fetch(jsonpath)->set_bool(value);
		} else {
			this->_add_entry(key, this->_jsonify_of_bool(value));
		}
	}
	public:
	/**
	 * 指定のキーの要素に値を反映。存在しない場合は要素を追加(Number)
	 * @param key キー
	 * @param value 値
	 */
	void apply_number_to(const std::string& key, float value) {
		std::string jsonpath = JsonParser::join_path(this->path(), key);
		if (this->exists(jsonpath)) {
			this->fetch(jsonpath)->set_number(value);
		} else {
			this->_add_entry(key, this->_jsonify_of_number(value));
		}
	}
	public:
	/**
	 * 指定のキーの要素に値を反映。存在しない場合は要素を追加(String)
	 * @param key キー
	 * @param value 値
	 */
	void apply_string_to(const std::string& key, const std::string& value) {
		std::string jsonpath = JsonParser::join_path(this->path(), key);
		if (this->exists(jsonpath)) {
			this->fetch(jsonpath)->set_string(value);
		} else {
			this->_add_entry(key, this->_jsonify_of_string(value));
		}
	}
	public:
	/**
	 * 指定のキーの要素に値を反映。存在しない場合は要素を追加(Array)
	 * @param key キー
	 * @param value 値
	 * @throw RuntimeError Array以外を指定
	 */
	void apply_array_to(const std::string& key, Json* value) {
		if (value->entry_type() != JsonEntryTypes::Array) {
			throw new std::runtime_error(std::format("Type not match. type_name: %s", (value->type_name()).c_str()));
		}
		std::string jsonpath = JsonParser::join_path(this->path(), key);
		if (this->exists(jsonpath)) {
			this->fetch(jsonpath)->set_array(value);
		} else {
			this->_add_entry(key, value->isolate());
		}
	}
	public:
	/**
	 * 指定のキーの要素に値を反映。存在しない場合は要素を追加(Object)
	 * @param key キー
	 * @param value 値
	 * @throw RuntimeError Object以外を指定
	 */
	void apply_object_to(const std::string& key, Json* value) {
		if (value->entry_type() != JsonEntryTypes::Object) {
			throw new std::runtime_error(std::format("Type not match. type_name: %s", (value->type_name()).c_str()));
		}
		std::string jsonpath = JsonParser::join_path(this->path(), key);
		if (this->exists(jsonpath)) {
			this->fetch(jsonpath)->set_object(value);
		} else {
			this->_add_entry(key, value->isolate());
		}
	}
	public:
	/**
	 * 指定のキーの要素に値を反映。存在しない場合は要素を追加(汎用)
	 * @param key キー
	 * @param value 値
	 */
	void apply_json_to(const std::string& key, Json* value) {
		if (value->scalar_with(JsonEntryTypes::Boolean)) {
			this->apply_bool_to(key, value->as_bool());
		} else if (value->scalar_with(JsonEntryTypes::Number)) {
			this->apply_number_to(key, value->as_number());
		} else if (value->scalar_with(JsonEntryTypes::String)) {
			this->apply_string_to(key, value->as_string());
		} else if (value->entry_type() == JsonEntryTypes::Array) {
			this->apply_array_to(key, value);
		} else {
			this->apply_object_to(key, value);
		}
	}
	public:
	/**
	 * 指定のインデックスの要素に値を反映。存在しない場合は要素を追加(Boolean)
	 * @param index インデックス
	 * @param value 値
	 * @throw RuntimeError Array以外で使用
	 */
	void apply_bool_at(int index, bool value) {
		if (this->entry_type() != JsonEntryTypes::Array) {
			throw new std::runtime_error(std::format("Operation not allowed. type_name: %s", (this->type_name()).c_str()));
		}
		this->apply_bool_to(std::to_string(index), value);
	}
	public:
	/**
	 * 指定のインデックスの要素に値を反映。存在しない場合は要素を追加(Number)
	 * @param index インデックス
	 * @param value 値
	 * @throw RuntimeError Array以外で使用
	 */
	void apply_number_at(int index, float value) {
		if (this->entry_type() != JsonEntryTypes::Array) {
			throw new std::runtime_error(std::format("Operation not allowed. type_name: %s", (this->type_name()).c_str()));
		}
		this->apply_number_to(std::to_string(index), value);
	}
	public:
	/**
	 * 指定のインデックスの要素に値を反映。存在しない場合は要素を追加(String)
	 * @param index インデックス
	 * @param value 値
	 * @throw RuntimeError Array以外で使用
	 */
	void apply_string_at(int index, const std::string& value) {
		if (this->entry_type() != JsonEntryTypes::Array) {
			throw new std::runtime_error(std::format("Operation not allowed. type_name: %s", (this->type_name()).c_str()));
		}
		this->apply_string_to(std::to_string(index), value);
	}
	public:
	/**
	 * 指定のインデックスの要素に値を反映。存在しない場合は要素を追加(Array)
	 * @param index インデックス
	 * @param value 値
	 * @throw RuntimeError Array以外で使用
	 */
	void apply_array_at(int index, Json* value) {
		if (this->entry_type() != JsonEntryTypes::Array) {
			throw new std::runtime_error(std::format("Operation not allowed. type_name: %s", (this->type_name()).c_str()));
		}
		this->apply_array_to(std::to_string(index), value);
	}
	public:
	/**
	 * 指定のインデックスの要素に値を反映。存在しない場合は要素を追加(Object)
	 * @param index インデックス
	 * @param value 値
	 * @throw RuntimeError Array以外で使用
	 */
	void apply_object_at(int index, Json* value) {
		if (this->entry_type() != JsonEntryTypes::Array) {
			throw new std::runtime_error(std::format("Operation not allowed. type_name: %s", (this->type_name()).c_str()));
		}
		this->apply_object_to(std::to_string(index), value);
	}
	public:
	/**
	 * 指定のインデックスの要素に値を反映。存在しない場合は要素を追加(汎用)
	 * @param index インデックス
	 * @param value 値
	 */
	void apply_json_at(int index, Json* value) {
		this->apply_json_to(std::to_string(index), value);
	}
	public:
	/**
	 * 指定のインデックスの要素を削除
	 * @param index インデックス
	 * @throw RuntimeError Array以外で使用
	 * @throw RuntimeError 存在しないエントリーを指定
	 */
	void remove_at(int index) {
		if (this->entry_type() != JsonEntryTypes::Array) {
			throw new std::runtime_error(std::format("Operation not allowed. type_name: %s", (this->type_name()).c_str()));
		}
		this->remove_by(std::to_string(index));
	}
	public:
	/**
	 * 指定のキーの要素を削除
	 * @param key キー
	 * @throw RuntimeError Array/Object以外で使用
	 * @throw RuntimeError 存在しないエントリーを指定
	 */
	void remove_by(const std::string& key) {
		if (this->scalar_with()) {
			throw new std::runtime_error(std::format("Operation not allowed. type_name: %s", (this->type_name()).c_str()));
		}
		std::string jsonpath = JsonParser::join_path(this->path(), key);
		if (!this->exists(jsonpath)) {
			throw new std::runtime_error(std::format("Entry not found. jsonpath: %s", (jsonpath).c_str()));
		}
		this->_remove_entry(this->fetch(jsonpath)->_entry_id);
	}
	protected:
	/**
	 * 自身の配下にJSONエントリーを追加
	 * @param key キー
	 * @param entry_json JSON
	 * @throw RuntimeError Array/Object以外で使用
	 * @note XXX このメソッドを実行する前に必ずexists/has_keyで重複がないことを確認すること
	 */
	void _add_entry(const std::string& key, std::shared_ptr<Json> entry_json) {
		if (this->scalar_with()) {
			throw new std::runtime_error(std::format("Operation not allowed. type_name: %s", (this->type_name()).c_str()));
		}
		this->_insert_entry(this->root()->_entries.size(), JsonParser::join_path(this->path(), key), entry_json);
	}
	protected:
	/**
	 * 自身のエントリーを基点に新たなJSONエントリーに置き換え
	 * @param entry_json JSON
	 */
	void _swap_entry(std::shared_ptr<Json> entry_json) {
		std::string self_path = this->path();
		this->_remove_entry(this->_entry_id);
		this->_insert_entry(this->_entry_id, self_path, entry_json);
	}
	protected:
	/**
	 * 指定位置のJSONエントリーとその下位要素を削除
	 * @param entry_id エントリーID
	 */
	void _remove_entry(int entry_id) {
		std::vector<int> relayed_ids = this->_relayed_entry_ids(entry_id);
		for (auto i = 0; i < relayed_ids.size(); i++) {
			int index = relayed_ids.size() - 1 - i;
			int relayed_id = entry_id + index;
			this->root()->_jsons.erase(this->root()->_jsons.begin() + relayed_id);
			this->root()->_entries.erase(this->root()->_entries.begin() + relayed_id);
		}
	}
	protected:
	/**
	 * 指定位置にJSONエントリーを挿入
	 * @param begin_id 挿入開始位置
	 * @param begin_path 基準のJSONパス
	 * @param entry_json JSON
	 */
	void _insert_entry(int begin_id, const std::string& begin_path, std::shared_ptr<Json> entry_json) {
		// ルートではない場合、ルートオブジェクトに変換
		if (!entry_json->is_root()) {
			entry_json = entry_json->isolate();
		}
		// JSONエントリーを挿入
		for (auto i = 0; i < entry_json->root()->_entries.size(); i++) {
			JsonEntry org_entry = entry_json->root()->_entries[i];
			std::string new_path = i > 0 ? JsonParser::join_path(begin_path, org_entry.path) : begin_path;
			int new_entry_id = begin_id + i;
			this->root()->_jsons.insert(this->root()->_jsons.begin() + new_entry_id, this->root()->_make_for_entry(new_entry_id));
			this->root()->_entries.insert(this->root()->_entries.begin() + new_entry_id, JsonEntry::make(new_path, org_entry.entry_type, org_entry.entity));
		}
		// 挿入位置の末尾から先の既存要素のエントリーIDを修正
		int post_id = begin_id + entry_json->root()->_entries.size();
		int remain = this->root()->_entries.size() - post_id;
		for (auto i = 0; i < remain; i++) {
			int new_entry_id = post_id + i;
			Json* in_entry_json = this->_at_json(new_entry_id);
			in_entry_json->_entry_id = new_entry_id;
		}
	}
	public:
	/**
	 * 自身を基点に新たなインスタンスを生成
	 * @return インスタンス
	 * @note
	 * ```
	 * * ルート要素との参照を切り離すことでメモリー安全な複製として利用可能する
	 * * 引数として渡す際に有効である反面、実行速度とメモリー効率を犠牲にする
	 * ```
	 */
	std::shared_ptr<Json> isolate() {
		std::shared_ptr<Json> instance = std::make_shared<Json>();
		auto [jsons, entries] = this->_isolate_entries(instance);
		instance->_jsons = jsons;
		instance->_entries = entries;
		return instance;
	}
	protected:
	/**
	 * 自身を含めた全ての下位要素を新たなエントリーとして生成
	 * @param new_root ルートオブジェクト
	 * @return JSON, JSONエントリーリスト
	 */
	std::tuple<std::vector<std::shared_ptr<Json>>, std::vector<JsonEntry>> _isolate_entries(std::shared_ptr<Json> new_root) {
		std::vector<std::shared_ptr<Json>> jsons = {};
		std::vector<JsonEntry> entries = {};
		std::vector<int> ids = this->_relayed_entry_ids(this->_entry_id);
		int new_entry_id = 0;
		for (auto& entry_id : ids) {
			JsonEntry entry = this->root()->_entries[entry_id];
			std::string new_path = new_entry_id > 0 ? entry.path.substr(this->path().size() + 1, entry.path.size() - (this->path().size() + 1)) : "";
			jsons.push_back(new_root->_make_for_entry(new_entry_id));
			entries.push_back(JsonEntry::make(new_path, entry.entry_type, entry.entity));
			new_entry_id++;
		}
		return {jsons, entries};
	}
	protected:
	/**
	 * 指定位置のJSONエントリーを含めた全ての下位要素のエントリーIDを抽出
	 * @param entry_id エントリーID
	 * @return エントリーIDリスト
	 */
	std::vector<int> _relayed_entry_ids(int entry_id) {
		std::vector<int> ids = {};
		int remain = this->root()->_entries.size() - entry_id;
		for (auto i = 0; i < remain; i++) {
			int in_entry_id = i + this->_entry_id;
			std::string path = this->root()->_entries[in_entry_id].path;
			if (this->_starts_with(path, this->path())) {
				ids.push_back(in_entry_id);
			}
		}
		return ids;
	}
	protected:
	/**
	 * 文字列が接頭辞から始まるか判定
	 * @param string 文字列
	 * @param prefix 接頭辞
	 * @return True = 適合
	 * @note XXX C++だと空文字を全く検証せず、ルート要素との比較をスキップしてしまうため、互換用に用意
	 */
	bool _starts_with(const std::string& string, const std::string& prefix) {
		return prefix.size() == 0 || string.starts_with(prefix);
	}
	public:
	/**
	 * 文字列表現を取得
	 * @return 文字列表現
	 */
	std::string to_string() {
		if (this->scalar_with(JsonEntryTypes::Boolean)) {
			return this->as_bool() ? "true" : "false";
		} else if (this->scalar_with(JsonEntryTypes::Number)) {
			return std::to_string(this->as_number());
		} else if (this->scalar_with(JsonEntryTypes::String)) {
			return std::format("\"%s\"", (String::escape(this->as_string(), '"')).c_str());
		} else if (this->entry_type() == JsonEntryTypes::Array) {
			std::vector<std::string> values = [&]() -> std::vector<std::string> {
				std::vector<std::string> __ret;
				for (auto under : this->unders()) {
					__ret.push_back(under->to_string());
				}
				return __ret;
			}();
			std::string join_values = ",".join(values);
			return "[" + join_values + "]";
		} else {
			std::vector<std::string> values = [&]() -> std::vector<std::string> {
				std::vector<std::string> __ret;
				for (auto under : this->unders()) {
					__ret.push_back(std::format("\"%s\":%s", (under->symbol()).c_str(), (under->to_string()).c_str()));
				}
				return __ret;
			}();
			std::string join_values = ",".join(values);
			return "{" + join_values + "}";
		}
	}
};
