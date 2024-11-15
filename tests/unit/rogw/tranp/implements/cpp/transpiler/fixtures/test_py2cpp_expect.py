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
	def for_enumerate(cls, index: str, value: str, iterates: str, statements: list[str]) -> str:
		return '\n'.join([
			f'int {index} = 0;',
			f'for (auto& {value} : {iterates}) ' '{',
			f'	{"\n".join(statements)}' if len(statements) else '',
			f'	{index}++;',
			'}',
		])

	@classmethod
	def list_comp(cls, proj_value: str, proj_type: str, iterates: str, proj_symbols: str = '', proj_infer: str = 'auto&') -> str:
		return '\n'.join([
			f'[&]() -> std::vector<{proj_type}> ' '{',
			f'	std::vector<{proj_type}> __ret;',
			f'	for ({proj_infer} {proj_symbols or proj_value} : {iterates}) ' '{',
			f'		__ret.push_back({proj_value});',
			'	}',
			'	return __ret;',
			'}()',
		])

	@classmethod
	def dict_comp(cls, proj_key: str, proj_value: str, proj_key_type: str, proj_value_type: str, iterates: str, proj_symbols: str, proj_infer: str = 'auto&') -> str:
		return '\n'.join([
			f'[&]() -> std::map<{proj_key_type}, {proj_value_type}> ' '{',
			f'	std::map<{proj_key_type}, {proj_value_type}> __ret;',
			f'	for ({proj_infer} {proj_symbols} : {iterates}) ' '{',
			f'		__ret[{proj_key}] = {proj_value};',
			'	}',
			'	return __ret;',
			'}()',
		])
