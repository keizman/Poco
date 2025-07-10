# Poco UI自动化测试工具使用指南 (tool.py)

本文档介绍了 `tool.py` 中提供的UI自动化测试工具集，基于Poco框架开发，主要功能包括坐标定位、元素跟踪和图像识别区域提取。

## 功能特性

- **坐标元素查找**：根据屏幕坐标查找UI元素信息
- **智能元素选择**：基于可见性、Z轴层级、交互性的多维度评估
- **元素跟踪**：记录元素信息，支持多种定位方式的智能切换
- **区域提取**：提取元素区域用于图像识别
- **截图保存**：自动裁剪并保存元素截图

## 安装依赖

```bash
pip install pocoui
# 如果需要图像处理功能
pip install Pillow
```

## 核心类说明

### CoordElementFinder - 坐标元素查找器

根据坐标查找UI元素，支持像素坐标和归一化坐标。

### ElementTracker - 元素跟踪器

跟踪UI元素信息，支持多种定位方式的智能切换。

### UIRegionExtractor - UI区域提取器

提取UI元素区域用于图像识别和截图保存。

## 使用示例

### 1. 基本坐标查找

```python
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from tool import CoordElementFinder

# 初始化Poco
poco = AndroidUiautomationPoco()

# 创建查找器
finder = CoordElementFinder(poco)

# 根据坐标查找元素
coord = [0.5, 0.3]  # 归一化坐标
element_info = finder.get_element_by_coord(coord)

if element_info:
    print(f"找到元素: {element_info['resourceId']}")
    print(f"文本内容: {element_info['text']}")
    print(f"元素类型: {element_info['type']}")
    print(f"是否可见: {element_info['visible']}")
    print(f"是否可点击: {element_info['touchable']}")
```

### 2. 元素跟踪和点击

```python
from tool import ElementTracker

# 创建跟踪器
tracker = ElementTracker(poco)

# 跟踪元素
coord = [0.2, 0.18]  # 按钮坐标
tracker.track_element_by_coord(coord, "login_button")

# 后续点击（会尝试多种定位方式）
success = tracker.click_tracked_element("login_button")

if success:
    print("元素点击成功")
else:
    print("元素点击失败")

# 查看所有跟踪的元素
tracked = tracker.get_tracked_elements()
print(f"已跟踪的元素: {list(tracked.keys())}")
```

### 3. 图像识别区域提取

```python
from tool import UIRegionExtractor

# 创建区域提取器
extractor = UIRegionExtractor(poco)

# 提取元素区域
coord = [0.2, 0.18]
region_info = extractor.extract_element_region(coord, padding=0.02)

if region_info:
    region = region_info['region']
    print(f"元素区域: 左={region['left']:.3f}, 上={region['top']:.3f}")
    print(f"区域尺寸: 宽={region['width']:.3f}, 高={region['height']:.3f}")
    
    # 获取像素区域（如果可用）
    if 'pixel_region' in region_info:
        pixel_region = region_info['pixel_region']
        print(f"像素区域: {pixel_region['left']}, {pixel_region['top']}, {pixel_region['right']}, {pixel_region['bottom']}")
```

### 4. 元素截图保存

```python
# 保存元素截图
coord = [0.2, 0.18]
filename = "element_screenshot.png"
success = extractor.save_element_screenshot(coord, filename, padding=0.01)

if success:
    print(f"截图已保存: {filename}")
```

### 5. 便捷函数使用

```python
from tool import find_element_by_coord, get_element_region_for_recognition, track_and_click_element

# 快速查找元素
element = find_element_by_coord(poco, [0.5, 0.3])

# 快速获取识别区域
region = get_element_region_for_recognition(poco, [0.5, 0.3], padding=0.02)

# 一键跟踪和点击
success = track_and_click_element(poco, [0.5, 0.3], "my_button")
```

## 实际应用场景

### 场景1：UI自动化录制回放

```python
# 录制阶段：记录用户点击的坐标
clicks = [
    ([0.2, 0.18], "featured_button"),
    ([0.5, 0.4], "search_button"),
    ([0.8, 0.6], "settings_button")
]

tracker = ElementTracker(poco)

# 跟踪所有点击的元素
for coord, name in clicks:
    tracker.track_element_by_coord(coord, name)

# 回放阶段：按顺序点击
for coord, name in clicks:
    tracker.click_tracked_element(name, fallback_coord=coord)
    time.sleep(1)  # 等待UI响应
```

### 场景2：图像识别辅助定位

```python
# 提取目标元素区域用于模板匹配
target_coord = [0.2, 0.18]
extractor = UIRegionExtractor(poco)

# 保存模板图像
template_file = "template.png"
extractor.save_element_screenshot(target_coord, template_file)

# 获取搜索区域
region_info = extractor.extract_element_region(target_coord, padding=0.05)
search_region = region_info['region']

print(f"在区域 {search_region} 内搜索模板 {template_file}")
```

### 场景3：动态UI元素定位

