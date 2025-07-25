# coding=utf-8
"""
Android UIAutomator2 Poco Driver Example

This example demonstrates how to use the new UIAutomator2-based Poco driver
for Android automation. This driver offers better performance and stability
compared to the original UIAutomator implementation.

Requirements:
- pip install uiautomator2
- Android device connected via USB or network (ADB enabled)
"""

from poco.drivers.android.uiautomator2 import AndroidUiautomator2Poco


def main():
    """Main example function"""
    print("Initializing AndroidUiautomator2Poco...")
    
    # Initialize Poco with UIAutomator2 backend
    poco = AndroidUiautomator2Poco()
    
    # Get device information
    device_info = poco.get_device_info()
    print("Device Info:")
    print("  Display: {}x{}".format(device_info.get('displayWidth'), device_info.get('displayHeight')))
    print("  Brand: {}".format(device_info.get('brand', 'Unknown')))
    print("  Model: {}".format(device_info.get('model', 'Unknown')))
    print("  Android Version: {}".format(device_info.get('version', 'Unknown')))
    
    # Example UI interactions
    print("\nPerforming UI interactions...")
    
    # Wait for and click on a button with text "Settings"
    try:
        settings_btn = poco('Settings')
        if settings_btn.exists():
            print("Found Settings button, clicking...")
            settings_btn.click()
        else:
            print("Settings button not found")
    except Exception as e:
        print("Error clicking Settings: {}".format(e))
    
    # Alternative: Find element by resource ID
    try:
        element = poco('android:id/title')
        if element.exists():
            print("Found element with android:id/title")
            print("Text: {}".format(element.get_text()))
        else:
            print("Element with android:id/title not found")
    except Exception as e:
        print("Error finding element: {}".format(e))
    
    # Example: Swipe gesture
    try:
        print("Performing swipe gesture...")
        poco.swipe([0.5, 0.8], [0.5, 0.2])  # Swipe up from bottom to top
    except Exception as e:
        print("Error performing swipe: {}".format(e))
    
    # Example: Take screenshot
    try:
        print("Taking screenshot...")
        screenshot_data, format_type = poco.agent.screen.getScreen(720)  # 720px width
        if screenshot_data:
            print("Screenshot captured successfully (format: {})".format(format_type))
            # You can save the base64 data to file if needed
        else:
            print("Failed to capture screenshot")
    except Exception as e:
        print("Error taking screenshot: {}".format(e))
    
    print("\nExample completed!")


def app_management_example():
    """Example of app management features"""
    print("\n=== App Management Example ===")
    
    poco = AndroidUiautomator2Poco()
    
    # Get current app info
    try:
        current_app = poco.get_current_app()
        print("Current app: {}".format(current_app))
    except Exception as e:
        print("Error getting current app: {}".format(e))
    
    # Example: Start an app (replace with actual package name)
    # poco.start_app("com.android.settings")
    
    # Example: Stop an app (replace with actual package name)  
    # poco.stop_app("com.example.app")


def connection_example():
    """Example of connecting to specific device"""
    print("\n=== Connection Example ===")
    
    # Connect to default device
    poco_default = AndroidUiautomator2Poco()
    print("Connected to default device")
    
    # Connect to specific device by serial number
    # poco_specific = AndroidUiautomator2Poco(device_id="your_device_serial")
    
    # Connect to device over network (WiFi ADB)
    # poco_wifi = AndroidUiautomator2Poco(device_id="192.168.1.100:5555")


if __name__ == '__main__':
    try:
        main()
        app_management_example()
        connection_example()
    except Exception as e:
        print("Error running example: {}".format(e))
        print("Make sure:")
        print("1. Android device is connected and ADB is enabled")
        print("2. uiautomator2 package is installed: pip install uiautomator2")
        print("3. UIAutomator2 server is properly installed on device")