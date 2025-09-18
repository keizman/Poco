# Android UIAutomator2 Poco Driver 使用参考

## 概述

本文档详细说明了 Android UIAutomator2 Poco Driver 支持的所有元素选择器和操作方法。

## 支持的元素选择器属性

### 基础属性

| 属性名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| `text` | string | 元素的文本内容 | `poco(text="登录")` |
| `name` | string | 元素名称(fallback到text或class) | `poco(name="button1")` |
| `type` | string | 元素类型(映射到class属性) | `poco(type="android.widget.Button")` |
| `class_name` | string | 元素的完整类名 | `poco(class_name="android.widget.EditText")` |
| `resourceId` | string | Android资源ID | `poco(resourceId="com.app:id/login_btn")` |
| `package` | string | 应用包名 | `poco(package="com.example.app")` |
| `contentDesc` | string | 内容描述(accessibility) | `poco(contentDesc="关闭按钮")` |

### 状态属性

| 属性名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| `clickable` | boolean | 是否可点击 | `poco(clickable=True)` |
| `focusable` | boolean | 是否可获得焦点 | `poco(focusable=True)` |
| `focused` | boolean | 是否已获得焦点 | `poco(focused=True)` |
| `enabled` | boolean | 是否启用 | `poco(enabled=True)` |
| `visible` | boolean | 是否对用户可见 | `poco(visible=True)` |
| `selected` | boolean | 是否已选择 | `poco(selected=True)` |
| `scrollable` | boolean | 是否可滚动 | `poco(scrollable=True)` |
| `checkable` | boolean | 是否可勾选 | `poco(checkable=True)` |
| `checked` | boolean | 是否已勾选 | `poco(checked=True)` |
| `longClickable` | boolean | 是否支持长按 | `poco(longClickable=True)` |
| `editable` | boolean | 是否可编辑(从类名推断) | `poco(editable=True)` |

### 位置属性

| 属性名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| `bounds` | array | 元素边界坐标(归一化) | `poco(bounds=[0.1, 0.2, 0.9, 0.8])` |
| `pos` | array | 元素中心位置(归一化) | N/A (只读属性) |
| `size` | array | 元素大小(归一化) | N/A (只读属性) |

## 支持的元素操作

### 1. 点击操作

```python
# 基础点击
poco(resourceId="com.app:id/button").click()

# 带偏移的点击
poco(text="登录").click([0.5, 0.5])  # 点击元素中心
poco(text="登录").click([0.8, 0.2])  # 点击元素右上角

# 长按
poco(text="选项").long_click()
poco(text="选项").long_click(duration=2.0)  # 长按2秒
```

### 2. 文本输入操作

```python
# 设置文本(覆盖原有内容)
poco(class_name="android.widget.EditText").set_text("新文本")
poco(resourceId="com.app:id/search_input").set_text("搜索关键词")

# 获取文本
text = poco(resourceId="com.app:id/title").get_text()
```

### 3. 滑动操作

```python
# 滑动到另一个元素
poco(text="起点").swipe_to(poco(text="终点"))

# 按方向滑动
poco(text="列表项").swipe("up")    # 向上滑动
poco(text="列表项").swipe("down")  # 向下滑动
poco(text="列表项").swipe("left")  # 向左滑动
poco(text="列表项").swipe("right") # 向右滑动

# 自定义滑动
poco(resourceId="com.app:id/container").swipe([0.5, 0.8], [0.5, 0.2])  # 从下往上滑动
```

### 4. 拖拽操作

```python
# 拖拽到另一个元素
poco(text="拖拽源").drag_to(poco(text="拖拽目标"))

# 拖拽到指定位置
poco(text="图标").drag_to([0.8, 0.2])  # 拖拽到屏幕右上角
```

### 5. 滚动操作

```python
# 滚动容器
poco(scrollable=True).scroll("vertical")    # 垂直滚动
poco(scrollable=True).scroll("horizontal")  # 水平滚动

# 滚动到指定元素可见
poco(scrollable=True).scroll_to(poco(text="目标元素"))
```

### 6. 等待操作

