import pytest


def test_device_manager_import():
    """Test that the DeviceManager can be imported successfully."""
    from src.gxipy import DeviceManager
    assert DeviceManager is not None


def test_device_list(device_manager):
    """Test that the device list can be retrieved."""
    dev_info_list = device_manager.update_device_list()
    # This test doesn't require a device to be connected
    # It just checks that the function runs without error
    assert isinstance(dev_info_list, list)


@pytest.mark.device_required
def test_device_available(devices_available):
    """Test that at least one device is available."""
    assert devices_available, "No devices are available for testing"