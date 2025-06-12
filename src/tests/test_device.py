import pytest


@pytest.mark.device_required
def test_device_open(first_device):
    """Test that a device can be opened."""
    assert first_device is not None, "Failed to open device"


@pytest.mark.device_required
def test_device_info(first_device):
    """Test that device information can be retrieved."""
    vendor_name = first_device.DeviceVendorName.get()
    model_name = first_device.DeviceModelName.get()
    serial_number = first_device.DeviceSN.get()
    
    assert vendor_name, "Vendor name is empty"
    assert model_name, "Model name is empty"
    assert serial_number, "Serial number is empty"
    
    print(f"\nDevice Info: {vendor_name} {model_name} (SN: {serial_number})")


@pytest.mark.device_required
def test_device_features(first_device):
    """Test that common device features can be accessed."""
    # Just test that these properties exist and don't raise exceptions
    assert hasattr(first_device, "Width")
    assert hasattr(first_device, "Height")
    assert hasattr(first_device, "PixelFormat")
    
    # Try to get some values (these should not raise exceptions)
    width = first_device.Width.get()
    height = first_device.Height.get()
    
    assert isinstance(width, int), "Width should be an integer"
    assert isinstance(height, int), "Height should be an integer"
    assert width > 0, "Width should be positive"
    assert height > 0, "Height should be positive"