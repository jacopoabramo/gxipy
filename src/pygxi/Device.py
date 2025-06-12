#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

import types

import pygxi.Feature as feat
import pygxi.gxwrapper as gx

from .DataStream import DataStream
from .errors import DeviceNotFoundError, ParameterTypeError, UnexpectedError
from .FeatureControl import FeatureControl
from .gxidef import UNSIGNED_INT_MAX
from .ImageProcessConfig import ImageProcessConfig
from .status import check_return_status


class Device:
    """
    The Camera class mainly encapsulates some common operations and function attributes,
    which are the operations and properties usually found in the camera.
    In addition, this class also encapsulates the common operations of  some functions in the C interface,
    such as SetInt, SetFloat, etc. Can not open to the user, so that when the subsequent addition of features,
    Python interface does not upgrade, or only the definition of the control code can support new features
    """

    def __init__(self, handle, interface_obj):
        """
        :brief  Constructor for instance initialization
        :param handle:  Device handle
        """
        self.__dev_handle = handle
        self.data_stream = []
        self.__interface_obj = interface_obj

        self.__c_offline_callback = gx.OFF_LINE_CALL(self.__on_device_offline_callback)
        self.__py_offline_callback = None
        self.__offline_callback_handle = None

        self.__c_feature_callback = gx.FEATURE_CALL(self.__on_device_feature_callback)
        self.__py_feature_callback = None
        self.__color_correction_param = 0

        # Function code function is obsolete, please use string to obtain attribute value
        # ---------------Device Information Section--------------------------
        self.DeviceVendorName = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_DEVICE_VENDOR_NAME
        )
        self.DeviceModelName = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_DEVICE_MODEL_NAME
        )
        self.DeviceFirmwareVersion = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_DEVICE_FIRMWARE_VERSION
        )
        self.DeviceVersion = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_DEVICE_VERSION
        )
        self.DeviceSerialNumber = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_DEVICE_SERIAL_NUMBER
        )
        self.FactorySettingVersion = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_FACTORY_SETTING_VERSION
        )
        self.DeviceUserID = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_DEVICE_USER_ID
        )
        self.DeviceLinkSelector = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_DEVICE_LINK_SELECTOR
        )
        self.DeviceLinkThroughputLimitMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_DEVICE_LINK_THROUGHPUT_LIMIT_MODE
        )
        self.DeviceLinkThroughputLimit = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_DEVICE_LINK_THROUGHPUT_LIMIT
        )
        self.DeviceLinkCurrentThroughput = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_DEVICE_LINK_CURRENT_THROUGHPUT
        )
        self.DeviceReset = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_DEVICE_RESET
        )
        self.TimestampTickFrequency = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_TIMESTAMP_TICK_FREQUENCY
        )
        self.TimestampLatch = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_TIMESTAMP_LATCH
        )
        self.TimestampReset = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_TIMESTAMP_RESET
        )
        self.TimestampLatchReset = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_TIMESTAMP_LATCH_RESET
        )
        self.TimestampLatchValue = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_TIMESTAMP_LATCH_VALUE
        )
        self.DevicePHYVersion = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_DEVICE_PHY_VERSION
        )
        self.DeviceTemperatureSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_DEVICE_TEMPERATURE_SELECTOR
        )
        self.DeviceTemperature = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_DEVICE_TEMPERATURE
        )
        self.DeviceIspFirmwareVersion = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_DEVICE_ISP_FIRMWARE_VERSION
        )
        self.LowPowerMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_LOWPOWER_MODE
        )
        self.CloseCCD = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_CLOSE_CCD
        )
        self.ProductionCode = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_PRODUCTION_CODE
        )
        self.DeviceOriginalName = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_DEVICE_ORIGINAL_NAME
        )
        self.Revision = feat.IntFeature(self.__dev_handle, gx.GxFeatureID.INT_REVISION)
        self.VersionsSupported = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_VERSIONS_SUPPORTED
        )
        self.VersionUsed = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_VERSION_USED
        )
        self.TecEnable = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_TEC_ENABLE
        )
        self.TecTargetTemperature = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_TEC_TARGET_TEMPERATURE
        )
        self.FanEnable = self.TecEnable = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_FAN_ENABLE
        )
        self.TemperatureDetectionStatus = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_TEMPERATURE_DETECTION_STATUS
        )
        self.FanSpeed = feat.IntFeature(self.__dev_handle, gx.GxFeatureID.INT_FAN_SPEED)
        self.DeviceHumidity = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_DEVICE_HUMIDITY
        )
        self.DevicePressure = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_DEVICE_PRESSURE
        )
        self.AirChangeDetectionStatus = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_AIR_CHANGE_DETECTION_STATUS
        )
        self.AirTightnessDetectionStatus = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_AIR_TIGHTNESS_DETECTION_STATUS
        )
        self.DeviceScanType = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_DEVICE_SCAN_TYPE
        )

        # ---------------ImageFormat Section--------------------------------
        self.SensorWidth = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SENSOR_WIDTH
        )
        self.SensorHeight = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SENSOR_HEIGHT
        )
        self.WidthMax = feat.IntFeature(self.__dev_handle, gx.GxFeatureID.INT_WIDTH_MAX)
        self.HeightMax = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_HEIGHT_MAX
        )
        self.OffsetX = feat.IntFeature(self.__dev_handle, gx.GxFeatureID.INT_OFFSET_X)
        self.OffsetY = feat.IntFeature(self.__dev_handle, gx.GxFeatureID.INT_OFFSET_Y)
        self.Width = feat.IntFeature(self.__dev_handle, gx.GxFeatureID.INT_WIDTH)
        self.Height = feat.IntFeature(self.__dev_handle, gx.GxFeatureID.INT_HEIGHT)
        self.BinningHorizontal = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_BINNING_HORIZONTAL
        )
        self.BinningVertical = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_BINNING_VERTICAL
        )
        self.DecimationHorizontal = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_DECIMATION_HORIZONTAL
        )
        self.DecimationVertical = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_DECIMATION_VERTICAL
        )
        self.PixelSize = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_PIXEL_SIZE
        )
        self.PixelColorFilter = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_PIXEL_COLOR_FILTER
        )
        self.PixelFormat = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_PIXEL_FORMAT
        )
        self.ReverseX = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_REVERSE_X
        )
        self.ReverseY = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_REVERSE_Y
        )
        self.TestPattern = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TEST_PATTERN
        )
        self.TestPatternGeneratorSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TEST_PATTERN_GENERATOR_SELECTOR
        )
        self.RegionSendMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_REGION_SEND_MODE
        )
        self.RegionMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_REGION_MODE
        )
        self.RegionSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_REGION_SELECTOR
        )
        self.CenterWidth = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_CENTER_WIDTH
        )
        self.CenterHeight = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_CENTER_HEIGHT
        )
        self.BinningHorizontalMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_BINNING_HORIZONTAL_MODE
        )
        self.BinningVerticalMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_BINNING_VERTICAL_MODE
        )
        self.SensorShutterMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SENSOR_SHUTTER_MODE
        )
        self.DecimationLineNumber = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_DECIMATION_LINENUMBER
        )
        self.SensorDecimationHorizontal = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SENSOR_DECIMATION_HORIZONTAL
        )
        self.SensorDecimationVertical = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SENSOR_DECIMATION_VERTICAL
        )
        self.SensorSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SENSOR_SELECTOR
        )
        self.CurrentSensorWidth = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_CURRENT_SENSOR_WIDTH
        )
        self.CurrentSensorHeight = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_CURRENT_SENSOR_HEIGHT
        )
        self.CurrentSensorOffsetX = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_CURRENT_SENSOR_OFFSETX
        )
        self.CurrentSensorOffsetY = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_CURRENT_SENSOR_OFFSETY
        )
        self.CurrentSensorWidthMax = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_CURRENT_SENSOR_WIDTHMAX
        )
        self.CurrectSensorHeightMax = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_CURRENT_SENSOR_HEIGHTMAX
        )
        self.SensorBitDepth = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SENSOR_BIT_DEPTH
        )
        self.WatermarkEnable = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_WATERMARK_ENABLE
        )

        # ---------------TransportLayer Section-------------------------------
        self.PayloadSize = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_PAYLOAD_SIZE
        )
        self.GevCurrentIPConfigurationLLA = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_LLA
        )
        self.GevCurrentIPConfigurationDHCP = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_DHCP
        )
        self.GevCurrentIPConfigurationPersistentIP = feat.BoolFeature(
            self.__dev_handle,
            gx.GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_PERSISTENT_IP,
        )
        self.EstimatedBandwidth = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_ESTIMATED_BANDWIDTH
        )
        self.GevHeartbeatTimeout = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_GEV_HEARTBEAT_TIMEOUT
        )
        self.GevSCPSPacketSize = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_GEV_PACKET_SIZE
        )
        self.GevSCPD = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_GEV_PACKET_DELAY
        )
        self.GevLinkSpeed = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_GEV_LINK_SPEED
        )
        self.DeviceTapGeometry = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_DEVICE_TAP_GEOMETRY
        )

        # ---------------AcquisitionTrigger Section---------------------------
        self.AcquisitionMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_ACQUISITION_MODE
        )
        self.AcquisitionStart = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_ACQUISITION_START
        )
        self.AcquisitionStop = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_ACQUISITION_STOP
        )
        self.TriggerMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TRIGGER_MODE
        )
        self.TriggerSoftware = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_TRIGGER_SOFTWARE
        )
        self.TriggerActivation = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TRIGGER_ACTIVATION
        )
        self.ExposureTime = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_EXPOSURE_TIME
        )
        self.ExposureAuto = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_EXPOSURE_AUTO
        )
        self.TriggerFilterRaisingEdge = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_TRIGGER_FILTER_RAISING
        )
        self.TriggerFilterFallingEdge = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_TRIGGER_FILTER_FALLING
        )
        self.TriggerSource = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TRIGGER_SOURCE
        )
        self.ExposureMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_EXPOSURE_MODE
        )
        self.TriggerSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TRIGGER_SELECTOR
        )
        self.TriggerDelay = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_TRIGGER_DELAY
        )
        self.TransferControlMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TRANSFER_CONTROL_MODE
        )
        self.TransferOperationMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TRANSFER_OPERATION_MODE
        )
        self.TransferStart = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_TRANSFER_START
        )
        self.TransferBlockCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_TRANSFER_BLOCK_COUNT
        )
        self.FrameBufferOverwriteActive = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_FRAMESTORE_COVER_ACTIVE
        )
        self.AcquisitionFrameRateMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_ACQUISITION_FRAME_RATE_MODE
        )
        self.AcquisitionFrameRate = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_ACQUISITION_FRAME_RATE
        )
        self.CurrentAcquisitionFrameRate = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_CURRENT_ACQUISITION_FRAME_RATE
        )
        self.FixedPatternNoiseCorrectMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_FIXED_PATTERN_NOISE_CORRECT_MODE
        )
        self.AcquisitionBurstFrameCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_ACQUISITION_BURST_FRAME_COUNT
        )
        self.AcquisitionStatusSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_ACQUISITION_STATUS_SELECTOR
        )
        self.AcquisitionStatus = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_ACQUISITION_STATUS
        )
        self.ExposureDelay = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_EXPOSURE_DELAY
        )
        self.ExposureOverlapTimeMax = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_EXPOSURE_OVERLAP_TIME_MAX
        )
        self.ExposureTimeMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_EXPOSURE_TIME_MODE
        )
        self.FrameBufferCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_FRAME_BUFFER_COUNT
        )
        self.FrameBufferFlush = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_FRAME_BUFFER_FLUSH
        )
        self.AcquisitionBurstMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_ACQUISITION_BURST_MODE
        )
        self.OverlapMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_OVERLAP_MODE
        )
        self.MultiSourceSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_MULTISOURCE_SELECTOR
        )
        self.MultiSourceEnable = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_MULTISOURCE_ENABLE
        )
        self.TriggerCacheEnable = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_TRIGGER_CACHE_ENABLE
        )

        # ----------------DigitalIO Section----------------------------------
        self.UserOutputSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_USER_OUTPUT_SELECTOR
        )
        self.UserOutputValue = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_USER_OUTPUT_VALUE
        )
        self.LineSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_LINE_SELECTOR
        )
        self.LineMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_LINE_MODE
        )
        self.LineInverter = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_LINE_INVERTER
        )
        self.LineSource = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_LINE_SOURCE
        )
        self.LineStatus = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_LINE_STATUS
        )
        self.LineStatusAll = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_LINE_STATUS_ALL
        )
        self.PulseWidth = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_PULSE_WIDTH
        )
        self.LineRange = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_LINE_RANGE
        )
        self.LineDelay = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_LINE_DELAY
        )
        self.LineFilterRaisingEdge = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_LINE_FILTER_RAISING_EDGE
        )
        self.LineFilterFallingEdge = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_LINE_FILTER_FALLING_EDGE
        )

        # ----------------AnalogControls Section----------------------------
        self.GainAuto = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_GAIN_AUTO
        )
        self.GainSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_GAIN_SELECTOR
        )
        self.BlackLevelAuto = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_BLACK_LEVEL_AUTO
        )
        self.BlackLevelSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_BLACK_LEVEL_SELECTOR
        )
        self.BalanceWhiteAuto = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_BALANCE_WHITE_AUTO
        )
        self.BalanceRatioSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_BALANCE_RATIO_SELECTOR
        )
        self.BalanceRatio = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_BALANCE_RATIO
        )
        self.DeadPixelCorrect = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_DEAD_PIXEL_CORRECT
        )
        self.Gain = feat.FloatFeature(self.__dev_handle, gx.GxFeatureID.FLOAT_GAIN)
        self.BlackLevel = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_BLACK_LEVEL
        )
        self.GammaEnable = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_GAMMA_ENABLE
        )
        self.GammaMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_GAMMA_MODE
        )
        self.Gamma = feat.FloatFeature(self.__dev_handle, gx.GxFeatureID.FLOAT_GAMMA)
        self.DigitalShift = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_DIGITAL_SHIFT
        )
        self.LightSourcePreset = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_LIGHT_SOURCE_PRESET
        )
        self.BlackLevelCalibStatus = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_BLACKLEVEL_CALIB_STATUS
        )
        self.BlackLevelCalibValue = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_BLACKLEVEL_CALIB_VALUE
        )
        self.PGAGain = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_PGA_GAIN
        )

        # ---------------CustomFeature Section------------------------------
        self.ExpectedGrayValue = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_GRAY_VALUE
        )
        self.AAROIOffsetX = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_AAROI_OFFSETX
        )
        self.AAROIOffsetY = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_AAROI_OFFSETY
        )
        self.AAROIWidth = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_AAROI_WIDTH
        )
        self.AAROIHeight = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_AAROI_HEIGHT
        )
        self.AutoGainMin = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_AUTO_GAIN_MIN
        )
        self.AutoGainMax = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_AUTO_GAIN_MAX
        )
        self.AutoExposureTimeMin = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_AUTO_EXPOSURE_TIME_MIN
        )
        self.AutoExposureTimeMax = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_AUTO_EXPOSURE_TIME_MAX
        )
        self.ContrastParam = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_CONTRAST_PARAM
        )
        self.GammaParam = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_GAMMA_PARAM
        )
        self.ColorCorrectionParam = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_COLOR_CORRECTION_PARAM
        )
        self.AWBLampHouse = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_AWB_LAMP_HOUSE
        )
        self.AWBROIOffsetX = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_AWBROI_OFFSETX
        )
        self.AWBROIOffsetY = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_AWBROI_OFFSETY
        )
        self.AWBROIWidth = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_AWBROI_WIDTH
        )
        self.AWBROIHeight = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_AWBROI_HEIGHT
        )
        self.SharpnessMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SHARPNESS_MODE
        )
        self.Sharpness = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_SHARPNESS
        )
        self.DataFieldSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_USER_DATA_FIELD_SELECTOR
        )
        self.DataFieldValue = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_USER_DATA_FIELD_VALUE
        )
        self.FlatFieldCorrection = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_FLAT_FIELD_CORRECTION
        )
        self.NoiseReductionMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_NOISE_REDUCTION_MODE
        )
        self.NoiseReduction = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_NOISE_REDUCTION
        )
        self.FFCLoad = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_FFCLOAD
        )
        self.FFCSave = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_FFCSAVE
        )
        self.StaticDefectCorrection = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_STATIC_DEFECT_CORRECTION
        )
        self.NoiseReductionMode2D = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_2D_NOISE_REDUCTION_MODE
        )
        self.NoiseReductionMode3D = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_3D_NOISE_REDUCTION_MODE
        )
        self.CloseISP = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_CLOSE_ISP
        )
        self.StaticDefectCorrectionValueAll = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_STATIC_DEFECT_CORRECTION_VALUE_ALL
        )
        self.StaticDefectCorrectionFlashValue = feat.BufferFeature(
            self.__dev_handle,
            gx.GxFeatureID.BUFFER_STATIC_DEFECT_CORRECTION_FLASH_VALUE,
        )
        self.StaticDefectCorrectionFinish = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_STATIC_DEFECT_CORRECTION_FINISH
        )
        self.StaticDefectCorrectionInfo = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_STATIC_DEFECT_CORRECTION_INFO
        )
        self.StripCalibrationStart = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_STRIP_CALIBRATION_START
        )
        self.StripCalibrationStop = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_STRIP_CALIBRATION_STOP
        )
        self.UserDataFiledValueAll = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_USER_DATA_FILED_VALUE_ALL
        )
        self.ShadingCorrectionMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SHADING_CORRECTION_MODE
        )
        self.FFCGenerate = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_FFC_GENERATE
        )
        self.FFCGenerateStatus = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_FFC_GENERATE_STATUS
        )
        self.FFCExpectedGrayValueEnable = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_FFC_EXPECTED_GRAY_VALUE_ENABLE
        )
        self.FFCExpectedGray = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_FFC_EXPECTED_GRAY
        )
        self.FFCCoeffinientsSize = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_FFC_COEFFICIENTS_SIZE
        )
        self.FFCValueAll = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_FFC_VALUE_ALL
        )
        self.DSNUSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_DSNU_SELECTOR
        )
        self.DSNUGenerate = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_DSNU_GENERATE
        )
        self.DSNUGenerateStatus = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_DSNU_GENERATE_STATUS
        )
        self.DSNUSave = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_DSNU_SAVE
        )
        self.DSNULoad = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_DSNU_LOAD
        )
        self.PRNUSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_PRNU_SELECTOR
        )
        self.PRNUGenerate = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_PRNU_GENERATE
        )
        self.PRNUGenerateStatus = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_PRNU_GENERATE_STATUS
        )
        self.PRNUSave = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_PRNU_SAVE
        )
        self.PRNULoad = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_PRNU_LOAD
        )
        self.DataFieldValueAll = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_USER_DATA_FILED_VALUE_ALL
        )
        self.StaticDefectCorrectionCalibStatus = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_STATIC_DEFECT_CORRECTION_CALIB_STATUS
        )
        self.FFCFactoryStatus = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_FFC_FACTORY_STATUS
        )
        self.DSNUFactoryStatus = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_DSNU_FACTORY_STATUS
        )
        self.PRNUFactoryStatus = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_PRNU_FACTORY_STATUS
        )
        self.Detect = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_DETECT
        )
        self.FFCCoefficient = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_FFC_COEFFICIENT
        )
        self.FFCFlashLoad = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_FFCFLASH_LOAD
        )
        self.FFCFlashSave = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_FFCFLASH_SAVE
        )

        # ---------------UserSetControl Section-------------------------------
        self.UserSetSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_USER_SET_SELECTOR
        )
        self.UserSetLoad = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_USER_SET_LOAD
        )
        self.UserSetSave = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_USER_SET_SAVE
        )
        self.UserSetDefault = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_USER_SET_DEFAULT
        )
        self.DataFieldValueAllUsedStatus = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_DATA_FIELD_VALUE_ALL_USED_STATUS
        )

        # ---------------Event Section----------------------------------------
        self.EventSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_EVENT_SELECTOR
        )
        self.EventNotification = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_EVENT_NOTIFICATION
        )
        self.EventExposureEnd = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_EXPOSURE_END
        )
        self.EventExposureEndTimestamp = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_EXPOSURE_END_TIMESTAMP
        )
        self.EventExposureEndFrameID = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_EXPOSURE_END_FRAME_ID
        )
        self.EventBlockDiscard = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_BLOCK_DISCARD
        )
        self.EventBlockDiscardTimestamp = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_BLOCK_DISCARD_TIMESTAMP
        )
        self.EventOverrun = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_OVERRUN
        )
        self.EventOverrunTimestamp = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_OVERRUN_TIMESTAMP
        )
        self.EventFrameStartOvertrigger = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_FRAME_START_OVER_TRIGGER
        )
        self.EventFrameStartOvertriggerTimestamp = feat.IntFeature(
            self.__dev_handle,
            gx.GxFeatureID.INT_EVENT_FRAME_START_OVER_TRIGGER_TIMESTAMP,
        )
        self.EventBlockNotEmpty = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_BLOCK_NOT_EMPTY
        )
        self.EventBlockNotEmptyTimestamp = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_BLOCK_NOT_EMPTY_TIMESTAMP
        )
        self.EventInternalError = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_INTERNAL_ERROR
        )
        self.EventInternalErrorTimestamp = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_INTERNAL_ERROR_TIMESTAMP
        )
        self.EventFrameBurstStartOvertrigger = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_FRAMEBURSTSTART_OVERTRIGGER
        )
        self.EventFrameBurstStartOvertriggerFrameID = feat.IntFeature(
            self.__dev_handle,
            gx.GxFeatureID.INT_EVENT_FRAMEBURSTSTART_OVERTRIGGER_FRAMEID,
        )
        self.EventFrameBurstStartOvertriggerTimestamp = feat.IntFeature(
            self.__dev_handle,
            gx.GxFeatureID.INT_EVENT_FRAMEBURSTSTART_OVERTRIGGER_TIMESTAMP,
        )
        self.EventFrameStartWait = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_FRAMESTART_WAIT
        )
        self.EventFrameStartWaitTimestamp = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_FRAMESTART_WAIT_TIMESTAMP
        )
        self.EventFrameBurstStartWait = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_FRAMEBURSTSTART_WAIT
        )
        self.EventFrameBurstStartWaitTimestamp = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_FRAMEBURSTSTART_WAIT_TIMESTAMP
        )
        self.EventBlockDiscardFrameID = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_BLOCK_DISCARD_FRAMEID
        )
        self.EventFrameStartOvertriggerFrameID = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_FRAMESTART_OVERTRIGGER_FRAMEID
        )
        self.EventBlockNotEmptyFrameID = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_BLOCK_NOT_EMPTY_FRAMEID
        )
        self.EventFrameStartWaitFrameID = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_FRAMESTART_WAIT_FRAMEID
        )
        self.EventFrameBurstStartWaitFrameID = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_EVENT_FRAMEBURSTSTART_WAIT_FRAMEID
        )
        self.EventSimpleMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_EVENT_SIMPLE_MODE
        )

        # ---------------LUT Section------------------------------------------
        self.LUTSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_LUT_SELECTOR
        )
        self.LUTValueAll = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_LUT_VALUE_ALL
        )
        self.LUTEnable = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_LUT_ENABLE
        )
        self.LUTIndex = feat.IntFeature(self.__dev_handle, gx.GxFeatureID.INT_LUT_INDEX)
        self.LUTValue = feat.IntFeature(self.__dev_handle, gx.GxFeatureID.INT_LUT_VALUE)
        self.LUTFactoryStatus = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_LUT_FACTORY_STATUS
        )

        # ---------------ChunkData Section------------------------------------
        self.ChunkModeActive = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_CHUNK_MODE_ACTIVE
        )
        self.ChunkSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_CHUNK_SELECTOR
        )
        self.ChunkEnable = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_CHUNK_ENABLE
        )

        # ---------------Color Transformation Control-------------------------
        self.ColorTransformationMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_COLOR_TRANSFORMATION_MODE
        )
        self.ColorTransformationEnable = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_COLOR_TRANSFORMATION_ENABLE
        )
        self.ColorTransformationValueSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_COLOR_TRANSFORMATION_VALUE_SELECTOR
        )
        self.ColorTransformationValue = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_COLOR_TRANSFORMATION_VALUE
        )
        self.SaturationMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SATURATION_MODE
        )
        self.Saturation = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SATURATION
        )

        # ---------------CounterAndTimerControl Section-----------------------
        self.TimerSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TIMER_SELECTOR
        )
        self.TimerDuration = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_TIMER_DURATION
        )
        self.TimerDelay = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_TIMER_DELAY
        )
        self.TimerTriggerSource = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TIMER_TRIGGER_SOURCE
        )
        self.CounterSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_COUNTER_SELECTOR
        )
        self.CounterEventSource = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_COUNTER_EVENT_SOURCE
        )
        self.CounterResetSource = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_COUNTER_RESET_SOURCE
        )
        self.CounterResetActivation = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_COUNTER_RESET_ACTIVATION
        )
        self.CounterReset = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_COUNTER_RESET
        )
        self.CounterTriggerSource = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_COUNTER_TRIGGER_SOURCE
        )
        self.CounterDuration = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_COUNTER_DURATION
        )
        self.TimerTriggerActivation = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TIMER_TRIGGER_ACTIVATION
        )
        self.CounterValue = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_COUNTER_VALUE
        )

        # ---------------RemoveParameterLimitControl Section------------------
        self.RemoveParameterLimit = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_REMOVE_PARAMETER_LIMIT
        )

        # ---------------HDRControl Section------------------
        self.HDRMode = feat.EnumFeature(self.__dev_handle, gx.GxFeatureID.ENUM_HDR_MODE)
        self.HDRTargetLongValue = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_HDR_TARGET_LONG_VALUE
        )
        self.HDRTargetShortValue = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_HDR_TARGET_SHORT_VALUE
        )
        self.HDRTargetMainValue = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_HDR_TARGET_MAIN_VALUE
        )

        # ---------------MultiGrayControl Section------------------
        self.MGCMode = feat.EnumFeature(self.__dev_handle, gx.GxFeatureID.ENUM_MGC_MODE)
        self.MGCSelector = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_MGC_SELECTOR
        )
        self.MGCExposureTime = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_MGC_EXPOSURE_TIME
        )
        self.MGCGain = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_MGC_GAIN
        )

        # ---------------ImageQualityControl Section------------------
        self.StripedCalibrationInfo = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_STRIPED_CALIBRATION_INFO
        )
        self.Contrast = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_CONTRAST
        )
        self.HotPixelCorrection = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_HOTPIXEL_CORRECTION
        )

        # ---------------GyroControl Section------------------
        self.IMUData = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_IMU_DATA
        )
        self.IMUConfigAccRange = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_IMU_CONFIG_ACC_RANGE
        )
        self.IMUConfigAccOdrLowPassFilterSwitch = feat.EnumFeature(
            self.__dev_handle,
            gx.GxFeatureID.ENUM_IMU_CONFIG_ACC_ODR_LOW_PASS_FILTER_SWITCH,
        )
        self.IMUConfigAccOdr = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_IMU_CONFIG_ACC_ODR
        )
        self.IMUConfigAccOdrLowPassFilterFrequency = feat.EnumFeature(
            self.__dev_handle,
            gx.GxFeatureID.ENUM_IMU_CONFIG_ACC_ODR_LOW_PASS_FILTER_FREQUENCY,
        )
        self.IMUConfigGyroXRange = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_IMU_CONFIG_GYRO_XRANGE
        )
        self.IMUConfigGyroYRange = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_IMU_CONFIG_GYRO_YRANGE
        )
        self.IMUConfigGyroZRange = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_IMU_CONFIG_GYRO_ZRANGE
        )
        self.IMUConfigGyroOdrLowPassFilterSwitch = feat.EnumFeature(
            self.__dev_handle,
            gx.GxFeatureID.ENUM_IMU_CONFIG_GYRO_ODR_LOW_PASS_FILTER_SWITCH,
        )
        self.IMUConfigGyroOdr = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_IMU_CONFIG_GYRO_ODR
        )
        self.IMUConfigGyroOdrLowPassFilterFrequency = feat.EnumFeature(
            self.__dev_handle,
            gx.GxFeatureID.ENUM_IMU_CONFIG_GYRO_ODR_LOW_PASS_FILTER_FREQUENCY,
        )
        self.IMURoomTemperature = feat.FloatFeature(
            self.__dev_handle, gx.GxFeatureID.FLOAT_IMU_ROOM_TEMPERATURE
        )
        self.IMUTemperatureOdr = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_IMU_TEMPERATURE_ODR
        )

        # ---------------FrameBufferControl Section------------------
        self.FrameBufferCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_FRAME_BUFFER_COUNT
        )
        self.FrameBufferFlush = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_FRAME_BUFFER_FLUSH
        )

        # ---------------SerialPortControl Section------------------
        self.DeviceSerialPortSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SERIALPORT_SELECTOR
        )
        self.SerialPortSource = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SERIALPORT_SOURCE
        )
        self.DeviceSerialPortBaudRate = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SERIALPORT_BAUDRATE
        )
        self.SerialPortDataBits = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SERIALPORT_DATA_BITS
        )
        self.SerialPortStopBits = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SERIALPORT_STOP_BITS
        )
        self.SerialPortParity = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SERIALPORT_PARITY
        )
        self.TransmitQueueMaxCharacterCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_TRANSMIT_QUEUE_MAX_CHARACTER_COUNT
        )
        self.TransmitQueueCurrentCharacterCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_TRANSMIT_QUEUE_CURRENT_CHARACTER_COUNT
        )
        self.ReceiveQueueMaxCharacterCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_RECEIVE_QUEUE_MAX_CHARACTER_COUNT
        )
        self.ReceiveQueueCurrentCharacterCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_RECEIVE_QUEUE_CURRENT_CHARACTER_COUNT
        )
        self.ReceiveFramingErrorCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_RECEIVE_FRAMING_ERROR_COUNT
        )
        self.ReceiveParityErrorCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_RECEIVE_PARITY_ERROR_COUNT
        )
        self.ReceiveQueueClear = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_RECEIVE_QUEUE_CLEAR
        )
        self.SerialPortData = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_SERIALPORT_DATA
        )
        self.SerialPortDataLength = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SERIALPORT_DATA_LENGTH
        )
        self.SerialPortDetectionStatus = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SERIAL_PORT_DETECTION_STATUS
        )

        # ---------------CoaXPress Section------------------
        self.CxpLinkConfiguration = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_CXP_LINK_CONFIGURATION
        )
        self.CxpLinkConfigurationPreferred = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_CXP_LINK_CONFIGURATION_PREFERRED
        )
        self.CxpLinkConfigurationStatus = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_CXP_LINK_CONFIGURATION_STATUS
        )
        self.Image1StreamID = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_IMAGE1_STREAM_ID
        )
        self.CxpConnectionSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_CXP_CONNECTION_SELECTOR
        )
        self.CxpConnectionTestMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_CXP_CONNECTION_TEST_MODE
        )
        self.CxpConnectionTestErrorCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_RECEIVE_FRAMING_ERROR_COUNT
        )
        self.CxpConnectionTestPacketRxCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_RECEIVE_FRAMING_ERROR_COUNT
        )
        self.CxpConnectionTestPacketTxCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_RECEIVE_FRAMING_ERROR_COUNT
        )

        # ---------------SequencerControl Section------------------
        self.SequencerMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SEQUENCER_MODE
        )
        self.SequencerConfigurationMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SEQUENCER_CONFIGURATION_MODE
        )
        self.SequencerFeatureSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SEQUENCER_FEATURE_SELECTOR
        )
        self.SequencerFeatureEnable = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_SEQUENCER_FEATURE_ENABLE
        )
        self.SequencerSetSelector = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SEQUENCER_SET_SELECTOR
        )
        self.SequencerSetCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SEQUENCER_SET_COUNT
        )
        self.SequencerSetActive = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SEQUENCER_SET_ACTIVE
        )
        self.SequencerSetReset = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_SEQUENCER_SET_RESET
        )
        self.SequencerPathSelector = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SEQUENCER_PATH_SELECTOR
        )
        self.SequencerSetNext = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_SEQUENCER_SET_NEXT
        )
        self.SequencerTriggerSource = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_SEQUENCER_TRIGGER_SOURCE
        )
        self.SequencerSetSave = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_SEQUENCER_SET_SAVE
        )
        self.SequencerSetLoad = feat.CommandFeature(
            self.__dev_handle, gx.GxFeatureID.COMMAND_SEQUENCER_SET_LOAD
        )

        # ---------------EnoderControl Section------------------
        self.EncoderSelector = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_ENCODER_SELECTOR
        )
        self.EncoderDirection = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_ENCODER_DIRECTION
        )
        self.EncoderValue = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_ENCODER_VALUE
        )
        self.EncoderSourceA = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_ENCODER_SOURCEA
        )
        self.EncoderSourceB = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_ENCODER_SOURCEB
        )
        self.EncoderMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_ENCODER_MODE
        )
        self.__get_stream_handle()

    def __get_stream_handle(self):
        """
        :brief      Get stream handle and create stream object
        :return:
        """
        status, data_stream_num = gx.gx_data_stream_number_from_device(
            self.__dev_handle
        )
        check_return_status(status, "Device", "__get_stream_handle")

        for index in range(data_stream_num):
            status, stream_handle = gx.gx_get_data_stream_handle_from_device(
                self.__dev_handle, index + 1
            )
            check_return_status(status, "Device", "__get_stream_handle")

            self.data_stream.append(DataStream(self.__dev_handle, stream_handle))

    def get_stream_channel_num(self):
        """
        :brief      Get the number of stream channels supported by the current device.
        :return:    the number of stream channels
        """
        return len(self.data_stream)

    def get_parent_interface(self):
        """
        :brief      Get interface
        :return:    Interface
        """
        return self.__interface_obj

    def close_device(self):
        """
        :brief      close device, close device handle
        :return:    None
        """
        status = gx.gx_close_device(self.__dev_handle)
        check_return_status(status, "Device", "close_device")
        self.__dev_handle = None
        self.__py_offline_callback = None
        self.__offline_callback_handle = None
        self.__py_feature_callback = None

    def get_stream_number(self):
        """
        :brief      Get the number of stream channels supported by the current device.
        :return:    the number of stream channels
        """
        return len(self.__data_stream_handle)

    def get_stream(self, stream_index):
        """
        :brief      Get stream object
        :param stream_index:    stream index
        :return: stream object
        """
        if not isinstance(stream_index, int):
            raise ParameterTypeError(
                "Device.get_stream: "
                "Expected stream_index type is int, not %s" % type(stream_index)
            )

        if stream_index < 1:
            print("Device.get_stream: stream_index must start from 1")
            return None
        elif stream_index > UNSIGNED_INT_MAX:
            print(
                "Device.get_stream: stream_index maximum: %s"
                % hex(len(self.data_stream)).__str__()
            )
            return None

        if len(self.data_stream) < stream_index:
            raise DeviceNotFoundError("Device.get_stream: invalid index")

        return self.data_stream[stream_index - 1]

    def get_local_device_feature_control(self):
        """
        :brief      Get local device layer feature control object
        :return:    Local device layer feature control object
        """
        status, local_handle = gx.gx_local_device_handle_from_device(self.__dev_handle)
        check_return_status(status, "Device", "register_device_offline_callback")
        feature_control = FeatureControl(local_handle)
        return feature_control

    def get_remote_device_feature_control(self):
        """
        :brief      Get remote device layer feature control object
        :return:    Remote device layer feature control object
        """
        feature_control = FeatureControl(self.__dev_handle)
        return feature_control

    def register_device_offline_callback(self, callback_func):
        """
        :brief      Register the device offline event callback function.
                    Interface is obsolete.
        :param      callback_func:  callback function
        :return:    none
        """
        if not isinstance(callback_func, types.FunctionType):
            raise ParameterTypeError(
                "Device.register_device_offline_callback: "
                "Expected callback type is function not %s" % type(callback_func)
            )

        status, offline_callback_handle = gx.gx_register_device_offline_callback(
            self.__dev_handle, self.__c_offline_callback
        )
        check_return_status(status, "Device", "register_device_offline_callback")

        # callback will not recorded when register callback failed.
        self.__py_offline_callback = callback_func
        self.__offline_callback_handle = offline_callback_handle

    def unregister_device_offline_callback(self):
        """
        :brief      Unregister the device offline event callback function.
                    Interface is obsolete.
        :return:    none
        """
        status = gx.gx_unregister_device_offline_callback(
            self.__dev_handle, self.__offline_callback_handle
        )
        check_return_status(status, "Device", "unregister_device_offline_callback")
        self.__py_offline_callback = None
        self.__offline_callback_handle = None

    def __on_device_offline_callback(self, c_user_param):
        """
        :brief      Device offline event callback function with an unused c_void_p.
                    Interface is obsolete.
        :return:    none
        """
        self.__py_offline_callback()

    # The following interfaces are obsolete.
    def stream_on(self, stream_index=0):
        """
        :brief      send start command, camera start transmission image data
                    Interface is obsolete.
        :return:    none
        """
        status = gx.gx_send_command(
            self.__dev_handle, gx.GxFeatureID.COMMAND_ACQUISITION_START
        )
        check_return_status(status, "Device", "stream_on")

        payload_size = self.data_stream[0].get_payload_size()
        self.data_stream[0].set_payload_size(payload_size)
        self.data_stream[0].set_acquisition_flag(True)

    def stream_off(self, stream_index=0):
        """
        :brief      send stop command, camera stop transmission image data
                    Interface is obsolete.
        :return:    none
        """
        status = gx.gx_send_command(
            self.__dev_handle, gx.GxFeatureID.COMMAND_ACQUISITION_STOP
        )
        check_return_status(status, "Device", "stream_off")
        self.data_stream[0].set_acquisition_flag(False)

    def export_config_file(self, file_path):
        """
        :brief      Export the current configuration file
                    Interface is obsolete.
        :param      file_path:      file path(type: str)
        :return:    none
        """
        if not isinstance(file_path, str):
            raise ParameterTypeError(
                "Device.export_config_file: "
                "Expected file_path type is str, not %s" % type(file_path)
            )

        status = gx.gx_export_config_file(self.__dev_handle, file_path)
        check_return_status(status, "Device", "export_config_file")

    def import_config_file(self, file_path, verify=False):
        """
        :brief      Imported configuration file
                    Interface is obsolete.
        :param      file_path:  file path(type: str)
        :param      verify:     If this value is true, all the imported values will be read out
                                and checked for consistency(type: bool)
        :return:    none
        """
        if not isinstance(file_path, str):
            raise ParameterTypeError(
                "Device.import_config_file: "
                "Expected file_path type is str, not %s" % type(file_path)
            )

        if not isinstance(verify, bool):
            raise ParameterTypeError(
                "Device.import_config_file: "
                "Expected verify type is bool, not %s" % type(verify)
            )

        status = gx.gx_import_config_file(self.__dev_handle, file_path, verify)
        check_return_status(status, "Device", "import_config_file")

    def register_device_feature_callback(self, callback_func, feature_id, args):
        """
        :brief      Register the device feature event callback function.
        :param      callback_func:  callback function
        :param      feature_id:     feature id
        :return:    none
        """
        if not isinstance(callback_func, types.FunctionType):
            raise ParameterTypeError(
                "Device.register_device_feature_callback: "
                "Expected callback type is function not %s" % type(callback_func)
            )

        if feature_id not in vars(gx.GxFeatureID).values():
            raise ParameterTypeError(
                "Device.register_device_feature_callback: "
                "Expected feature id is in GxEventSectionEntry not %s" % feature_id
            )

        status, feature_callback_handle = gx.gx_register_feature_callback(
            self.__dev_handle, self.__c_feature_callback, feature_id, args
        )
        check_return_status(status, "Device", "register_device_feature_callback")

        # callback will not recorded when register callback failed.
        self.__py_feature_callback = callback_func
        return feature_callback_handle

    def register_device_feature_callback_by_string(
        self, callback_func, feature_name, args
    ):
        """
        :brief      Register the device feature event callback function.
        :param      callback_func:  callback function
        :param      feature_id:     feature id
        :return:    none
        """
        if not isinstance(callback_func, types.FunctionType):
            raise ParameterTypeError(
                "Device.register_device_feature_callback: "
                "Expected callback type is function not %s" % type(callback_func)
            )

        if not isinstance(feature_name, str):
            raise ParameterTypeError(
                "Device.register_device_feature_callback: "
                "Expected feature id is in GxEventSectionEntry not %s" % feature_name
            )

        status, feature_callback_handle = gx.gx_register_feature_call_back_by_string(
            self.__dev_handle, self.__c_feature_callback, feature_name, args
        )
        check_return_status(status, "Device", "register_device_feature_callback")

        # callback will not recorded when register callback failed.
        self.__py_feature_callback = callback_func
        return feature_callback_handle

    def unregister_device_feature_callback(self, feature_id, feature_callback_handle):
        """
        :brief      Unregister the device feature event callback function.
        :return:    none
        """
        if feature_id not in vars(gx.GxFeatureID).values():
            raise ParameterTypeError(
                "Device.unregister_device_feature_callback: "
                "Expected feature id is in GxEventSectionEntry not %s" % feature_id
            )

        status = gx.gx_unregister_feature_callback(
            self.__dev_handle, feature_id, feature_callback_handle
        )
        check_return_status(status, "Device", "unregister_device_feature_callback")

        self.__py_feature_callback = None

    def unregister_device_feature_callback_by_string(
        self, feature_name, feature_callback_handle
    ):
        """
        :brief      Unregister the device feature event callback function.
        :return:    none
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError(
                "Device.unregister_device_feature_callback: "
                "Expected feature id is in GxEventSectionEntry not %s" % feature_name
            )

        status = gx.gx_unregister_feature_call_back_by_string(
            self.__dev_handle, feature_name, feature_callback_handle
        )
        check_return_status(status, "Device", "unregister_device_feature_callback")

        self.__py_feature_callback = None

    def __on_device_feature_callback(self, c_feature_id, c_user_param):
        """
        :brief      Device feature event callback function with an unused c_void_p.
        :return:    none
        """
        self.__py_feature_callback(c_feature_id, c_user_param)

    def read_remote_device_port(self, address, buff, size):
        """
        :brief      Read Remote Regesiter
                    Interface is obsolete.
        :param      address:    The address of the register to be read(type: int)
        :param      bytearray:  The data to be read from register(type: buffer)
        :return:    Read Remote Regesiter Data Buff
        """
        if not isinstance(address, int):
            raise ParameterTypeError(
                "Device.read_remote_device_port: "
                "Expected address type is int, not %s" % type(address)
            )

        if not isinstance(size, int):
            raise ParameterTypeError(
                "Device.read_remote_device_port: "
                "Expected size type is int, not %s" % type(size)
            )

        status, read_result = gx.gx_read_remote_device_port(
            self.__dev_handle, address, buff, size
        )
        check_return_status(status, "Device", "read_remote_device_port")

        return status

    def write_remote_device_port(self, address, buf, size):
        """
        :brief      Write remote register
                    Interface is obsolete.
        :param      address:    The address of the register to be written.(type: int)
        :param      bytearray:  The data to be written from user.(type: buffer)
        :return:    none
        """
        if not isinstance(address, int):
            raise ParameterTypeError(
                "Device.write_remote_device_port: "
                "Expected address type is int, not %s" % type(address)
            )

        status, r_size = gx.gx_write_remote_device_port(
            self.__dev_handle, address, buf, size
        )
        check_return_status(status, "Device", "write_remote_device_port")

    def read_remote_device_port_stacked(self, entries, size):
        """
        :brief        Batch read the value of a user-specified register (only for registers with a command value of 4 bytes in length)
        :entries      [in]Batch read register addresses and values
                      [out]Read the data to the corresponding register
        :read_num     [in]Read the number of device registers
                      [out]The number of registers that were successfully read
        :return:    none
        """
        if not isinstance(size, int):
            raise ParameterTypeError(
                "Device.set_read_remote_device_port_stacked: "
                "Expected size type is int, not %s" % type(size)
            )

        status = gx.gx_set_read_remote_device_port_stacked(
            self.__dev_handle, entries, size
        )
        check_return_status(status, "Device", "read_remote_device_port_stacked")

        return status

    def write_remote_device_port_stacked(self, entries, size):
        """
        :brief        Batch read the value of a user-specified register (only for registers with a command value of 4 bytes in length)
        :entries      [in]The address and value of the batch write register
        :read_num     [in]Sets the number of device registers
                      [out]The number of registers that were successfully written
        :return:    none
        """
        if not isinstance(size, int):
            raise ParameterTypeError(
                "Device.set_read_remote_device_port_stacked: "
                "Expected size type is int, not %s" % type(size)
            )

        status = gx.gx_set_write_remote_device_port_stacked(
            self.__dev_handle, entries, size
        )
        check_return_status(status, "Device", "set_write_remote_device_port_stacked")

    def create_image_process_config(self):
        """
        :brief      Create an image processing configuration parameter object
        :return:    image processing configuration object
        """
        color_correction_param = self.__color_correction_param

        remote_feature_control = self.get_remote_device_feature_control()
        if remote_feature_control.is_implemented("ColorCorrectionParam"):
            if remote_feature_control.is_readable("ColorCorrectionParam"):
                color_correction_param = remote_feature_control.get_int_feature(
                    "ColorCorrectionParam"
                ).get()
            else:
                raise UnexpectedError("ColorCorrectionParam does not support read")

        image_process_config = ImageProcessConfig(color_correction_param)
        return image_process_config

    def set_device_persistent_ip_address(self, ip, subnet_mask, default_gate_way):
        """
        brief:  Set the persistent IP information of the device
        return: Success:    feature name
                Failed:     convert feature ID to string
        """
        status = gx.gx_set_device_persistent_ip_address(
            self.__dev_handle, ip, subnet_mask, default_gate_way
        )
        check_return_status(status, "Device", "set_device_persistent_ip_address")

    def get_device_persistent_ip_address(self):
        """
        brief:  Set the persistent IP information of the device
        return: Success:    feature name
                Failed:     convert feature ID to string
        """
        status, ip, subnet_mask, default_gateway = (
            gx.gx_get_device_persistent_ip_address(self.__dev_handle)
        )
        check_return_status(status, "Device", "get_device_persistent_ip_address")
        return status, ip, subnet_mask, default_gateway


class GEVDevice(Device):
    def __init__(self, handle, interface_obj):
        self.__dev_handle = handle
        Device.__init__(self, self.__dev_handle, interface_obj)
        self.GevCurrentIPConfigurationLLA = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_LLA
        )
        self.GevCurrentIPConfigurationDHCP = feat.BoolFeature(
            self.__dev_handle, gx.GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_DHCP
        )
        self.GevCurrentIPConfigurationPersistentIP = feat.BoolFeature(
            self.__dev_handle,
            gx.GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_PERSISTENT_IP,
        )
        self.EstimatedBandwidth = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_ESTIMATED_BANDWIDTH
        )
        self.GevHeartbeatTimeout = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_GEV_HEARTBEAT_TIMEOUT
        )
        self.GevSCPSPacketSize = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_GEV_PACKET_SIZE
        )
        self.GevSCPD = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_GEV_PACKET_DELAY
        )
        self.GevLinkSpeed = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_GEV_LINK_SPEED
        )
        self.DeviceCommandTimeout = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_COMMAND_TIMEOUT
        )
        self.DeviceCommandRetryCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_COMMAND_RETRY_COUNT
        )


class U3VDevice(Device):
    """
    The U3VDevice class inherits from the Device class. In addition to inheriting the properties of the Device,
    the U3V Device has special attributes such as bandwidth limitation, URBSetting, frame info, etc.
    """

    def __init__(self, handle, interface_obj):
        self.__dev_handle = handle
        Device.__init__(self, self.__dev_handle, interface_obj)


class U2Device(Device):
    """
    The U2Device class inherits from the Device class
    """

    def __init__(self, handle, interface_obj):
        self.__dev_handle = handle
        Device.__init__(self, self.__dev_handle, interface_obj)
        self.AcquisitionSpeedLevel = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_ACQUISITION_SPEED_LEVEL
        )
        self.AcquisitionFrameCount = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_ACQUISITION_FRAME_COUNT
        )
        self.TriggerSwitch = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_TRIGGER_SWITCH
        )
        self.UserOutputMode = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_USER_OUTPUT_MODE
        )
        self.StrobeSwitch = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_STROBE_SWITCH
        )
        self.ADCLevel = feat.IntFeature(self.__dev_handle, gx.GxFeatureID.INT_ADC_LEVEL)
        self.HBlanking = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_H_BLANKING
        )
        self.VBlanking = feat.IntFeature(
            self.__dev_handle, gx.GxFeatureID.INT_V_BLANKING
        )
        self.UserPassword = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_USER_PASSWORD
        )
        self.VerifyPassword = feat.StringFeature(
            self.__dev_handle, gx.GxFeatureID.STRING_VERIFY_PASSWORD
        )
        self.UserData = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_USER_DATA
        )
        self.AALightEnvironment = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_AA_LIGHT_ENVIRONMENT
        )
        self.FrameInformation = feat.BufferFeature(
            self.__dev_handle, gx.GxFeatureID.BUFFER_FRAME_INFORMATION
        )
        self.ImageGrayRaiseSwitch = feat.EnumFeature(
            self.__dev_handle, gx.GxFeatureID.ENUM_IMAGE_GRAY_RAISE_SWITCH
        )
