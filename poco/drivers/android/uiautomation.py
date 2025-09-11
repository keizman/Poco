# coding=utf-8
"""
Android UIAutomation driver for Poco - Now using UIAutomator2 by default

This module provides the default Android automation driver for Poco.
Starting from this version, it uses the modern UIAutomator2 backend for better performance,
stability, and compatibility with video playback scenarios.

For the legacy UIAutomator implementation, use:
    from poco.drivers.android.uiautomation1 import AndroidUiautomationPoco

For the new UIAutomator2 implementation (default):
    from poco.drivers.android.uiautomation import AndroidUiautomationPoco

Note: The class is still named AndroidUiautomationPoco for backward compatibility,
but the underlying implementation now uses UIAutomator2.
"""

import warnings
from .uiautomation2 import AndroidUiautomator2Poco, AndroidUiautomator2Helper

__author__ = 'claude'
__all__ = ['AndroidUiautomationPoco', 'AndroidUiautomationHelper']

# Main class - now using UIAutomator2 implementation
class AndroidUiautomationPoco(AndroidUiautomator2Poco):
    """
    Poco Android implementation for testing **Android native apps**.
    
    This class now uses the modern UIAutomator2 backend by default, providing:
    - Better performance and stability
    - Full package information preservation  
    - Improved video playback compatibility
    - Enhanced coordinate system handling
    - Modern selector functionality
    
    Args:
        device: Airtest device object (legacy compatibility, deprecated)
        device_id: Device serial number or IP address (None for default device)
        using_proxy: Whether to use proxy connection (compatibility parameter)
        force_restart: Whether to restart UIAutomator2 daemon on initialization
        use_airtest_input: Whether to use Airtest input system (requires airtest package)
        screenshot_each_action: Whether to take screenshot before each action (requires airtest)
        **options: see :py:class:`poco.pocofw.Poco`

    Examples:
        Initialize AndroidUiautomationPoco instance (now using UIAutomator2)::

            from poco.drivers.android.uiautomation import AndroidUiautomationPoco

            poco = AndroidUiautomationPoco()
            poco('android:id/title').click()
            ...
            
        Connect to specific device::
        
            poco = AndroidUiautomationPoco(device_id='192.168.1.100:5555')
            
        Use with Airtest input system::
        
            poco = AndroidUiautomationPoco(use_airtest_input=True)

    Migration Notes:
        - This class maintains the same API as the original AndroidUiautomationPoco
        - No code changes needed for existing applications
        - Improved reliability for video playback scenarios  
        - Better package information handling
        - For legacy behavior, use uiautomation1 module instead
        
    Performance Improvements:
        - Faster hierarchy traversal
        - Reduced memory usage
        - Better element selection reliability
        - Enhanced coordinate precision
    """
    
    def __init__(self, device=None, device_id=None, using_proxy=True, force_restart=False, use_airtest_input=False, screenshot_each_action=False, **options):
        # Issue deprecation warning to inform users about the change
        if not hasattr(self.__class__, '_deprecation_warned'):
            warnings.warn(
                "AndroidUiautomationPoco now uses UIAutomator2 backend by default for improved "
                "performance and stability. For the legacy implementation, use: "
                "from poco.drivers.android.uiautomation1 import AndroidUiautomationPoco",
                DeprecationWarning,
                stacklevel=2
            )
            self.__class__._deprecation_warned = True
        
        # Initialize with UIAutomator2 implementation
        super(AndroidUiautomationPoco, self).__init__(
            device=device,
            device_id=device_id,
            using_proxy=using_proxy,
            force_restart=force_restart,
            use_airtest_input=use_airtest_input,
            screenshot_each_action=screenshot_each_action,
            **options
        )
        
        # Add compatibility properties for legacy code
        self._legacy_compatibility_mode = True
        
    def get_implementation_info(self):
        """Get information about the current implementation"""
        return {
            'backend': 'UIAutomator2',
            'version': '2.0',
            'legacy_compatible': True,
            'improvements': [
                'Full package information preservation',
                'Enhanced video playback support', 
                'Improved selector reliability',
                'Better coordinate handling',
                'Modern UIAutomator2 backend'
            ]
        }


# Helper class - also using UIAutomator2
class AndroidUiautomationHelper(AndroidUiautomator2Helper):
    """
    Helper class for managing AndroidUiautomationPoco instances (UIAutomator2 backend).
    
    This helper now uses the UIAutomator2 backend by default for better performance
    and reliability.
    """
    
    _instances = {}
    
    @classmethod
    def get_instance(cls, device=None):
        """
        Get or create AndroidUiautomationPoco instance for specified device.
        
        Args:
            device: Device instance or device_id string
            
        Returns:
            AndroidUiautomationPoco instance (using UIAutomator2 backend)
        """
        # Handle both device objects and device_id strings
        if hasattr(device, 'serialno'):
            # Airtest device object
            device_key = device.serialno
        elif isinstance(device, str):
            # Device ID string
            device_key = device
        else:
            device_key = 'default'
            
        if device_key not in cls._instances:
            if isinstance(device, str):
                cls._instances[device_key] = AndroidUiautomationPoco(device_id=device)
            else:
                cls._instances[device_key] = AndroidUiautomationPoco()
                
        return cls._instances[device_key]
        
    @classmethod
    def clear_instances(cls):
        """Clear all cached instances"""
        cls._instances.clear()


# Backward compatibility aliases
AndroidUiAutomationPoco = AndroidUiautomationPoco  # Alternative spelling
AndroidUIAutomationPoco = AndroidUiautomationPoco  # Another alternative