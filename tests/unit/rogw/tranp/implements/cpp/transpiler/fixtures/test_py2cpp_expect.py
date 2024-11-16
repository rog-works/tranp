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

	@classmethod
	def list_slice(cls, symbol: str, begin: str, end: str, step: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> std::vector<{var_type}> ' '{',
			f'	std::vector<{var_type}> __ret;',
			f'	auto __begin = {symbol}.begin();',
			f'	auto __end = {end if end else f"{symbol}.size()"};',
			f'	for (auto __index = {begin if begin else "0"}; __index < __end; __index += {step if step else "1"}) ' '{',
			'		__ret.push_back(*(__begin + __index));',
			'	}',
			'	return __ret;',
			'}();',
		])

	@classmethod
	def list_pop(cls, symbol: str, index: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> {var_type} ' '{',
			f'	auto __iter = {symbol}' + (f'.begin() + {index};' if index else '.end() - 1;'),
			'	auto __copy = *__iter;',
			f'	{symbol}.erase(__iter);',
			'	return __copy;',
			'}();',
		])

	@classmethod
	def list_values(cls, symbol: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> std::vector<{var_type}> ' '{',
			f'	std::vector<{var_type}> __ret;',
			f'	for (auto& __value : {symbol}) ' '{',
			'		__ret.push_back(__value);',
			'	}',
			'	return __ret;',
			'}();'
		])

	@classmethod
	def dict_pop(cls, symbol: str, key: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> {var_type} ' '{',
			f'	auto __copy = {symbol}[{key}];',
			f'	{symbol}.erase({key});',
			'	return __copy;',
			'}();',
		])

	@classmethod
	def dict_keys(cls, symbol: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> std::vector<{var_type}> ' '{',
			f'	std::vector<{var_type}> __ret;',
			f'	for (auto& [__key, _] : {symbol}) ' '{',
			'		__ret.push_back(__key);',
			'	}',
			'	return __ret;',
			'}();'
		])

	@classmethod
	def dict_values(cls, symbol: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> std::vector<{var_type}> ' '{',
			f'	std::vector<{var_type}> __ret;',
			f'	for (auto& [_, __value] : {symbol}) ' '{',
			'		__ret.push_back(__value);',
			'	}',
			'	return __ret;',
			'}();'
		])

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
