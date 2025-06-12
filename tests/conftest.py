import pytest
from src.gxipy import DeviceManager


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


@pytest.fixture
def first_device(request, device_manager, devices_available):
    """
    Open the first available device. Skip the test if no devices are available.
    """
    if not devices_available:
        pytest.skip("No devices available for testing")
    
    dev_info_list = device_manager.update_device_list()
    device = device_manager.open_device_by_index(1)  # Assuming 1-based indexing
    request.addfinalizer(lambda: device.close() if device else None)
    return device