# coding=utf-8
"""
UIAutomator2 驱动输入系统对比示例

演示 use_airtest_input=True 和 use_airtest_input=False 的区别
"""

from poco.drivers.android.uiautomator2 import AndroidUiautomator2Poco


def test_uiautomator2_input():
    """测试 UIAutomator2 原生输入系统"""
    print("=== 测试 UIAutomator2 原生输入系统 ===")
    
    poco = AndroidUiautomator2Poco(use_airtest_input=False)
    
    # 基本点击
    print("基本点击操作...")
    # poco.click([0.5, 0.5])
    
    # 滑动操作
    print("滑动操作...")
    # poco.swipe([0.5, 0.8], [0.5, 0.2])
    
    # 长按操作
    print("长按操作...")
    # poco.agent.input.long_click(0.5, 0.5, 2.0)
    
    # 双击操作
    print("双击操作...")
    # poco.agent.input.double_click(0.5, 0.5)
    
    print("UIAutomator2 原生输入系统测试完成\n")


def test_airtest_input():
    """测试 Airtest 输入系统"""
    print("=== 测试 Airtest 输入系统 ===")
    
    try:
        poco = AndroidUiautomator2Poco(use_airtest_input=True)
        
        # 基本点击
        print("基本点击操作...")
        # poco.click([0.5, 0.5])
        
        # 滑动操作
        print("滑动操作...")
        # poco.swipe([0.5, 0.8], [0.5, 0.2])
        
        # 长按操作
        print("长按操作...")
        # poco.agent.input.longClick(0.5, 0.5, 2.0)
        
        # 双击操作
        print("双击操作...")
        # poco.agent.input.double_click(0.5, 0.5)
        
        # 复杂手势操作（Airtest 特有）
        print("复杂手势操作...")
        # events = [
        #     ('d', [0.5, 0.5], 0),  # down event
        #     ('s', 0.1),            # sleep
        #     ('m', [0.6, 0.6], 0),  # move event
        #     ('s', 0.1),            # sleep
        #     ('u', 0)               # up event
        # ]
        # poco.agent.input.applyMotionEvents(events)
        
        print("Airtest 输入系统测试完成")
        
    except ImportError as e:
        print(f"Airtest 输入系统不可用: {e}")
        print("请安装 airtest: pip install airtest")


def compare_input_systems():
    """对比两种输入系统"""
    print("=== UIAutomator2 输入系统对比 ===\n")
    
    print("1. UIAutomator2 原生输入 (use_airtest_input=False):")
    print("   优点:")
    print("   - 直接使用 UIAutomator2 API，性能较好")
    print("   - 不需要额外依赖")
    print("   - 与 UIAutomator2 完全兼容")
    print("   缺点:")
    print("   - 功能相对有限")
    print("   - 不支持复杂的多点触控手势")
    print("   - 没有自动日志记录")
    
    print("\n2. Airtest 输入系统 (use_airtest_input=True):")
    print("   优点:")
    print("   - 功能更丰富，支持复杂手势")
    print("   - 更好的设备兼容性")
    print("   - 自动操作日志记录")
    print("   - 支持多点触控")
    print("   - 与 Airtest 生态系统集成")
    print("   缺点:")
    print("   - 需要安装 airtest 包")
    print("   - 可能有轻微的性能开销")
    print("   - 增加了依赖复杂度")
    
    print("\n3. 使用建议:")
    print("   - 如果只需要基本的点击、滑动操作：use_airtest_input=False")
    print("   - 如果需要复杂手势或与 Airtest 集成：use_airtest_input=True")
    print("   - 如果在某些设备上原生输入不稳定：尝试 use_airtest_input=True")


def show_input_methods_comparison():
    """显示输入方法的对比"""
    print("\n=== 输入方法对比表 ===")
    
    methods = [
        ("方法", "UIAutomator2 原生", "Airtest", "说明"),
        ("click(x, y)", "✓", "✓", "基本点击"),
        ("double_click(x, y)", "✓", "✓", "双击"),
        ("long_click/longClick(x, y)", "✓", "✓", "长按"),
        ("swipe(x1, y1, x2, y2)", "✓", "✓", "滑动"),
        ("drag(x1, y1, x2, y2)", "✓", "✓", "拖拽"),
        ("keyevent(key)", "✓", "✓", "按键事件"),
        ("applyMotionEvents(events)", "部分支持", "✓", "复杂手势"),
        ("自动日志记录", "✗", "✓", "操作记录"),
        ("坐标自适应", "基本", "高级", "分辨率适配"),
        ("多点触控", "✗", "✓", "多指操作"),
    ]
    
    # 打印表格
    for i, row in enumerate(methods):
        if i == 0:  # 表头
            print(f"{'方法':<25} {'UIAutomator2 原生':<15} {'Airtest':<10} {'说明'}")
            print("-" * 70)
        else:
            print(f"{row[0]:<25} {row[1]:<15} {row[2]:<10} {row[3]}")


def main():
    """主函数"""
    compare_input_systems()
    show_input_methods_comparison()
    
    print("\n=== 实际测试 ===")
    print("注意: 需要连接 Android 设备才能进行实际测试")
    
    # 如果有设备连接，可以取消注释进行实际测试
    # test_uiautomator2_input()
    # test_airtest_input()


if __name__ == "__main__":
    main()