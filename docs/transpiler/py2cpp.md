トランスパイラー / Python to C++
===

# 概要

* Python to C++特有のルール、技術的なトピックの紹介

# インデックス

* [記述ルール](#記述ルール)
  * [型注釈](#型注釈)
  * [インポート](#インポート)
* [一般](#一般)
  * [クラス](#クラス)
  * [Enum](#Enum)
  * [ジェネリック](#ジェネリック)
  * [型エイリアス](#型エイリアス)
  * [C++型変数](#c型変数)
  * [for文](#for文)
  * [文字・文字列](#文字文字列)
  * [配列・連想配列](#配列連想配列)
  * [クロージャー・ラムダ](#クロージャーラムダ)
  * [文字列展開](#文字列展開)
* [アノテーション](#アノテーション)
  * [エイリアス](#エイリアス)
  * [インターフェイス・抽象型](#インターフェイス抽象型)
  * [構造体・ユニオン](#構造体ユニオン)
  * [出力除外](#出力除外)
  * [継承除外](#継承除外)
  * [関数シグネチャー](#関数シグネチャー)
  * [不変型](#不変型)
  * [暗黙的不変型の解除](#暗黙的不変型の解除)
  * [関数ローカルスタティック変数](#関数ローカルスタティック変数)

# 記述ルール

## 型注釈

* 基本的に必須
* 代入など、型推論可能な場合は省略可能

## インポート

* モジュール全体のインポートは不可

# 一般

## クラス

```python
from typing import ClassVar

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

## Enum

```python
from enum import Enum

class Values(Enum):
  A = 0
  B = 1

e = Values.A
value = Values.A.value
name = Values.A.name
```
↓
```cpp
enum class Values {
  A = 0,
  B = 1,
};
Values e = Values::A;
int value = 0;
std::string name = "A";
```

## ジェネリック

```python
# 関数
def gen[T](t: type[T]) -> T: ...

n = gen(int)

# クラス
class Gen[T]:
  value: T

  def __init__(self, value: T) -> None:
    self.value = value

g = Gen(0)
```
↓
```cpp
// 関数
<typename T>
T gen() { ... }
int n = gen<int>();
// クラス
<typename T>
class Gen {
public: T value;
public:
  Gen(T value) : value(value) {}
};
Gen<int> g = Gen(0);
```

## 型エイリアス

```python
from typing import TypeAlias

Int: TypeAlias = int
# NG: Int = int
# NG: type Int = int
```
↓
```cpp
using Int = int;
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
from tranp.app.compatible.cpp.cvar import CP, CSP, CW, CUP

# ポインター
p = CP.new(0)
p_weak = CW(p)
# スマートポインター
shared = CSP(p)
weak = shared.weak
unique = CUP.new(1)
# 参照
ref = p.ref
ref_const = ref.const
```
↓
```cpp
// ポインター
int* p = new int(0)
int* p_weak = p;
// スマートポインター
std::shared_ptr<int> shared = std::shared_ptr<int>(p);
std::weak_ptr<int> weak = shared.to_weak();
std::unique_ptr<int> unique = std::make_unique<int>(1);
// 参照
int& ref = *p;
const int& ref_const = ref;
```

## for文

```python
for i in range(10): ...
for value in values: ...
for index, value in enumerate(values): ...
```
↓
```cpp
for (auto i = 0; i < 10; i += 1) {}
for (auto value& : values) {}
int index = 0;
for (auto value& : values) {
  ...
  index += 1;
}
```

## 文字・文字列

```python
from tranp.app.compatible.cpp.classes import char

s = 'abc'
c = char('c')
```
↓
```cpp
std::string s = "abc";
char c = 'c';
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
from typing import Callable

def method(self) -> None:
  def closure() -> int:
    return self.n

  add: Callable[[int, int], int] = lambda a, b: a + b
  bind(lambda s: print('s: {s}'.format(s=s)))

def bind(self, callback: Callable[[str], None]) -> None: ...
def factory(n: int) -> Callable[[], int]:
  return lambda: n
```
↓
```cpp
#include <functional>
void method() {
  std::function<int()> closure = [this]() -> int { return this->n; };
  std::function<int(int, int)> add = [](int a, int b) -> int { return a + b; };
  bind([](std::string s) -> void { printf("s: %s", s.c_str()); });
}
void bind(std::function<void(std::string)>>& callback) {}
std::function<int()> factory(int n) {
  return [n]() -> int { return n; };
}
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
from typing import Annotated
from tranp.app.compatible.python.embed import Embed

@Embed.alias('A2')
class A:
  n: Annotated[int, Embed.alias('n2')]

  def __init__(self, n: int) -> None:
    self.n = n

  @Embed.alias('func2')
  def func(self) -> None: ...

@Embed.alias('A', prefix=True)
class B: ...
```
↓
```cpp
class A2 {
public: int n2;
public:
  A2(int n) n2(n) {}
  void func2() {}
};
class AB {};
```

## インターフェイス・抽象型

```python
from abc import abstracemethod, ABCMeta
from tranp.app.compatible.python.embed import Embed

class Interface(metaclass=ABCMeta):
  @Embed.allow_override
  def __py_destroy__(self) -> None: ...
  @abstractmethod
  def interface_func(self) -> int: ...

class Abstract:
  @Embed.allow_override
  def __py_destroy__(self) -> None: ...
  @abstractmethod
  def interface_func(self) -> int: ...
  @Embed.allow_override
  def abstract_func(self) -> int:
    return 1
```
↓
```cpp
class Interface {
public: virtual ~Interface() = default;
public: virtual int interface_func() = 0;
};
class Abstract {
public: virtual ~Abstract() = default;
public: virtual int interface_func() = 0;
public:
  virtual int abstract_func(self) {
    return 1;
  }
};
```

## 構造体・ユニオン

```python
from tranp.app.compatible.python.embed import Embed

@Embed.struct
class S: ...

@Embed.union
class U:
  b: bool
  n: int
  f: float

  @Embed.python
  def __init__(self) -> None:
    self.b = False
    self.n = 0
    self.f = 0.0
```
↓
```cpp
struct S {};
union U {
  bool b;
  int n;
  float f;
};
```

## 出力除外

```python
from enum import Enum
from tranp.app.compatible.python.embed import Embed

@Embed.python
class Values(Enum): ...

@Embed.python
def func() -> None:
  print('python')

@Embed.alias(func.__name__)
def func_cpp() -> None:
  print('cpp')

func()
```
↓
```cpp
void func() {
  printf("cpp");
}
func();
```

## 継承除外

```python
from tranp.app.compatible.python.embed import Embed

@Embed.ignore(OnPython)
class A(OnPython): ...
```
↓
```cpp
class A {};
```

## 関数シグネチャー

```python
from tranp.app.compatible.python.embed import Embed

class A:
  @Embed.pure
  def const_func(self) -> int: ...
  @Embed.public
  def __public_func(self) -> int: ...
```
↓
```cpp
class A {
public: int const_func() const { ... }
public: int __public_func() { ... }
};
```

## 不変型

```python
from typing import Annotated
from tranp.app.compatible.python.embed import Embed

def func(obj: Annotated[Obj, Embed.immutable]) -> None: ...

const_n: Annotated[int, Embed.immutable] = 1
```
↓
```cpp
void func(const Obj& obj) {}
const int& const_n = 1;
```

## 暗黙的不変型の解除

```python
def sum(arr: list[int]) -> int: ...
def sum_alt(arr: Annotated[list[int], Embed.mutable]) -> int: ...
```
↓
```cpp
int sum(const std::vector<int>& arr) { ... }
int sum_alt(std::vector<int> arr) { ... }
```

## 関数ローカルスタティック変数

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
