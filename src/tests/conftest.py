import pytest
from pygxi import DeviceManager


@pytest.fixture(scope="session")
def device_manager():
    """
    Create a DeviceManager instance for the entire test session.
    """
    return DeviceManager.DeviceManager()


@pytest.fixture(scope="session")
def devices_available(device_manager):
    """
    Check if any devices are available and return the count.
    """
    dev_info_list = device_manager.update_device_list()
    return len(dev_info_list) > 0