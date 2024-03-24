class BlockExpects:
	DeclOps = """/** DeclOps */
class DeclOps {
	public: static Sub* class_bp = nullptr;
	public: static std::map<std::string, std::map<std::string, std::vector<int>>> class_map = {{"a", {{"b", {1}}}}};
	public: Sub* inst_var;
	/** Constructor */
	public: DeclOps() : inst_var(nullptr) {
	}
};"""

	CompOps_list_comp_assign_values1 = \
"""std::vector<int> values1 = [this, &]() -> std::vector<int> {
	std::vector<int> __ret;
	for (auto& value : values0) {
		__ret.push_back(value);
	}
	return __ret;
}();"""

	CompOps_dict_comp_assign_kvs1 = \
"""std::map<std::string, CompOps::C> kvs1 = [this, &]() -> std::map<std::string, CompOps::C> {
	std::map<std::string, CompOps::C> __ret;
	for (auto& [key, value] : kvs0) {
		__ret[key] = value;
	}
	return __ret;
}();"""

	ForOps_enumerate_for_index_key = \
"""for (auto& [index, key] : [&]() -> std::map<int, std::string> {
	std::map<int, std::string> __ret;
	int __index = 0;
	for (auto& __entry : keys) {
		__ret[__index++] = __entry;
	}
	return __ret;
}()) {

}"""

	ListOps_pop_assign_value0 = \
"""int value0 = [&]() -> int {
	auto __iter = values.begin() + 1;
	auto __copy = *__iter;
	values.erase(__iter);
	return __copy;
}();"""

	ListOps_pop_assign_value1 = \
"""int value1 = [&]() -> int {
	auto __iter = values.end() - 1;
	auto __copy = *__iter;
	values.erase(__iter);
	return __copy;
}();"""

	DictOps_pop_assign_value0 = \
"""int value0 = [&]() -> int {
	auto __copy = values["a"];
	values.erase("a");
	return __copy;
}();"""

	DictOps_pop_assign_value1 = \
"""int value1 = [&]() -> int {
	auto __copy = values["b"];
	values.erase("b");
	return __copy;
}();"""

	DictOps_keys_assign_keys = \
"""std::vector<std::string> keys = [&]() -> std::vector<std::string> {
	std::vector<std::string> __ret;
	for (auto [__key, _] : kvs) {
		__ret.push_back(__key);
	}
	return __ret;
}();"""

	DictOps_values_assign_values = \
"""std::vector<int> values = [&]() -> std::vector<int> {
	std::vector<int> __ret;
	for (auto [_, __value] : kvs) {
		__ret.push_back(__value);
	}
	return __ret;
}();"""
