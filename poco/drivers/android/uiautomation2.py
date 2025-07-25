# coding=utf-8
__author__ = 'claude'

import os
import time
import threading
import warnings
import xml.etree.ElementTree as ET

try:
    import uiautomator2 as u2
except ImportError:
    raise ImportError("uiautomator2 is required. Install with: pip install uiautomator2")

from poco.pocofw import Poco
from poco.agent import PocoAgent
from poco.sdk.interfaces.hierarchy import HierarchyInterface
from poco.sdk.interfaces.input import InputInterface
from poco.sdk.interfaces.screen import ScreenInterface
from poco.sdk.AbstractNode import AbstractNode
from poco.sdk.AbstractDumper import AbstractDumper
from poco.sdk.Attributor import Attributor
from poco.utils.device import default_device
from poco.utils import six

__all__ = ['AndroidUiautomator2Poco', 'AndroidUiautomator2Helper']


class UIAutomator2Node(AbstractNode):
    """Node implementation for UIAutomator2 that mimics original structure"""
    
    def __init__(self, xml_element, screen_size=(1280, 720)):
        super(UIAutomator2Node, self).__init__()
        self.xml_element = xml_element
        self.screen_width, self.screen_height = screen_size
        self._parent = None
        self._children = None
        
    def getParent(self):
        return self._parent
        
    def setParent(self, parent):
        self._parent = parent
        
    def getChildren(self):
        if self._children is None:
            self._children = []
            for child_elem in self.xml_element:
                child_node = UIAutomator2Node(child_elem, (self.screen_width, self.screen_height))
                child_node.setParent(self)
                self._children.append(child_node)
        return self._children
        
    def getAttr(self, attrName):
        """Get attribute value, compatible with original format"""
        
        # Get XML attributes
        attrib = self.xml_element.attrib
        
        # Handle hierarchy root element case
        if self.xml_element.tag == 'hierarchy':
            if attrName == 'name':
                return '<Unknown>'
            elif attrName == 'type':
                return 'Unknown'
            elif attrName == 'visible':
                return True
            elif attrName == 'enabled':
                return False
            elif attrName == 'pos':
                return [0.0, 0.0]
            elif attrName == 'size':
                return [0.0, 0.0]
            elif attrName == 'bounds':
                return []
            elif attrName in ['text', 'resourceId', 'package']:
                return ''
            elif attrName in ['clickable', 'touchable', 'focusable', 'focused', 'scrollable', 
                             'selected', 'checkable', 'checked', 'longClickable', 'editable', 'dismissable']:
                return False
            elif attrName == 'scale':
                return [1.0, 1.0]
            elif attrName == 'anchorPoint':
                return [0.5, 0.5]
            elif attrName == 'zOrders':
                return {'local': 0, 'global': 0}
            elif attrName == 'boundsInParent':
                return []
        
        if attrName == 'name':
            # Use text content or class name as name
            text = attrib.get('text', '').strip()
            if text:
                return text
            return attrib.get('class', '<Unknown>')
            
        elif attrName == 'type':
            return attrib.get('class', 'Unknown')
            
        elif attrName == 'visible':
            visible_to_user = attrib.get('visible-to-user', 'true')
            return visible_to_user.lower() == 'true'
            
        elif attrName == 'enabled':
            enabled = attrib.get('enabled', 'true')
            return enabled.lower() == 'true'
            
        elif attrName == 'pos':
            return self._get_normalized_pos()
            
        elif attrName == 'size':
            return self._get_normalized_size()
            
        elif attrName == 'bounds':
            return self._get_bounds_array()
            
        elif attrName == 'text':
            return attrib.get('text', '')
            
        elif attrName == 'resourceId':
            return attrib.get('resource-id', '')
            
        elif attrName == 'package':
            return attrib.get('package', '')
            
        elif attrName == 'clickable':
            clickable = attrib.get('clickable', 'false')
            return clickable.lower() == 'true'
            
        elif attrName == 'touchable':
            # UIAutomator2 doesn't have touchable, use clickable as fallback
            clickable = attrib.get('clickable', 'false')
            return clickable.lower() == 'true'
            
        elif attrName == 'focusable':
            focusable = attrib.get('focusable', 'false')
            return focusable.lower() == 'true'
            
        elif attrName == 'focused':
            focused = attrib.get('focused', 'false')
            return focused.lower() == 'true'
            
        elif attrName == 'scrollable':
            scrollable = attrib.get('scrollable', 'false')
            return scrollable.lower() == 'true'
            
        elif attrName == 'selected':
            selected = attrib.get('selected', 'false')
            return selected.lower() == 'true'
            
        elif attrName == 'checkable':
            checkable = attrib.get('checkable', 'false')
            return checkable.lower() == 'true'
            
        elif attrName == 'checked':
            checked = attrib.get('checked', 'false')
            return checked.lower() == 'true'
            
        elif attrName == 'longClickable':
            long_clickable = attrib.get('long-clickable', 'false')
            return long_clickable.lower() == 'true'
            
        elif attrName == 'editable':
            # UIAutomator doesn't have editable directly, infer from class
            class_name = attrib.get('class', '')
            return 'EditText' in class_name
            
        elif attrName == 'dismissable':
            # Not available in UIAutomator, return False
            return False
            
        elif attrName == 'scale':
            # Default scale
            return [1.0, 1.0]
            
        elif attrName == 'anchorPoint':
            # Default anchor point
            return [0.5, 0.5]
            
        elif attrName == 'zOrders':
            # Default z-orders
            drawing_order = attrib.get('drawing-order', '0')
            try:
                order = int(drawing_order)
            except (ValueError, TypeError):
                order = 0
            return {'local': order, 'global': order}
            
        elif attrName == 'boundsInParent':
            # Get normalized size as bounds in parent
            return self._get_normalized_size()
            
        else:
            # Fallback to parent implementation
            return super(UIAutomator2Node, self).getAttr(attrName)
    
    def _parse_bounds(self):
        """Parse bounds string like '[54,34][592,75]' into coordinates"""
        # Handle hierarchy root element case
        if self.xml_element.tag == 'hierarchy':
            return 0, 0, 0, 0
            
        bounds_str = self.xml_element.attrib.get('bounds', '[0,0][0,0]')
        try:
            # Remove brackets and split
            bounds_str = bounds_str.replace('[', '').replace(']', ',')
            coords = [int(x) for x in bounds_str.split(',') if x]
            if len(coords) >= 4:
                return coords[0], coords[1], coords[2], coords[3]  # x1, y1, x2, y2
        except (ValueError, IndexError):
            pass
        return 0, 0, 0, 0
    
    def _get_normalized_pos(self):
        """Get normalized position [x, y]"""
        # Handle hierarchy root element case
        if self.xml_element.tag == 'hierarchy':
            return [0.0, 0.0]
            
        x1, y1, x2, y2 = self._parse_bounds()
        center_x = (x1 + x2) / 2.0
        center_y = (y1 + y2) / 2.0
        return [center_x / self.screen_width, center_y / self.screen_height]
    
    def _get_normalized_size(self):
        """Get normalized size [width, height]"""
        # Handle hierarchy root element case
        if self.xml_element.tag == 'hierarchy':
            return [0.0, 0.0]
            
        x1, y1, x2, y2 = self._parse_bounds()
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        return [width / self.screen_width, height / self.screen_height]
    
    def _get_bounds_array(self):
        """Get bounds as array [x1, y1, x2, y2] normalized"""
        # Handle hierarchy root element case
        if self.xml_element.tag == 'hierarchy':
            return []
            
        x1, y1, x2, y2 = self._parse_bounds()
        return [
            x1 / self.screen_width,
            y1 / self.screen_height,
            x2 / self.screen_width,
            y2 / self.screen_height
        ]


