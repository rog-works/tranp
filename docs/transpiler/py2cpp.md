トランスパイラー / Python to C++
===

# 概要

* Python to C++特有のルール、各種フックやテクニックの紹介

# 一般

## クラス

```python
class A:
  cls_n: ClassVar = 0
  n: int

  def __init__(self, n: int) -> None:
    self.n = n
```
↓
```cpp
class A {
public: inline static int cls_n = 0;
public: int n;
public:
  A(int n) : n(n) {}
};
```

## C++型変数

|型名|不変型|C++|概要|
|------|-----------|----------------------|---|
| CP   | CPConst   | `T*`                 |ポインター|
| CW   | -         | `T*`                 |ポインター(Pythonでは弱参照)|
| CSP  | CSPConst  | `std::shared_ptr<T>` |強参照|
| CWP  | -         | `std::weak_ptr<T>`   |弱参照(Pythonでも弱参照)|
| CUP  | CUPConst  | `std::unique_ptr<T>` |ユニークポインター|
| CRef | CRefConst | `T&`                 |参照|

```python
p = CP.new(0)
p_weak = CW(p)
shared = CSP(p)
weak = shared.weak
unique = CUP.new(1)
ref = p.ref
ref_const = ref.const
```
↓
```cpp
int* p = new int(0)
int* p_weak = p;
std::shared_ptr<int> shared = std::shared_ptr<int>(p);
std::weak_ptr<int> weak = shared.to_weak();
std::unique_ptr<int> unique = std::make_unique<int>(1);
int& ref = *p;
const int& ref_const = ref;
```

## 配列・連想配列

```python
numbers = [1, 2, 3]
str_to_int = {'n': 1}
```
↓
```cpp
std::vector<int> numbers{{1}, {2}, {3}};
std::map<std::string, int> str_to_int{{"n", 1}};
```

## クロージャー・ラムダ

```python
def closure() -> int:
  return 0

func: Callable[[], None] = lambda: print('bar')
```
↓
```cpp
std::function<int()> closure = []() -> int { return 0; };
std::function<void()> func = []() -> void { printf("bar"); };
```

## 文字列展開

```python
s = 'b: {b}, n: {n}, f: {f}, s: {s}'.format(b=True, n=1, f=1.0, s='bar')
```
↓
```cpp
std::string s = std::format('b: %d, n: %d, f: %f, s: %s', true, 1, 1.0f, std::string("bar").c_str());
```

# アノテーション

## エイリアス

```python
from tranp.app.compatible.python.embed import Embed

@Embed.alias('A2')
class A: ...
```
↓
```cpp
class A2 {};
```

## ローカルスタティック変数

```python
from tranp.app.compatible.python.embed import Embed

def func(index: int) -> str:
  strings = Embed.static(func).decl(lambda: {0: 'a', 1: 'b', 2: 'c'})
  return strings[index]
```
↓
```cpp
std::string func(int index) {
  static std::map<int, std::string> strings = {{0, "a"}, {1, "b"}, {2, "c"}};
  return strings[index];
}
```
