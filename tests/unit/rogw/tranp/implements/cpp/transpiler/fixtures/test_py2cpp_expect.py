class BlockExpects:
	DeclOps = """/** DeclOps */
class DeclOps {
	public: static Sub* class_bp = nullptr;
	public: static std::map<std::string, std::map<std::string, std::vector<int*>>> class_map = {{"a", {{"b", {}}}}};
	public: Sub* inst_var;
	public: std::vector<int*> inst_arr;
	public: std::map<std::string, int*> inst_map;
	public:
	/** __init__ */
	DeclOps() : inst_var(nullptr), inst_arr({}), inst_map({}) {
	}
	public:
	/** prop */
	int prop() {
		return 1;
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

	CompOps_dict_comp_assign_kvs0_1 = \
"""std::map<std::string, CompOps::C> kvs0_1 = [this, &]() -> std::map<std::string, CompOps::C> {
	std::map<std::string, CompOps::C> __ret;
	for (auto& [key, value] : kvs0_0) {
		__ret[key] = value;
	}
	return __ret;
}();"""

	CompOps_dict_comp_assign_kvsp_1 = \
"""std::map<std::string, CompOps::C> kvsp_1 = [this, &]() -> std::map<std::string, CompOps::C> {
	std::map<std::string, CompOps::C> __ret;
	for (auto& [key, value] : *(kvsp_0)) {
		__ret[key] = value;
	}
	return __ret;
}();"""

	CompOps_dict_comp_assign_kvs2 = \
"""std::map<int, int> kvs2 = [this, &]() -> std::map<int, int> {
	std::map<int, int> __ret;
	for (auto& in_values : values) {
		__ret[in_values[0]] = in_values[1];
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

	ListOps_slice_assign_ns0 = \
"""std::vector<int> ns0 = [&]() -> std::vector<int> {
	std::vector<int> __ret;
	int __index = 0;
	int __start = 1;
	int __end = ns.size() - __start;
	int __step = 0;
	for (auto& __value : ns) {
		int __offset = __index >= __start ? __index - __start : 0;
		if (__index >= __start && __index < __end && (__step > 0 && __offset % __step == 0)) {
			__ret.push_back(__value);
		}
		__index++;
	}
	return __ret;
}();"""

	ListOps_slice_assign_ns1 = \
"""std::vector<int> ns1 = [&]() -> std::vector<int> {
	std::vector<int> __ret;
	int __index = 0;
	int __start = 0;
	int __end = 5 - __start;
	int __step = 0;
	for (auto& __value : ns) {
		int __offset = __index >= __start ? __index - __start : 0;
		if (__index >= __start && __index < __end && (__step > 0 && __offset % __step == 0)) {
			__ret.push_back(__value);
		}
		__index++;
	}
	return __ret;
}();"""

	ListOps_slice_assign_ns2 = \
"""std::vector<int> ns2 = [&]() -> std::vector<int> {
	std::vector<int> __ret;
	int __index = 0;
	int __start = 3;
	int __end = 9 - __start;
	int __step = 2;
	for (auto& __value : ns) {
		int __offset = __index >= __start ? __index - __start : 0;
		if (__index >= __start && __index < __end && (__step > 0 && __offset % __step == 0)) {
			__ret.push_back(__value);
		}
		__index++;
	}
	return __ret;
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
	for (auto& [__key, _] : kvs) {
		__ret.push_back(__key);
	}
	return __ret;
}();"""

	DictOps_values_assign_values = \
"""std::vector<int> values = [&]() -> std::vector<int> {
	std::vector<int> __ret;
	for (auto& [_, __value] : kvs) {
		__ret.push_back(__value);
	}
	return __ret;
}();"""