```python
# 处理动态变化的UI元素
def smart_click_element(coord, element_name):
    finder = CoordElementFinder(poco)
    tracker = ElementTracker(poco)
    
    # 首先尝试通过坐标查找
    element_info = finder.get_element_by_coord(coord)
    
    if element_info:
        # 如果找到元素，跟踪并点击
        tracker.track_element_by_coord(coord, element_name)
        return tracker.click_tracked_element(element_name, coord)
    else:
        # 如果找不到，直接点击坐标
        try:
            poco.click(coord)
            return True
        except:
            return False

# 使用示例
success = smart_click_element([0.2, 0.18], "dynamic_button")
```

## 注意事项

1. **坐标系统**：默认使用归一化坐标（0-1范围），也支持像素坐标转换
2. **元素优先级**：系统会自动选择最合适的元素（可见、可交互、层级高）
3. **多重定位**：跟踪器会尝试resourceId、name、text等多种定位方式
4. **异常处理**：所有功能都包含完善的异常处理机制
5. **性能考虑**：避免频繁获取UI层次结构，建议批量处理

## 扩展功能

如需添加新功能，可以继承现有类或创建新的工具类。例如：

```python
class CustomElementFinder(CoordElementFinder):
    def find_similar_elements(self, coord, similarity_threshold=0.8):
        # 自定义相似元素查找逻辑
        pass
```

