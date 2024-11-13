class BlockExpects:
	DeclOps = """/** DeclOps */
class DeclOps {
	public: inline static Sub* class_bp = nullptr;
	public: inline static std::map<std::string, std::map<std::string, std::vector<int*>>> class_map = {{"a", {{"b", {}}}}};
	public: Sub* inst_var0;
	public: Sub inst_var1;
	public: std::vector<int*> inst_arr;
	public: std::map<std::string, int*> inst_map;
	public: std::vector<TSII> inst_tsiis;
	public:
	/** __init__ */
	DeclOps() : inst_var0(nullptr), inst_var1({}), inst_arr({}), inst_map({}), inst_tsiis({}) {
		int n = this->prop();
	}
	public:
	/** prop */
	int prop() {
		return 1;
	}
};"""

	CompOps_list_comp_assign_values1 = \
"""std::vector<int> values1 = [&]() -> std::vector<int> {
	std::vector<int> __ret;
	for (auto& value : values0) {
		__ret.push_back(value);
	}
	return __ret;
}();"""

	CompOps_dict_comp_assign_kvs0_1 = \
"""std::map<std::string, CompOps::C> kvs0_1 = [&]() -> std::map<std::string, CompOps::C> {
	std::map<std::string, CompOps::C> __ret;
	for (auto& [key, value] : kvs0_0) {
		__ret[key] = value;
	}
	return __ret;
}();"""

	CompOps_dict_comp_assign_kvsp_1 = \
"""std::map<std::string, CompOps::C> kvsp_1 = [&]() -> std::map<std::string, CompOps::C> {
	std::map<std::string, CompOps::C> __ret;
	for (auto& [key, value] : *(kvsp_0)) {
		__ret[key] = value;
	}
	return __ret;
}();"""

	CompOps_dict_comp_assign_kvs2 = \
"""std::map<int, int> kvs2 = [&]() -> std::map<int, int> {
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
	int __end = ns.size();
	int __step = 0;
	for (auto& __value : ns) {
		int __offset = __index >= __start ? __index - __start : 0;
		if (__index >= __start && __index < __end && (__step == 0 || __offset % __step == 0)) {
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
	int __end = 5;
	int __step = 0;
	for (auto& __value : ns) {
		int __offset = __index >= __start ? __index - __start : 0;
		if (__index >= __start && __index < __end && (__step == 0 || __offset % __step == 0)) {
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
	int __end = 9;
	int __step = 2;
	for (auto& __value : ns) {
		int __offset = __index >= __start ? __index - __start : 0;
		if (__index >= __start && __index < __end && (__step == 0 || __offset % __step == 0)) {
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

	ForTemplateClass_Delegate = \
"""/** Delegate */
template<typename ...TArgs>
class Delegate {
	public:
	/** bind */
	template<typename T>
	void bind(T* obj, const typename PluckMethod<T, void, TArgs...>::method& method) {}
	public:
	/** invoke */
	void invoke(TArgs... args) {}
};"""

	@classmethod
	def for_enumerate(cls, key: str, value: str, iterates: str, var_type: str, statements: list[str]) -> str:
		return '\n'.join([
			f'for (auto& [{key}, {value}] : [&]() -> std::map<int, {var_type}> ' '{',
			f'	std::map<int, {var_type}> __ret;',
			'	int __index = 0;',
			f'	for (auto& __entry : {iterates}) ' '{',
			'		__ret[__index++] = __entry;',
			'	}',
			'	return __ret;',
			'}()) {',
			'\n'.join(statements),
			'}',
		])

	@classmethod
	def for_values(cls, value: str, iterates: str, var_type: str, statements: list[str]) -> str:
		return '\n'.join([
			f'for (auto& {value} : [&]() -> std::vector<{var_type}> ' '{',
			f'	std::vector<{var_type}> __ret;',
			f'	for (auto& [_, __value] : {iterates}) ' '{',
			'		__ret.push_back(__value);',
			'	}',
			'	return __ret;',
			'}()) {',
			'\n'.join(statements),
			'}',
		])