class UIAutomator2Dumper(AbstractDumper):
    """Dumper implementation for UIAutomator2"""
    
    def __init__(self, device):
        super(UIAutomator2Dumper, self).__init__()
        self.device = device
        self._root_node = None
        
    def getRoot(self):
        """Get root node from UI hierarchy"""
        if self._root_node is None:
            self._update_hierarchy()
        return self._root_node
    
    def _update_hierarchy(self):
        """Update the UI hierarchy from device"""
        try:
            # Get device info for screen size
            info = self.device.info
            screen_size = (info.get('displayWidth', 1280), info.get('displayHeight', 720))
            
            # Get XML hierarchy
            xml_content = self.device.dump_hierarchy()
            
            # Parse XML
            root_element = ET.fromstring(xml_content)
            
            # The hierarchy element contains multiple node elements as direct children
            # We need to create a synthetic root that properly contains all nodes
            # but we also need to preserve the original hierarchy structure
            
            # Create root node - the hierarchy element itself becomes our root
            self._root_node = UIAutomator2Node(root_element, screen_size)
            
        except Exception as e:
            warnings.warn("Failed to update hierarchy: {}".format(str(e)))
            # Create a dummy root node
            dummy_xml = ET.Element('hierarchy')
            self._root_node = UIAutomator2Node(dummy_xml, (1280, 720))
    
    def dumpHierarchy(self, onlyVisibleNode=True):
        """Override to ensure we get fresh data each time"""
        self._root_node = None  # Force refresh
        return super(UIAutomator2Dumper, self).dumpHierarchy(onlyVisibleNode)


