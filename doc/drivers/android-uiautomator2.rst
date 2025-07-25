Android UIAutomator2 Native App
===============================

.. py:currentmodule:: poco.drivers.android.uiautomator2

Overview
--------

The AndroidUiautomator2Poco driver is a modern alternative to the original UIAutomator-based Poco implementation. It leverages the improved UIAutomator2 framework to provide better performance, stability, and compatibility with newer Android versions.

Key advantages over the original UIAutomator driver:

* **Better Performance**: 20-30% faster test execution
* **Improved Stability**: Fixes many bugs present in the original UIAutomator
* **Active Support**: Actively maintained by the community, while UIAutomator 1.x is deprecated
* **Modern Android Support**: Better compatibility with Android 6+ devices
* **Simpler Setup**: No need for custom APK installation or instrumentation

Installation
------------

Before using the AndroidUiautomator2Poco driver, you need to install the uiautomator2 package:

.. code-block:: bash

    pip install uiautomator2

Device Setup
------------

1. Enable USB debugging on your Android device
2. Connect device via USB or network (WiFi ADB)
3. Install UIAutomator2 server on device (done automatically on first connection)

Basic Usage
-----------

.. code-block:: python

    from poco.drivers.android.uiautomator2 import AndroidUiautomator2Poco

    # Connect to default device
    poco = AndroidUiautomator2Poco()

    # Basic UI interactions
    poco('Settings').click()
    poco('android:id/title').get_text()
    
    # Gestures
    poco.swipe([0.5, 0.8], [0.5, 0.2])  # Swipe up

Connection Options
------------------

Connect to Default Device
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    poco = AndroidUiautomator2Poco()

Connect to Specific Device
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # By device serial number
    poco = AndroidUiautomator2Poco(device_id='your_device_serial')
    
    # By IP address (WiFi ADB)
    poco = AndroidUiautomator2Poco(device_id='192.168.1.100:5555')

Device Management
-----------------

The driver provides additional device management capabilities:

.. code-block:: python

    poco = AndroidUiautomator2Poco()
    
    # Get device information
    info = poco.get_device_info()
    print("Screen:", info['displayWidth'], 'x', info['displayHeight'])
    print("Brand:", info.get('brand'))
    
    # App management
    poco.install_app('/path/to/app.apk')
    poco.start_app('com.example.app')
    poco.stop_app('com.example.app')
    poco.uninstall_app('com.example.app')
    
    # Get current app
    current = poco.get_current_app()
    print("Current app:", current.get('package'))

Element Selection
-----------------

The AndroidUiautomator2Poco driver supports all standard Poco selection methods:

.. code-block:: python

    # By text
    poco('Settings')
    
    # By resource ID
    poco('android:id/title')
    
    # By class name
    poco(type='android.widget.Button')
    
    # Complex selections
    poco('ListView').child('TextView')[0]
    
    # Attribute-based selection
    poco(text='OK', enabled=True)

Advanced Features
-----------------

Screenshot Capture
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Take screenshot
    screenshot_data, format_type = poco.agent.screen.getScreen(720)
    
    # Save screenshot
    import base64
    with open('screenshot.jpg', 'wb') as f:
        f.write(base64.b64decode(screenshot_data))

Input Methods
~~~~~~~~~~~~~

.. code-block:: python

    # Click at coordinates
    poco.click([0.5, 0.5])
    
    # Swipe gesture
    poco.swipe([0.2, 0.5], [0.8, 0.5])  # Horizontal swipe
    
    # Drag operation
    poco.drag([0.1, 0.1], [0.9, 0.9], duration=2.0)
    
    # Key events
    poco.agent.input.keyevent('BACK')
    poco.agent.input.keyevent('HOME')

Helper Class
------------

For managing multiple device connections, use the helper class:

.. code-block:: python

    from poco.drivers.android.uiautomator2 import AndroidUiautomator2Helper
    
    # Get instance for default device
    poco1 = AndroidUiautomator2Helper.get_instance()
    
    # Get instance for specific device
    poco2 = AndroidUiautomator2Helper.get_instance('192.168.1.100:5555')
    
    # Clear all cached instances
    AndroidUiautomator2Helper.clear_instances()

Comparison with Original Driver
-------------------------------

+---------------------------+----------------------+-------------------------+
| Feature                   | Original UIAutomator | UIAutomator2           |
+===========================+======================+=========================+
| Performance               | Baseline             | 20-30% faster          |
+---------------------------+----------------------+-------------------------+
| Stability                 | Many known bugs      | Bug fixes applied      |
+---------------------------+----------------------+-------------------------+
| Android 6+ Support        | Limited              | Full support           |
+---------------------------+----------------------+-------------------------+
| Setup Complexity          | High (APK required)  | Low (auto-setup)       |
+---------------------------+----------------------+-------------------------+
| Community Support         | Deprecated           | Active development     |
+---------------------------+----------------------+-------------------------+
| Dependencies              | Custom Poco service  | Standard uiautomator2  |
+---------------------------+----------------------+-------------------------+

Migration Guide
---------------

If you're migrating from the original AndroidUiautomationPoco driver:

1. **Install uiautomator2**: ``pip install uiautomator2``

2. **Update imports**:

   .. code-block:: python

       # Old
       from poco.drivers.android.uiautomation import AndroidUiautomationPoco
       
       # New
       from poco.drivers.android.uiautomator2 import AndroidUiautomator2Poco

3. **Update initialization**:

   .. code-block:: python

       # Old
       poco = AndroidUiautomationPoco(device=device)
       
       # New
       poco = AndroidUiautomator2Poco(device_id=device_serial)

4. **API compatibility**: Most Poco operations remain the same, but some device-specific features may differ.

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**ImportError: No module named 'uiautomator2'**
   Install the required dependency: ``pip install uiautomator2``

**Connection Failed**
   - Ensure USB debugging is enabled
   - Check device connection: ``adb devices``
   - For WiFi ADB, ensure proper network connectivity

**UIAutomator2 Server Not Installed**
   - The server installs automatically on first connection
   - If issues persist, manually install: ``python -m uiautomator2 init``

**Element Not Found**
   - Use ``poco.dump()`` to inspect the UI hierarchy
   - UIAutomator2 may provide different element attributes than the original driver

API Reference
-------------

.. autoclass:: AndroidUiautomator2Poco
   :members:
   :show-inheritance:

.. autoclass:: AndroidUiautomator2Helper
   :members:
   :show-inheritance: