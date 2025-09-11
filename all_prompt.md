
 uiautomator 不支持在视频播放状态获取 xml(poco 底层使用它因此也无法工作). uiautomator2 能获取, 但是播放状态下获取不到控件和播放相关信息, 有作用的只有面板的数据, 但是项目本身希望能通过 ranger API 获取 debug
  等验证信息
  poco dump 元素在 mobile 似乎有些问题, 导致自动小屏, 获取不到播放页(暂停播放状态元素). 考虑到兼容问题, 完全使用 uiautomator2 获取元素, 并采用 poco 计算 pos 的方法用于传递参数

  问题核心：
  Poco的dump逻辑存在bug，原始XML包含完整package信息，但经过Poco处理后package统计为空{} UIAutomator2 可正确提取95个com.unitvnet.mobs节点，但Poco层丢失了所有package信息
  请你尝试修复 Poco的问题, 让 Poco 使用 UIAutomator2 新方式进行 元素处理, 比如当我 Click 时 使用新的方式以避免版本混用导致的冲突
 --------
 最终确实关闭了, 什么原因, 如何避免其它应用使用 poco click 无法点击问题, 确认其它方法是否还会有此类问题发生

---

很好,现在做一个修改, 默认使用  UIAutomator2 而不是 兼容原始引入方式, 比如 from poco.drivers.android.uiautomation import AndroidUiautomationPoco 这样引入的将时 UIAutomator2 from
  poco.drivers.android.uiautomation1 import AndroidUiautomationPoco 只有这样才引入旧版本

---