```python
# 等待元素出现
poco(text="加载完成").wait_for_appearance(timeout=10)

# 等待元素消失
poco(text="加载中...").wait_for_disappearance(timeout=30)

# 等待元素变为指定状态
poco(resourceId="com.app:id/button").wait(visible=True, timeout=5)
```

### 7. 状态查询

```python
# 检查元素是否存在
exists = poco(text="登录").exists()

# 获取元素属性
clickable = poco(resourceId="com.app:id/btn").attr("clickable")
text_content = poco(resourceId="com.app:id/label").attr("text")
class_name = poco(resourceId="com.app:id/view").attr("class_name")

# 获取元素位置和大小
pos = poco(text="按钮").get_position()     # 返回 [x, y]
size = poco(text="按钮").get_size()       # 返回 [width, height]
bounds = poco(text="按钮").get_bounds()   # 返回 [x1, y1, x2, y2]
```

## 元素选择器组合

### 逻辑组合

```python
# 多属性组合(AND逻辑)
poco(class_name="android.widget.EditText", clickable=True, enabled=True)

# 使用父子关系
poco("LoginForm").child("Button")                    # 直接子元素
poco("Container").offspring("EditText")              # 所有后代元素
poco("ListView").child().child("TextView")           # 孙子元素

# 使用兄弟关系
poco(text="用户名").sibling("EditText")              # 兄弟元素

# 使用索引选择
poco(class_name="android.widget.Button")[0]         # 第一个按钮
poco(class_name="android.widget.Button")[1]         # 第二个按钮
poco(class_name="android.widget.Button")[-1]        # 最后一个按钮
```

### 模糊匹配

```python
# 文本模糊匹配
poco(textMatches=".*登录.*")                         # 包含"登录"的文本
poco(textMatches="^开始.*")                          # 以"开始"开头的文本

# 资源ID模糊匹配
poco(resourceIdMatches=".*login.*")                  # 包含"login"的资源ID
```

## 最佳实践

### 1. 选择器优先级

1. **resourceId** (最稳定) - 推荐首选
2. **text** (较稳定) - 适合有明确文本的元素
3. **class_name + 其他属性** (中等稳定) - 组合使用提高准确性
4. **contentDesc** (中等稳定) - 适合无文本但有描述的元素
5. **位置坐标** (最不稳定) - 仅作最后选择

### 2. 错误处理

```python
try:
    # 使用主要选择器
    poco(resourceId="com.app:id/login_btn").click()
except PocoNoSuchNodeException:
    # 使用备用选择器
    poco(text="登录").click()
```

### 3. 等待策略

```python
# 操作前确保元素可见和可用
element = poco(resourceId="com.app:id/button")
element.wait_for_appearance(timeout=10)
if element.attr("enabled"):
    element.click()
```

## 常见问题解决

### 1. 元素定位失败

**原因**: 属性映射问题、时序问题、可见性问题
**解决**:
- 使用更稳定的选择器(resourceId)
- 添加等待时间
- 检查元素是否被遮挡

### 2. 操作失败

**原因**: 元素不可操作、状态不正确
**解决**:
- 检查元素的clickable、enabled等状态
- 确保元素完全可见
- 使用适当的等待时间

### 3. 性能问题

**原因**: 复杂选择器、频繁查询
**解决**:
- 使用简单明确的选择器
- 缓存常用的元素引用
- 避免深层嵌套查询

## 版本更新说明

### v1.1.0 (当前版本)
- 修复了 `class_name` 属性映射问题
- 新增了 `contentDesc` 属性支持
- 完善了属性列表文档

### 已知限制

1. `touchable` 属性映射到 `clickable`(UIAutomator2无原生touchable)
2. `editable` 属性通过类名推断(检查是否包含EditText)
3. `dismissable` 属性不支持(UIAutomator2无此属性)
4. 坐标系统使用归一化坐标(0-1范围)

## 参考资料

- [Poco官方文档](https://poco.readthedocs.io/)
- [Android UIAutomator2文档](https://github.com/openatx/uiautomator2)
- [元素选择器最佳实践指南](https://poco-chinese.readthedocs.io/zh_CN/latest/source/doc/poco-example/index.html)