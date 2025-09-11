# coding=utf-8
from __future__ import absolute_import

import warnings

try:
    from airtest.core.device import Device
    from airtest.core.api import connect_device, device as current_device
    from airtest.core.error import NoDeviceError
    AIRTEST_AVAILABLE = True
except ImportError:
    warnings.warn("Airtest not available. Device utilities will be limited.")
    AIRTEST_AVAILABLE = False
    Device = None
    connect_device = current_device = NoDeviceError = None


class VirtualDevice(object):
    def __init__(self, ip):
        if AIRTEST_AVAILABLE and Device:
            super(VirtualDevice, self).__init__()
        self.ip = ip

    @property
    def uuid(self):
        return 'virtual-device'

    def get_current_resolution(self):
        return [1920, 1080]

    def get_ip_address(self):
        return self.ip


def default_device():
    """
    Get default device, if no device connected, connect to first android device.

    :return:
    """
    if not AIRTEST_AVAILABLE:
        return None
    try:
        return current_device()
    except NoDeviceError:
        return connect_device('Android:///')
