# coding=utf-8
"""
Poco Android drivers with improved UIAutomator2 backend

Import structure:
- Default (UIAutomator2): from poco.drivers.android import AndroidUiautomationPoco
- Legacy (UIAutomator1): from poco.drivers.android.uiautomation1 import AndroidUiautomationPoco  
- Explicit UIAutomator2: from poco.drivers.android.uiautomator2 import AndroidUiautomator2Poco
"""

# Import default implementation (now UIAutomator2)
from .uiautomation import AndroidUiautomationPoco, AndroidUiautomationHelper

# Import explicit UIAutomator2 implementation
try:
    from .uiautomator2 import AndroidUiautomator2Poco, AndroidUiautomator2Helper
    uiautomator2_available = True
except ImportError:
    uiautomator2_available = False

# Import legacy UIAutomator1 implementation
try:
    from .uiautomation1 import AndroidUiautomationPoco as AndroidUiautomation1Poco
    from .uiautomation1 import AndroidUiautomationHelper as AndroidUiautomation1Helper
    uiautomation1_available = True
except ImportError:
    uiautomation1_available = False

# Define exports based on availability
__all__ = ['AndroidUiautomationPoco', 'AndroidUiautomationHelper']

if uiautomator2_available:
    __all__.extend(['AndroidUiautomator2Poco', 'AndroidUiautomator2Helper'])

if uiautomation1_available:
    __all__.extend(['AndroidUiautomation1Poco', 'AndroidUiautomation1Helper'])

# Compatibility aliases
AndroidUIAutomationPoco = AndroidUiautomationPoco  # Alternative spelling
AndroidUiAutomationPoco = AndroidUiautomationPoco  # Alternative spelling