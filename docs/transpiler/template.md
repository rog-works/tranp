トランスパイラー / テンプレート
===

# 概要

* デフォルトのテンプレートエンジンはJinja2
* テンプレートエンジンは置き換え可能
* テンプレートの記述方法はテンプレートエンジン側の資料を参照

# カスタムヘルパーの登録

## コンフィグの設定

```yaml
di:
  tranp.app.view.render.RendererHelperProvider: view.helper.my_helper_provider
```

## ヘルパープロバイダーの実装

```python
# view.helper.py
from tranp.app.implements.cpp.view.cpp_view_helper import factories_for_cpp
from tranp.app.view.helper.helper import factories
from tranp.app.view.render import RendererHelperProvider, RendererSetting

def custom_function(setting: RendererSetting) -> Callable[[str], str]:
  return lambda string: ...

def custom_filter(setting: RendererSetting) -> Callable[[list[str]], list[str]]:
  return lambda strings: ...

def my_helper_provider() -> RenderHelperProvider:
  funcs, filters = factories()
  funcs_cpp, filters_cpp = factories_for_cpp()
  return lambda: ([*funcs, *funcs_cpp, custom_function], [*filters, *filters_cpp, custom_filter])
```