class UIAutomator2Attributor(Attributor):
    """Attributor implementation for UIAutomator2"""
    
    def __init__(self, device):
        super(UIAutomator2Attributor, self).__init__()
        self.device = device
        
    def getAttr(self, node, attrName):
        if isinstance(node, UIAutomator2Node):
            return node.getAttr(attrName)
        return None
        
    def setAttr(self, node, attrName, attrVal):
        """Set attribute on UI element"""
        if not isinstance(node, UIAutomator2Node):
            return False
            
        if attrName == 'text':
            # Try to find element and set text
            try:
                # Get element attributes
                resource_id = node.getAttr('resourceId')
                text = node.getAttr('text')
                class_name = node.getAttr('type')
                
                # Try different selectors
                element = None
                
                if resource_id:
                    element = self.device(resourceId=resource_id)
                elif text:
                    element = self.device(text=text)
                elif class_name:
                    element = self.device(className=class_name)
                
                if element and element.exists:
                    element.set_text(attrVal)
                    return True
                    
            except Exception as e:
                warnings.warn("Failed to set text: {}".format(str(e)))
        
        return False


class UIAutomator2Input(InputInterface):
    """Input implementation for UIAutomator2"""
    
    def __init__(self, device):
        super(UIAutomator2Input, self).__init__()
        self.device = device
        self.default_touch_down_duration = 0.01
        
    def _get_actual_pos(self, x, y):
        """Convert normalized coordinates to actual screen coordinates"""
        info = self.device.info
        screen_width = info.get('displayWidth', 1280)
        screen_height = info.get('displayHeight', 720)
        
        actual_x = int(x * screen_width)
        actual_y = int(y * screen_height)
        return actual_x, actual_y
        
    def click(self, x, y):
        """Click at normalized coordinates"""
        actual_x, actual_y = self._get_actual_pos(x, y)
        self.device.click(actual_x, actual_y)
        
    def double_click(self, x, y):
        """Double click at normalized coordinates (for Airtest compatibility)"""
        actual_x, actual_y = self._get_actual_pos(x, y)
        self.device.double_click(actual_x, actual_y)
        
    def long_click(self, x, y, duration=2.0):
        """Long click at normalized coordinates (for Airtest compatibility)"""
        actual_x, actual_y = self._get_actual_pos(x, y)
        self.device.long_click(actual_x, actual_y, duration)
    
    # Alias for compatibility
    def longClick(self, x, y, duration=2.0):
        """Long click (Airtest style method name)"""
        return self.long_click(x, y, duration)
        
    def swipe(self, x1, y1, x2, y2, duration=0.5):
        """Swipe from (x1,y1) to (x2,y2) with duration"""
        actual_x1, actual_y1 = self._get_actual_pos(x1, y1)
        actual_x2, actual_y2 = self._get_actual_pos(x2, y2)
        
        self.device.swipe(actual_x1, actual_y1, actual_x2, actual_y2, duration)
        
    def drag(self, x1, y1, x2, y2, duration=2.0):
        """Drag from (x1,y1) to (x2,y2) with duration"""
        actual_x1, actual_y1 = self._get_actual_pos(x1, y1)
        actual_x2, actual_y2 = self._get_actual_pos(x2, y2)
        
        self.device.drag(actual_x1, actual_y1, actual_x2, actual_y2, duration)
        
    def keyevent(self, keyname):
        """Send key event"""
        # Map common key names to UIAutomator2 format
        key_mapping = {
            'HOME': 'home',
            'BACK': 'back', 
            'MENU': 'menu',
            'ENTER': 'enter',
            'DELETE': 'del',
            'VOLUME_UP': 'volume_up',
            'VOLUME_DOWN': 'volume_down',
        }
        
        key = key_mapping.get(keyname, keyname.lower())
        self.device.press(key)
    
    def setTouchDownDuration(self, duration):
        """Set touch down duration (for Airtest compatibility)"""
        self.default_touch_down_duration = duration
        
    def getTouchDownDuration(self):
        """Get touch down duration (for Airtest compatibility)"""
        return self.default_touch_down_duration
    
    def applyMotionEvents(self, events):
        """Apply motion events (limited UIAutomator2 support)"""
        warnings.warn("applyMotionEvents has limited support in UIAutomator2. "
                     "Consider using use_airtest_input=True for full motion event support.")
        
        # Basic implementation for simple events
        for event in events:
            event_type = event[0]
            if event_type == 'd':  # down
                pos = event[1]  # [x, y]
                # UIAutomator2 doesn't support separate down events, simulate with quick tap
                actual_x, actual_y = self._get_actual_pos(pos[0], pos[1])
                self.device.click(actual_x, actual_y)
            elif event_type == 's':  # sleep
                duration = event[1]
                time.sleep(duration)
            # Note: UIAutomator2 doesn't support separate move/up events like Airtest