更多详细信息请参考源代码注释和Poco官方文档。
--------
● 我来详细解释 best_match 的原理和 CoordElementFinder 的工作流程。

  best_match 的原理

  在UI自动化中，一个坐标点可能同时位于多个重叠的UI元素内，比如：
  - 一个按钮在父容器内
  - 父容器在根布局内
  - 可能还有透明的遮罩层

  best_match 通过多维度评分来选择最合适的元素：

  def priority_score(element):
      score = 0

      # 1. 可见性优先 (最重要)
      if element.get('visible', False):
          score += 1000  # 不可见元素基本不应该被选中

      # 2. Z轴层级 (层级越高越在前台)
      z_orders = element.get('zOrders', {})
      global_z = z_orders.get('global', 0)  # 全局层级
      local_z = z_orders.get('local', 0)    # 局部层级
      score += global_z * 100 + local_z * 10

      # 3. 可交互性 (可点击的元素更有价值)
      if element.get('touchable', False):
          score += 50

      # 4. 面积越小越精确 (避免选择大的容器)
      size = element.get('size', [0, 0])
      if size[0] > 0 and size[1] > 0:
          area = size[0] * size[1]
          score -= area * 10  # 负分，面积越小分数越高

      return score

  CoordElementFinder 工作流程

  CoordElementFinder 工作流程
  =====================================

  Input: coordinate [x, y]
           |
           v
      ┌─────────────────────────────────────┐
      │  1. 坐标预处理                        │
      │  ┌─────────────────────────────────┐  │
      │  │ pixel_coord? → normalized_coord │  │
      │  │ [800, 600] → [0.5, 0.4]        │  │
      │  └─────────────────────────────────┘  │
      └─────────────────────────────────────┘
           |
           v
      ┌─────────────────────────────────────┐
      │  2. 获取UI层次结构                    │
      │  ┌─────────────────────────────────┐  │
      │  │ poco.agent.hierarchy.dump()     │  │
      │  │                                 │  │
      │  │ Root                            │  │
      │  │ ├── Container1                  │  │
      │  │ │   ├── Button1                 │  │
      │  │ │   └── Label1                  │  │
      │  │ ├── Container2                  │  │
      │  │ │   ├── Button2                 │  │
      │  │ │   └── ImageView               │  │
      │  │ └── OverlayLayer                │  │
      │  │     └── PopupDialog             │  │
      │  └─────────────────────────────────┘  │
      └─────────────────────────────────────┘
           |
           v
      ┌─────────────────────────────────────┐
      │  3. 深度优先搜索 (DFS) 查找           │
      │  ┌─────────────────────────────────┐  │
      │  │ def traverse(node):             │  │
      │  │   if coord_in_element(coord):   │  │
      │  │     matches.append(node)        │  │
      │  │   for child in children:        │  │
      │  │     traverse(child)             │  │
      │  └─────────────────────────────────┘  │
      └─────────────────────────────────────┘
           |
           v
      ┌─────────────────────────────────────┐
      │  4. 边界检测算法                      │
      │  ┌─────────────────────────────────┐  │
      │  │ For each element:               │  │
      │  │                                 │  │
      │  │   pos = [cx, cy]  # 中心点       │  │
      │  │   size = [w, h]   # 尺寸         │  │
      │  │                                 │  │
      │  │   left = cx - w/2               │  │
      │  │   top = cy - h/2                │  │
      │  │   right = cx + w/2              │  │
      │  │   bottom = cy + h/2             │  │
      │  │                                 │  │
      │  │   if (left ≤ x ≤ right) and    │  │
      │  │      (top ≤ y ≤ bottom):       │  │
      │  │     → 匹配!                     │  │
      │  └─────────────────────────────────┘  │
      └─────────────────────────────────────┘
           |
           v
      ┌─────────────────────────────────────┐
      │  5. 收集所有匹配的元素                │
      │  ┌─────────────────────────────────┐  │
      │  │ matches = [                     │  │
      │  │   Container1,  # 大容器          │  │
      │  │   Button1,     # 目标按钮        │  │
      │  │   OverlayLayer # 透明遮罩        │  │
      │  │ ]                               │  │
      │  └─────────────────────────────────┘  │
      └─────────────────────────────────────┘
           |
           v
      ┌─────────────────────────────────────┐
      │  6. 多维度评分排序                    │
      │  ┌─────────────────────────────────┐  │
      │  │ Container1:                     │  │
      │  │   visible=True    → +1000       │  │
      │  │   zOrder=0        → +0          │  │
      │  │   touchable=False → +0          │  │
      │  │   area=0.5        → -5          │  │
      │  │   Total: 995                    │  │
      │  │                                 │  │
      │  │ Button1:                        │  │
      │  │   visible=True    → +1000       │  │
      │  │   zOrder=1        → +100        │  │
      │  │   touchable=True  → +50         │  │
      │  │   area=0.01       → -0.1        │  │
      │  │   Total: 1149.9 ← 最高分!       │  │
      │  │                                 │  │
      │  │ OverlayLayer:                   │  │
      │  │   visible=False   → +0          │  │
      │  │   zOrder=2        → +200        │  │
      │  │   touchable=False → +0          │  │
      │  │   area=0.8        → -8          │  │
      │  │   Total: 192                    │  │
      │  └─────────────────────────────────┘  │
      └─────────────────────────────────────┘
           |
           v
      ┌─────────────────────────────────────┐
      │  7. 返回最佳匹配                      │
      │  ┌─────────────────────────────────┐  │
      │  │ best_match = Button1            │  │
      │  │ return {                        │  │
      │  │   'resourceId': 'btn_login',    │  │
      │  │   'name': 'login_button',       │  │
      │  │   'type': 'Button',             │  │
      │  │   'text': 'Login',              │  │
      │  │   'pos': [0.5, 0.4],           │  │
      │  │   'size': [0.1, 0.05],         │  │
      │  │   'visible': True,              │  │
      │  │   'touchable': True,            │  │
      │  │   ...                           │  │
      │  │ }                               │  │
      │  └─────────────────────────────────┘  │
      └─────────────────────────────────────┘


  边界检测详细示例

  UI元素边界检测
  ==============

  假设有一个按钮:
    pos = [0.5, 0.3]    # 中心点
    size = [0.2, 0.1]   # 宽度=0.2, 高度=0.1

  计算边界:
    left = 0.5 - 0.2/2 = 0.4
    top = 0.3 - 0.1/2 = 0.25
    right = 0.5 + 0.2/2 = 0.6
    bottom = 0.3 + 0.1/2 = 0.35

  视觉表示:
       0.4      0.5      0.6
        |        |        |
  0.25 ─┼────────┼────────┼─
        │        │        │
        │    ┌───┼───┐    │
        │    │   │   │    │
  0.3  ─┼────┼───●───┼────┼─  ← 中心点
        │    │   │   │    │
        │    └───┼───┘    │
        │        │        │
  0.35 ─┼────────┼────────┼─

  点击测试:
    coord = [0.45, 0.32]

    检查: 0.4 ≤ 0.45 ≤ 0.6  ✓
          0.25 ≤ 0.32 ≤ 0.35  ✓

    结果: 匹配! ✓

  为什么需要 best_match

  实际场景问题:
  重叠元素示例
  ============

       Container (大容器)
     ┌─────────────────────────┐
     │  ┌─────────────────────┐ │
     │  │    SubContainer     │ │
     │  │  ┌─────────────────┐│ │
     │  │  │     Button      ││ │
     │  │  │   [点击这里]     ││ │ ← 用户想点击这个
     │  │  └─────────────────┘│ │
     │  └─────────────────────┘ │
     │                         │
     │  ┌─────────────────────┐ │
     │  │   Invisible Mask    │ │ ← 不可见遮罩
     │  └─────────────────────┘ │
     └─────────────────────────┘

  点击坐标 [0.5, 0.4] 时，会匹配到:
  1. Container (visible=True, zOrder=0, area=大)
  2. SubContainer (visible=True, zOrder=1, area=中)
  3. Button (visible=True, zOrder=2, area=小, touchable=True)
  4. Invisible Mask (visible=False, zOrder=3, area=大)

  best_match 选择 Button，因为:
  - 可见 ✓
  - 层级最高 ✓
  - 可交互 ✓
  - 面积最小（最精确）✓

  评分优先级的合理性:
  1. visible > zOrder: 不可见元素不应该被选中
  2. zOrder > touchable: 前台元素比后台元素重要
  3. touchable > area: 可交互元素比纯显示元素重要
  4. area 越小越好: 避免选择大容器，选择最精确的目标

  这样设计确保了在复杂UI中能准确选择用户真正想要操作的元素。