class BlockExpects:
	@classmethod
	def class_method(cls, access: str, name: str, return_type: str, params: list[str] = [], statements: list[str] = [], pure: bool = False, template: str = '') -> str:
		return cls.method(access, name, return_type, params, statements, pure, template, prop=False, static=True)

	@classmethod
	def method(cls, access: str, name: str, return_type: str = 'void', params: list[str] = [], statements: list[str] = [], pure: bool = False, template: str = '', prop: bool = False, static: bool = False) -> str:
		lines: list[str] = []
		if statements:
			lines = [
				f'{access}:',
				f'/** {name} */',
				f'template<typename {template}>' if template else '',
				f'{"static " if static else ""}{return_type} {name}({", ".join(params)}) {"const " if pure else ""}' '{',
				f'	{"\n\t".join(statements)}',
				'}',
			]
		else:
			lines = [
				f'{access}:',
				f'/** {name} */',
				f'template<typename {template}>' if template else '',
				f'{"static " if static else ""}{return_type} {name}({", ".join(params)}) {"const " if pure else ""}' '{}',
			]

		return '\n'.join([line for line in lines if line])

	@classmethod
	def list_slice(cls, symbol: str, begin: str, end: str, step: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> std::vector<{var_type}> ' '{',
			f'	std::vector<{var_type}> l_ret;',
			f'	auto l_begin = {symbol}.begin();',
			f'	auto l_end = {end if end else f"{symbol}.size()"};',
			f'	for (auto l_index = {begin if begin else "0"}; l_index < l_end; l_index += {step if step else "1"}) ' '{',
			'		l_ret.push_back(*(l_begin + l_index));',
			'	}',
			'	return l_ret;',
			'}();',
		])

	@classmethod
	def list_pop(cls, symbol: str, index: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> {var_type} ' '{',
			f'	auto l_iter = {symbol}' + (f'.begin() + {index};' if index else '.end() - 1;'),
			'	auto l_copy = *l_iter;',
			f'	{symbol}.erase(l_iter);',
			'	return l_copy;',
			'}();',
		])

	@classmethod
	def list_values(cls, symbol: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> std::vector<{var_type}> ' '{',
			f'	std::vector<{var_type}> l_ret;',
			f'	for (auto& l_value : {symbol}) ' '{',
			'		l_ret.push_back(l_value);',
			'	}',
			'	return l_ret;',
			'}();'
		])

	@classmethod
	def dict_pop(cls, symbol: str, key: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> {var_type} ' '{',
			f'	auto l_copy = {symbol}[{key}];',
			f'	{symbol}.erase({key});',
			'	return l_copy;',
			'}();',
		])

	@classmethod
	def dict_keys(cls, symbol: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> std::vector<{var_type}> ' '{',
			f'	std::vector<{var_type}> l_ret;',
			f'	for (auto& [l_key, l_] : {symbol}) ' '{',
			'		l_ret.push_back(l_key);',
			'	}',
			'	return l_ret;',
			'}();'
		])

	@classmethod
	def dict_values(cls, symbol: str, var_type: str) -> str:
		return '\n'.join([
			f'[&]() -> std::vector<{var_type}> ' '{',
			f'	std::vector<{var_type}> l_ret;',
			f'	for (auto& [l_, l_value] : {symbol}) ' '{',
			'		l_ret.push_back(l_value);',
			'	}',
			'	return l_ret;',
			'}();'
		])

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
			f'	std::vector<{proj_type}> l_ret;',
			f'	for ({proj_infer} {proj_symbols or proj_value} : {iterates}) ' '{',
			f'		l_ret.push_back({proj_value});',
			'	}',
			'	return l_ret;',
			'}()',
		])

	@classmethod
	def list_comp_range(cls, proj_value: str, proj_type: str, size: str, proj_symbol: str) -> str:
		return '\n'.join([
			f'[&]() -> std::vector<{proj_type}> ' '{',
			f'	std::vector<{proj_type}> l_ret;',
			f'	for (auto {proj_symbol} = 0; {proj_symbol} < {size}; {proj_symbol}++) ' '{',
			f'		l_ret.push_back({proj_value});',
			'	}',
			'	return l_ret;',
			'}()',
		])

	@classmethod
	def list_comp_enumerate(cls, proj_value: str, proj_type: str, iterates: str, proj_symbols: list[str]) -> str:
		return '\n'.join([
			f'[&]() -> std::vector<{proj_type}> ' '{',
			f'	std::vector<{proj_type}> l_ret;',
			f'	for (auto [{proj_symbols[0]}, l_iter, l_end, {proj_symbols[1]}] = std::tuple' '{' f'0, {iterates}.begin(), {iterates}.end(), *({iterates}.begin())' '}' f'; l_iter < l_end; l_iter++, {proj_symbols[1]} = *l_iter) ' '{',
			f'		l_ret.push_back({proj_value});',
			'	}',
			'	return l_ret;',
			'}()',
		])

	@classmethod
	def dict_comp(cls, proj_key: str, proj_value: str, proj_key_type: str, proj_value_type: str, iterates: str, proj_symbols: str, proj_infer: str = 'auto&') -> str:
		return '\n'.join([
			f'[&]() -> std::map<{proj_key_type}, {proj_value_type}> ' '{',
			f'	std::map<{proj_key_type}, {proj_value_type}> l_ret;',
			f'	for ({proj_infer} {proj_symbols} : {iterates}) ' '{',
			f'		l_ret[{proj_key}] = {proj_value};',
			'	}',
			'	return l_ret;',
			'}()',
		])

	DeclOps = """/** DeclOps */
class DeclOps {
	public: inline static Sub* class_bp = nullptr;
	public: inline static std::map<std::string, std::map<std::string, std::vector<int*>>> class_map = {{"a", {{"b", {}}}}};
	protected: inline static int p_protected_class_n = 0;
	private: inline static int p__private_class_n = 0;
	public: Sub* inst_var0;
	public: Sub inst_var1;
	public: std::vector<int*> inst_arr;
	public: std::map<std::string, int*> inst_map;
	public: std::vector<TSII> inst_tsiis;
	protected: int p_protected_n;
	private: int p__private_n;
	public:
	/** __init__ */
	DeclOps() : inst_var0(nullptr), inst_var1{}, inst_arr{}, inst_map{}, inst_tsiis{}, p_protected_n(0), p__private_n(0) {
		void n = this->prop();
	}
	public:
	/** prop */
	void prop() {}
	protected:
	/** p_protected_prop */
	void p_protected_prop() {}
	private:
	/** p__private_prop */
	void p__private_prop() {}
};"""

	DeclProps = """public:
/** DeclProps */
class DeclProps : public DeclPropsBase {
	using DeclPropsBase::DeclPropsBase;
	public: inline static bool cls_b = true;
	public: inline static int cls_n = 0;
	public: std::map<std::string, int> move_dsn;
	public:
	/** __init__ */
	DeclProps(int n, const std::string& s) : DeclPropsBase(), move_dsn{{s, n}} {
		this->anno_n = std::stoi(s);
		this->move_s = std::to_string(n);
	}
};"""

	ForFunction_ModifierVars = """public:
/** Vars */
class Vars {
	public: int& r;
	public: const std::vector<int>& i;
	public:
	/** __init__ */
	Vars(int* n, const std::vector<int>& arr) : r((*(n))), i(arr) {}
};"""

	ForClass_AliasInner = """public:
/** Inner2 */
class Inner2 {
	public: inline static int V2 = 0;
	public: int n;
	public: std::string s;
	public:
	/** __init__ */
	Inner2() : n(0), s("1") {
		int ns = this->n + std::stoi(this->s);
	}
	public:
	/** func */
	void func() {}
};"""

	ForFlows_try_catch_throw = """try {
} catch (const std::runtime_error& e) {
	throw std::exception(std::format("%d", 1));
} catch (const std::exception& e) {
	throw e;
}"""

	ForFlows_if_isinstance = """if constexpr (std::is_same_v<T, int>) {
	return v;
} else if constexpr (std::is_same_v<T, std::string>) {
	return v;
} else {
	static_assert(std::is_same_v<T, void>, "Unmatch type");
}"""

	ForFlows_if_issubclass = """if constexpr (std::is_same_v<T, int>) {
	return (*(static_cast<T*>(p)));
} else if constexpr (std::is_same_v<T, std::string>) {
	return (*(static_cast<T*>(p)));
} else {
	static_assert(std::is_same_v<T, void>, "Unmatch type");
}"""

	ForTemplateClass_Delegate = """public:
/** Delegate */
template<typename ...T_Args>
class Delegate {
	public:
	/** bind */
	template<typename T>
	void bind(T* obj, const typename PluckMethod<T, void, T_Args...>::method& method) {}
	public:
	/** invoke */
	void invoke(T_Args... args) {}
};"""

	ForIteratorList = """public:
/** values */
std::vector<std::string>::iterator values() {
	return this->l.begin();
}"""

	ForIteratorList2 = """public:
/** numbers */
struct Iterator_numbers {
	const std::vector<std::tuple<std::string, int>>& lts;
	int index;
	Iterator_numbers(const std::vector<std::tuple<std::string, int>>& lts, int index) : lts(lts), index(index) {}
	bool operator!=(const Iterator_numbers& other) const { return this->index != other.index; }
	void operator++() { index += 1; }
	const int& operator*() const { return std::get<1>(this->lts[index]); }
	Iterator_numbers begin() const { return {this->lts, 0}; }
	Iterator_numbers end() const { return {this->lts, this->lts.size()}; }
};
Iterator_numbers numbers() {
	return {this->lts, 0};
}"""

	ForIteratorDict = """public:
/** items */
struct Iterator_items {
	std::map<std::string, int>* p_iterates;
	Iterator_items(std::map<std::string, int>* iterates) : p_iterates(iterates) {}
	std::map<std::string, int>::iterator begin() { return {this->p_iterates->begin()}; }
	std::map<std::string, int>::iterator end() { return {this->p_iterates->end()}; }
};
Iterator_items items() {
	return {&(this->d)};
}"""