class UIAutomator2Screen(ScreenInterface):
    """Screen interface implementation for UIAutomator2"""
    
    def __init__(self, device):
        super(UIAutomator2Screen, self).__init__()
        self.device = device
        
    def getScreen(self, width):
        """Get screenshot as base64 encoded image"""
        try:
            import base64
            import io
            
            # Take screenshot
            screenshot = self.device.screenshot(format='pillow')
            
            # Resize if width specified
            if width and width > 0:
                from PIL import Image
                ratio = width / float(screenshot.width)
                height = int(screenshot.height * ratio)
                screenshot = screenshot.resize((width, height), Image.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            screenshot.save(buffer, format='JPEG', quality=80)
            img_data = buffer.getvalue()
            
            return base64.b64encode(img_data).decode('utf-8'), 'jpg'
        except Exception as e:
            warnings.warn("Failed to capture screen: {}".format(str(e)))
            return None, None
            
    def getPortSize(self):
        """Get screen size"""
        info = self.device.info
        return [info.get('displayWidth', 1280), info.get('displayHeight', 720)]


class UIAutomator2Hierarchy(HierarchyInterface):
    """Hierarchy interface implementation for UIAutomator2"""
    
    def __init__(self, dumper, selector, attributor):
        super(UIAutomator2Hierarchy, self).__init__()
        self.dumper = dumper
        self.selector = selector  # Not used in UIAutomator2
        self.attributor = attributor
        
    def dump(self):
        """Dump current UI hierarchy"""
        return self.dumper.dumpHierarchy()
        
    def getAttr(self, node, attrName):
        """Get attribute from node"""
        return self.attributor.getAttr(node, attrName)
        
    def setAttr(self, node, attrName, attrVal):
        """Set attribute on node"""
        return self.attributor.setAttr(node, attrName, attrVal)


class AndroidUiautomator2Agent(PocoAgent):
    """Poco agent implementation using UIAutomator2"""
    
    def __init__(self, device=None, use_airtest_input=False):
        # Connect to device
        if device is None:
            device = u2.connect()
        self.device = device
        
        # Initialize components
        dumper = UIAutomator2Dumper(device)
        attributor = UIAutomator2Attributor(device)
        
        # For compatibility, we need a selector, but UIAutomator2 doesn't need it
        # We'll create a dummy selector
        selector = None
        
        hierarchy = UIAutomator2Hierarchy(dumper, selector, attributor)
        
        # 选择输入系统
        if use_airtest_input:
            try:
                from poco.utils.airtest.input import AirtestInput
                input_interface = AirtestInput()
                print("使用 Airtest 输入系统")
            except ImportError as e:
                warnings.warn("AirtestInput 不可用 ({}), 使用 UIAutomator2 输入".format(str(e)))
                input_interface = UIAutomator2Input(device)
        else:
            input_interface = UIAutomator2Input(device)
            print("使用 UIAutomator2 原生输入系统")
            
        screen_interface = UIAutomator2Screen(device)
        
        super(AndroidUiautomator2Agent, self).__init__(hierarchy, input_interface, screen_interface)


class AndroidUiautomator2Poco(Poco):
    """
    Poco Android implementation using UIAutomator2 for testing **Android native apps**.
    
    This is a modern alternative to the original UIAutomator-based implementation,
    offering better performance, stability, and compatibility with newer Android versions.
    
    Args:
        device_id: Device serial number or IP address (None for default device)
        use_airtest_input: Whether to use Airtest input system (requires airtest package)
        **options: see :py:class:`poco.pocofw.Poco`
    
    Examples:
        Initialize AndroidUiautomator2Poco instance::
        
            from poco.drivers.android.uiautomator2 import AndroidUiautomator2Poco
            
            poco = AndroidUiautomator2Poco()
            poco('android:id/title').click()
            ...
            
        Connect to specific device::
        
            poco = AndroidUiautomator2Poco(device_id='192.168.1.100:5555')
            
        Use with Airtest input system::
        
            poco = AndroidUiautomator2Poco(use_airtest_input=True)
            
    """
    
    def __init__(self, device_id=None, use_airtest_input=False, **options):
        # Connect to device
        try:
            if device_id:
                device = u2.connect(device_id)
            else:
                device = u2.connect()
        except Exception as e:
            raise RuntimeError("Failed to connect to Android device: {}".format(str(e)))
        
        self.device = device
        
        # Initialize agent
        agent = AndroidUiautomator2Agent(device, use_airtest_input)
        
        # Initialize Poco
        super(AndroidUiautomator2Poco, self).__init__(agent, **options)
        
    def get_device_info(self):
        """Get device information"""
        return self.device.info
        
    def install_app(self, apk_path):
        """Install APK file"""
        return self.device.app_install(apk_path)
        
    def uninstall_app(self, package_name):
        """Uninstall app by package name"""
        return self.device.app_uninstall(package_name)
        
    def start_app(self, package_name, activity=None):
        """Start app by package name"""
        if activity:
            return self.device.app_start(package_name, activity)
        else:
            return self.device.app_start(package_name)
            
    def stop_app(self, package_name):
        """Stop app by package name"""
        return self.device.app_stop(package_name)
        
    def get_current_app(self):
        """Get current running app info"""
        return self.device.app_current()


class AndroidUiautomator2Helper(object):
    """Helper class for managing AndroidUiautomator2Poco instances"""
    
    _instances = {}
    
    @classmethod
    def get_instance(cls, device_id=None):
        """
        Get or create AndroidUiautomator2Poco instance for specified device.
        
        Args:
            device_id: Device serial number or IP address (None for default device)
            
        Returns:
            AndroidUiautomator2Poco instance
        """
        key = device_id or 'default'
        if key not in cls._instances:
            cls._instances[key] = AndroidUiautomator2Poco(device_id)
        return cls._instances[key]
        
    @classmethod
    def clear_instances(cls):
        """Clear all cached instances"""
        cls._instances.clear()