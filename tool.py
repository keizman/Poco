# -*- coding: utf-8 -*-
"""
Poco UI automation testing toolkit
Provides coordinate positioning, element finding, region calculation and other useful functions
"""

import time
from poco.exceptions import PocoNoSuchNodeException


class CoordElementFinder:
    """Coordinate element finder"""
    
    def __init__(self, poco):
        self.poco = poco
    
    def get_element_by_coord(self, coord, coord_type='normalized'):
        """
        Get element information by coordinate
        
        Args:
            coord: coordinate [x, y]
            coord_type: 'normalized' or 'pixel'
        
        Returns:
            dict: element information including resourceId, name, type, text, etc.
        """
        # 1. Coordinate conversion if needed
        if coord_type == 'pixel':
            coord = self._pixel_to_normalized(coord)
        
        # 2. Get UI hierarchy
        try:
            hierarchy = self.poco.agent.hierarchy.dump()
        except Exception as e:
            print(f"Failed to get UI hierarchy: {e}")
            return None
        
        # 3. Find all matching elements
        matches = self._find_all_elements_at_coord(hierarchy, coord)
        
        # 4. Sort by priority (visibility, Z-order, size, etc.)
        best_match = self._select_best_match(matches)
        
        return best_match
    
    def get_element_region_by_coord(self, coord, coord_type='normalized', padding=0.01):
        """
        Get complete element region information by coordinate, suitable for image recognition
        
        Args:
            coord: coordinate [x, y]
            coord_type: 'normalized' or 'pixel'
            padding: region padding, default 0.01
        
        Returns:
            dict: dictionary containing region information
        """
        element_info = self.get_element_by_coord(coord, coord_type)
        
        if not element_info:
            return None
        
        # Calculate complete element region
        pos = element_info.get('pos', [0, 0])
        size = element_info.get('size', [0, 0])
        
        # Calculate boundary coordinates
        left = pos[0] - size[0] / 2
        top = pos[1] - size[1] / 2
        right = pos[0] + size[0] / 2
        bottom = pos[1] + size[1] / 2
        
        # Add padding
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(1, right + padding)
        bottom = min(1, bottom + padding)
        
        return {
            'element_info': element_info,
            'region': {
                'left': left,
                'top': top,
                'right': right,
                'bottom': bottom,
                'width': right - left,
                'height': bottom - top,
                'center': pos
            },
            'original_bounds': {
                'left': pos[0] - size[0] / 2,
                'top': pos[1] - size[1] / 2,
                'right': pos[0] + size[0] / 2,
                'bottom': pos[1] + size[1] / 2
            }
        }
    
    def _find_all_elements_at_coord(self, root, coord):
        """Find all elements at specified coordinate"""
        matches = []
        
        def traverse(node):
            if self._is_coord_in_element(coord, node):
                matches.append(node)
            
            for child in node.get('children', []):
                traverse(child)
        
        traverse(root)
        return matches
    
    def _is_coord_in_element(self, coord, element):
        """Check if coordinate is within element"""
        pos = element.get('pos', [0, 0])
        size = element.get('size', [0, 0])
        
        if not pos or not size:
            return False
        
        left = pos[0] - size[0] / 2
        top = pos[1] - size[1] / 2
        right = pos[0] + size[0] / 2
        bottom = pos[1] + size[1] / 2
        
        return (left <= coord[0] <= right and 
                top <= coord[1] <= bottom)
    
    def _select_best_match(self, matches):
        """Select the best matching element"""
        if not matches:
            return None
        
        # Priority: visible > Z-order > interactive > small area (more precise)
        def priority_score(element):
            '''
              在UI自动化中，一个坐标点可能同时位于多个重叠的UI元素内，比如：
            - 一个按钮在父容器内
            - 父容器在根布局内
            - 可能还有透明的遮罩层

            best_match 通过多维度评分来选择最合适的元素：
            '''
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
        
        best_match = max(matches, key=priority_score)
        
        # Extract required information
        return {
            'resourceId': best_match.get('resourceId'),
            'name': best_match.get('name'),
            'type': best_match.get('type'),
            'text': best_match.get('text'),
            'pos': best_match.get('pos'),
            'size': best_match.get('size'),
            'package': best_match.get('package'),
            'visible': best_match.get('visible'),
            'touchable': best_match.get('touchable'),
            'enabled': best_match.get('enabled'),
            'zOrders': best_match.get('zOrders'),
            'boundsInParent': best_match.get('boundsInParent'),
            'anchorPoint': best_match.get('anchorPoint'),
            'scale': best_match.get('scale'),
            'full_attributes': best_match  # Complete attribute information
        }
    
    def _pixel_to_normalized(self, pixel_coord):
        """Convert pixel coordinates to normalized coordinates"""
        try:
            screen_size = self.poco.get_screen_size()
            return [pixel_coord[0] / screen_size[0], pixel_coord[1] / screen_size[1]]
        except:
            # If unable to get screen size, return original coordinates
            return pixel_coord


class ElementTracker:
    """Element tracker - for recording and repeatedly locating UI elements"""
    
    def __init__(self, poco):
        self.poco = poco
        self.finder = CoordElementFinder(poco)
        self.tracked_elements = {}
    
    def track_element_by_coord(self, coord, element_name, coord_type='normalized'):
        """
        Track element by coordinate
        
        Args:
            coord: coordinate [x, y]
            element_name: element name (for later reference)
            coord_type: coordinate type
        
        Returns:
            bool: whether tracking was successful
        """
        element_info = self.finder.get_element_by_coord(coord, coord_type)
        
        if element_info:
            self.tracked_elements[element_name] = element_info
            print(f"Successfully tracked element '{element_name}': {element_info['resourceId'] or element_info['name']}")
            return True
        else:
            print(f"Unable to track element '{element_name}': no element found at coordinate {coord}")
            return False
    
    def click_tracked_element(self, element_name, fallback_coord=None):
        """
        Click tracked element
        
        Args:
            element_name: element name
            fallback_coord: fallback coordinate (if element location fails)
        
        Returns:
            bool: whether click was successful
        """
        if element_name not in self.tracked_elements:
            print(f"Element '{element_name}' not tracked")
            return False
        
        element_info = self.tracked_elements[element_name]
        
        # Try locating by resourceId
        if element_info.get('resourceId'):
            try:
                self.poco(resourceId=element_info['resourceId']).click()
                print(f"Successfully clicked '{element_name}' by resourceId")
                return True
            except PocoNoSuchNodeException:
                print(f"Failed to locate by resourceId, trying other methods...")
        
        # Try locating by name
        if element_info.get('name'):
            try:
                self.poco(element_info['name']).click()
                print(f"Successfully clicked '{element_name}' by name")
                return True
            except PocoNoSuchNodeException:
                print(f"Failed to locate by name, trying other methods...")
        
        # Try locating by text
        if element_info.get('text'):
            try:
                self.poco(text=element_info['text']).click()
                print(f"Successfully clicked '{element_name}' by text")
                return True
            except PocoNoSuchNodeException:
                print(f"Failed to locate by text, trying other methods...")
        
        # Use fallback coordinate
        if fallback_coord:
            try:
                self.poco.click(fallback_coord)
                print(f"Successfully clicked '{element_name}' by fallback coordinate")
                return True
            except Exception as e:
                print(f"Failed to click by fallback coordinate: {e}")
        
        # Use original coordinate
        if element_info.get('pos'):
            try:
                self.poco.click(element_info['pos'])
                print(f"Successfully clicked '{element_name}' by original coordinate")
                return True
            except Exception as e:
                print(f"Failed to click by original coordinate: {e}")
        
        print(f"All location methods failed, unable to click '{element_name}'")
        return False
    
    def get_tracked_elements(self):
        """Get all tracked elements"""
        return self.tracked_elements
    
    def remove_tracked_element(self, element_name):
        """Remove tracked element"""
        if element_name in self.tracked_elements:
            del self.tracked_elements[element_name]
            print(f"Removed tracked element '{element_name}'")
            return True
        return False


class UIRegionExtractor:
    """UI region extractor - for extracting regions for image recognition"""
    
    def __init__(self, poco):
        self.poco = poco
        self.finder = CoordElementFinder(poco)
    
    def extract_element_region(self, coord, padding=0.01, coord_type='normalized'):
        """
        Extract element region for image recognition
        
        Args:
            coord: coordinate [x, y]
            padding: region padding
            coord_type: coordinate type
        
        Returns:
            dict: region information including normalized and pixel coordinates
        """
        region_info = self.finder.get_element_region_by_coord(coord, coord_type, padding)
        
        if not region_info:
            return None
        
        # Convert to pixel coordinates (if possible)
        try:
            screen_size = self.poco.get_screen_size()
            region = region_info['region']
            
            pixel_region = {
                'left': int(region['left'] * screen_size[0]),
                'top': int(region['top'] * screen_size[1]),
                'right': int(region['right'] * screen_size[0]),
                'bottom': int(region['bottom'] * screen_size[1]),
                'width': int(region['width'] * screen_size[0]),
                'height': int(region['height'] * screen_size[1])
            }
            
            region_info['pixel_region'] = pixel_region
            
        except Exception as e:
            print(f"Unable to get pixel coordinates: {e}")
        
        return region_info
    
    def save_element_screenshot(self, coord, filename, padding=0.01, coord_type='normalized'):
        """
        Save element screenshot
        
        Args:
            coord: coordinate [x, y]
            filename: save filename
            padding: region padding
            coord_type: coordinate type
        
        Returns:
            bool: whether save was successful
        """
        try:
            import base64
            from PIL import Image
            import io
            
            # Get region information
            region_info = self.extract_element_region(coord, padding, coord_type)
            if not region_info:
                return False
            
            # Get screen screenshot
            b64img, fmt = self.poco.snapshot()
            img_data = base64.b64decode(b64img)
            img = Image.open(io.BytesIO(img_data))
            
            # Crop region
            if 'pixel_region' in region_info:
                pixel_region = region_info['pixel_region']
                cropped_img = img.crop((
                    pixel_region['left'],
                    pixel_region['top'],
                    pixel_region['right'],
                    pixel_region['bottom']
                ))
            else:
                # Use normalized coordinates
                region = region_info['region']
                width, height = img.size
                cropped_img = img.crop((
                    int(region['left'] * width),
                    int(region['top'] * height),
                    int(region['right'] * width),
                    int(region['bottom'] * height)
                ))
            
            # Save image
            cropped_img.save(filename)
            print(f"Element screenshot saved: {filename}")
            return True
            
        except Exception as e:
            print(f"Failed to save element screenshot: {e}")
            return False


# Convenience functions
def find_element_by_coord(poco, coord, coord_type='normalized'):
    """Convenience function: find element by coordinate"""
    finder = CoordElementFinder(poco)
    return finder.get_element_by_coord(coord, coord_type)


def get_element_region_for_recognition(poco, coord, padding=0.01, coord_type='normalized'):
    """Convenience function: get element region for image recognition"""
    finder = CoordElementFinder(poco)
    return finder.get_element_region_by_coord(coord, coord_type, padding)


def track_and_click_element(poco, coord, element_name, coord_type='normalized'):
    """Convenience function: track element and click later"""
    tracker = ElementTracker(poco)
    if tracker.track_element_by_coord(coord, element_name, coord_type):
        return tracker.click_tracked_element(element_name, coord)
    return False