#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

from __future__ import annotations

import pygxi.gxwrapper as gx
from typing import TypedDict

from .Device import Device, GEVDevice, U2Device, U3VDevice
from .errors import InvalidParameterError, DeviceNotFoundError, ParameterTypeError
from .gxidef import UNSIGNED_INT_MAX, GxAccessMode, GxDeviceClassList, GxTLClassList
from .ImageFormatConvert import ImageFormatConvert
from .ImageProcess import ImageProcess
from .Interface import Interface
from .status import check_return_status


class InterfaceInfo(TypedDict):
    """Interface information dictionary."""

    handle: int
    type: int
    display_name: str
    interface_id: str
    serial_number: str
    description: str
    init_flag: int
    reserved: list[int]


class DeviceInfo(TypedDict):
    """Device information dictionary."""

    index: int
    vendor_name: str
    model_name: str
    sn: str
    display_name: str
    device_id: str
    user_id: str
    access_status: int
    device_class: int
    mac: str
    ip: str
    subnet_mask: str
    gateway: str
    nic_mac: str
    nic_ip: str
    nic_subnet_mask: str
    nic_gateWay: str
    nic_description: str


class DeviceManager:
    __instance_num = 0

    def __new__(
        cls,
    ) -> DeviceManager:
        cls.__instance_num += 1
        status = gx.gx_init_lib()
        check_return_status(status, "DeviceManager", "init_lib")
        return object.__new__(cls)

    def __init__(self) -> None:
        self.__device_num = 0
        self.__device_info_list: list[DeviceInfo] = []
        self.__interface_info_list: list[InterfaceInfo] = []
        self.__interface_num = 0

    def __del__(self) -> None:
        self.__class__.__instance_num -= 1
        if self.__class__.__instance_num <= 0:
            status = gx.gx_close_lib()
            check_return_status(status, "DeviceManager", "close_lib")

    def set_log_type(self, log_type: int) -> None:
        """Set whether logs of the specified type can be sent.

        Parameters
        ----------
        log_type : int
            Log type, see details in GxLogTypeList.

        :brief      Set whether logs of the specified type can be sent
        :param      log_type:   log type,See detail in GxLogTypeList
        :return:    status:     State return value, See detail in GxStatusList
        """
        if not isinstance(log_type, int):
            raise ParameterTypeError(
                "DeviceManager.set_log_type: "
                "Expected log type is int, not %s" % type(log_type)
            )

        status = gx.gx_set_log_type(log_type)
        check_return_status(status, "DeviceManager", "set_log_type")

    def get_log_type(self) -> int:
        """
        :brief      Gets whether logs of the specified type can be sent
        :return:    status:      State return value, See detail in GxStatusList
                    log_type:    log type,See detail in GxLogTypeList
        """
        status, log_type = gx.gx_get_log_type()
        check_return_status(status, "DeviceManager", "get_log_type")
        self.__log_type = log_type

        return self.__log_type

    def __create_device(self, device_class: int, device_handle: int) -> Device | U2Device | U3VDevice | GEVDevice:
        status, interface_handle = gx.gx_get_parent_interface_from_device(device_handle)
        check_return_status(status, "DeviceManager", "__create_device")

        index = 0
        for interface_item in self.__interface_info_list:
            if interface_item["handle"] == interface_handle:
                break
            index += index

        if device_class == GxDeviceClassList.U3V:
            return U3VDevice(
                device_handle,
                Interface(interface_handle, self.__interface_info_list[index]),
            )
        elif device_class == GxDeviceClassList.USB2:
            return U2Device(
                device_handle,
                Interface(interface_handle, self.__interface_info_list[index]),
            )
        elif device_class == GxDeviceClassList.GEV:
            return GEVDevice(
                device_handle,
                Interface(interface_handle, self.__interface_info_list[index]),
            )
        elif device_class == GxDeviceClassList.CXP:
            return Device(
                device_handle,
                Interface(interface_handle, self.__interface_info_list[index]),
            )
        else:
            raise DeviceNotFoundError(
                "DeviceManager.__create_device: Does not support this device type."
            )

    def __get_device_info_list(
        self,
        base_info: list[gx.GxDeviceBaseInfo],
        ip_info: list[gx.GxDeviceIPInfo],
        num: int,
    ) -> list[DeviceInfo]:
        """
        :brief      Convert GxDeviceBaseInfo and gx.GxDeviceIPInfo to device info list
        :param      base_info:  device base info list[GxDeviceBaseInfo]
        :param      ip_info:    device ip info list[gx.GxDeviceIPInfo]
        :param      num:        device number
        :return:    device info list
        """
        device_info_list: list[DeviceInfo] = []
        for i in range(num):
            device_info_list.append(
                {
                    "index": i + 1,
                    "vendor_name": gx.string_decoding(base_info[i].vendor_name),
                    "model_name": gx.string_decoding(base_info[i].model_name),
                    "sn": gx.string_decoding(base_info[i].serial_number),
                    "display_name": gx.string_decoding(base_info[i].display_name),
                    "device_id": gx.string_decoding(base_info[i].device_id),
                    "user_id": gx.string_decoding(base_info[i].user_id),
                    "access_status": base_info[i].access_status,
                    "device_class": base_info[i].device_class,
                    "mac": gx.string_decoding(ip_info[i].mac),
                    "ip": gx.string_decoding(ip_info[i].ip),
                    "subnet_mask": gx.string_decoding(ip_info[i].subnet_mask),
                    "gateway": gx.string_decoding(ip_info[i].gateway),
                    "nic_mac": gx.string_decoding(ip_info[i].nic_mac),
                    "nic_ip": gx.string_decoding(ip_info[i].nic_ip),
                    "nic_subnet_mask": gx.string_decoding(ip_info[i].nic_subnet_mask),
                    "nic_gateWay": gx.string_decoding(ip_info[i].nic_gateWay),
                    "nic_description": gx.string_decoding(ip_info[i].nic_description),
                }
            )

        return device_info_list

    def __get_interface_info_list(self) -> tuple[int, list[InterfaceInfo]]:
        """
        :brief      Get GXInterfaceInfo and Convert GXInterfaceInfo to interface info list
        :return:    interface info list
        """
        status, interface_number = gx.gx_get_interface_number()
        check_return_status(status, "DeviceManager", "__get_interface_info_list")

        interface_info_list: list[InterfaceInfo] = []
        for nindex in range(interface_number):
            status, interface_info = gx.gx_get_interface_info(nindex + 1)
            check_return_status(status, "DeviceManager", "__get_interface_info_list")

            status, interface_handle = gx.gx_get_interface_handle(nindex + 1)
            check_return_status(status, "DeviceManager", "__get_interface_info_list")

            if GxTLClassList.TL_TYPE_CXP == interface_info.TLayer_type:
                interface_info_list.append(
                    {
                        "handle": interface_handle,
                        "type": GxTLClassList.TL_TYPE_CXP,
                        "display_name": gx.string_decoding(
                            interface_info.IF_info.CXP_interface_info.display_name
                        ),
                        "interface_id": gx.string_decoding(
                            interface_info.IF_info.CXP_interface_info.interface_id
                        ),
                        "serial_number": gx.string_decoding(
                            interface_info.IF_info.CXP_interface_info.serial_number
                        ),
                        "description": "",
                        "init_flag": interface_info.IF_info.CXP_interface_info.init_flag,
                        "reserved": gx.array_decoding(
                            interface_info.IF_info.CXP_interface_info.reserved
                        ),
                    }
                )
            elif GxTLClassList.TL_TYPE_GEV == interface_info.TLayer_type:
                interface_info_list.append(
                    {
                        "handle": interface_handle,
                        "type": GxTLClassList.TL_TYPE_GEV,
                        "display_name": gx.string_decoding(
                            interface_info.IF_info.GEV_interface_info.display_name
                        ),
                        "interface_id": gx.string_decoding(
                            interface_info.IF_info.GEV_interface_info.interface_id
                        ),
                        "serial_number": gx.string_decoding(
                            interface_info.IF_info.GEV_interface_info.serial_number
                        ),
                        "description": gx.string_decoding(
                            interface_info.IF_info.GEV_interface_info.description
                        ),
                        "init_flag": interface_info.IF_info.GEV_interface_info.init_flag,
                        "reserved": gx.array_decoding(
                            interface_info.IF_info.GEV_interface_info.reserved
                        ),
                    }
                )
            elif GxTLClassList.TL_TYPE_U3V == interface_info.TLayer_type:
                interface_info_list.append(
                    {
                        "handle": interface_handle,
                        "type": GxTLClassList.TL_TYPE_U3V,
                        "display_name": gx.string_decoding(
                            interface_info.IF_info.U3V_interface_info.display_name
                        ),
                        "interface_id": gx.string_decoding(
                            interface_info.IF_info.U3V_interface_info.interface_id
                        ),
                        "serial_number": gx.string_decoding(
                            interface_info.IF_info.U3V_interface_info.serial_number
                        ),
                        "description": gx.string_decoding(
                            interface_info.IF_info.U3V_interface_info.description
                        ),
                        "init_flag": 0,
                        "reserved": gx.array_decoding(
                            interface_info.IF_info.U3V_interface_info.reserved
                        ),
                    }
                )
            elif GxTLClassList.TL_TYPE_USB == interface_info.TLayer_type:
                interface_info_list.append(
                    {
                        "handle": interface_handle,
                        "type": GxTLClassList.TL_TYPE_USB,
                        "display_name": gx.string_decoding(
                            interface_info.IF_info.USB_interface_info.display_name
                        ),
                        "interface_id": gx.string_decoding(
                            interface_info.IF_info.USB_interface_info.interface_id
                        ),
                        "serial_number": gx.string_decoding(
                            interface_info.IF_info.USB_interface_info.serial_number
                        ),
                        "description": gx.string_decoding(
                            interface_info.IF_info.USB_interface_info.description
                        ),
                        "init_flag": 0,
                        "reserved": gx.array_decoding(
                            interface_info.IF_info.USB_interface_info.reserved
                        ),
                    }
                )
            else:
                interface_info_list.append(
                    {
                        "handle": 0,
                        "type": GxTLClassList.TL_TYPE_UNKNOWN,
                        "display_name": "unknown",
                        "interface_id": "",
                        "serial_number": "",
                        "description": "",
                        "init_flag": 0,
                        "reserved": [],
                    }
                )
        return interface_number, interface_info_list

    def __get_ip_info(self, base_info_list, dev_mum):
        """
        :brief      Get the network information
        """

        ip_info_list = []
        for i in range(dev_mum):
            if base_info_list[i].device_class == GxDeviceClassList.GEV:
                status, ip_info = gx.gx_get_device_ip_info(i + 1)
                check_return_status(status, "DeviceManager", "__get_ip_info")
                ip_info_list.append(ip_info)
            else:
                ip_info_list.append(gx.GxDeviceIPInfo())

        return ip_info_list

    def update_device_list(self, timeout: int = 200) -> tuple[int, list[DeviceInfo]]:
        """Enumerate the devices on the same network segment.

        Parameters
        ----------
        timeout : int, optional
            Timeout for API request in milliseconds. Default is 200 ms.

        Returns
        -------
        tuple[int, list[dict[str, Any]]]
            A tuple containing:
            - `int`: The number of devices found (0 if none found).
            - `list[dict[str, Any]]`: List of dictionaries with device information
              (empty list if no devices found).

        """
        if not isinstance(timeout, int):
            raise ParameterTypeError(
                "DeviceManager.update_device_list: "
                "Expected timeout type is int, not %s" % type(timeout)
            )

        if (timeout < 0) or (timeout > UNSIGNED_INT_MAX):
            print(
                "DeviceManager.update_device_list: "
                "timeout out of bounds, timeout: minimum=0, maximum=%s"
                % hex(UNSIGNED_INT_MAX).__str__()
            )
            return 0, []

        status, dev_num = gx.gx_update_device_list(timeout)
        check_return_status(status, "DeviceManager", "update_device_list")

        self.__interface_num, self.__interface_info_list = (
            self.__get_interface_info_list()
        )

        status, base_info_list = gx.gx_get_all_device_base_info(dev_num)
        check_return_status(status, "DeviceManager", "update_device_list")

        ip_info_list = self.__get_ip_info(base_info_list, dev_num)
        self.__device_num = dev_num
        self.__device_info_list = self.__get_device_info_list(
            base_info_list, ip_info_list, dev_num
        )

        return self.__device_num, self.__device_info_list

    def update_device_list_ex(
        self, tl_type: int, timeout=2000
    ) -> tuple[int, list[DeviceInfo]]:
        """ Enumerate the available devices of the specified type.

        Parameters
        ----------
        tl_type : int
            The type of device to enumerate, see details in GxTLClassList.
        timeout : int, optional
            Timeout for API request in milliseconds. Default is 2000 ms.

        Returns
        -------
        tuple[int, list[DeviceInfo]]
            A tuple containing:
            - `int`: The number of devices found (0 if none found).
            - `list[DeviceInfo]`: List of dictionaries with device information
                (empty list if no devices found).
        """
        if not isinstance(timeout, int):
            raise ParameterTypeError(
                "DeviceManager.update_device_list: "
                "Expected timeout type is int, not %s" % type(timeout)
            )

        if (timeout < 0) or (timeout > UNSIGNED_INT_MAX):
            print(
                "DeviceManager.update_device_list: "
                "timeout out of bounds, timeout: minimum=0, maximum=%s"
                % hex(UNSIGNED_INT_MAX).__str__()
            )
            return 0, []

        status, dev_num = gx.gx_update_device_list_ex(tl_type, timeout)
        check_return_status(status, "DeviceManager", "update_device_list_ex")

        self.__interface_num, self.__interface_info_list = (
            self.__get_interface_info_list()
        )

        status, base_info_list = gx.gx_get_all_device_base_info(dev_num)
        check_return_status(status, "DeviceManager", "update_device_list_ex")

        ip_info_list = self.__get_ip_info(base_info_list, dev_num)
        self.__device_num = dev_num
        self.__device_info_list = self.__get_device_info_list(
            base_info_list, ip_info_list, dev_num
        )

        return self.__device_num, self.__device_info_list

    def update_all_device_list(self, timeout: int=200) -> tuple[int, list[DeviceInfo]]:
        """Enumerate devices on different network segments.

        Parameters
        ----------
        timeout : int, optional
            Timeout for API request in milliseconds. Default is 200 ms.

        :brief      Enumerate devices on different network segments
        :param      timeout:    Enumeration timeout, range:[0, 0xFFFFFFFF]
        :return:    dev_num:    device number
                    device_info_list:   all device info list
        """
        if not isinstance(timeout, int):
            raise ParameterTypeError(
                "DeviceManager.update_all_device_list: "
                "Expected timeout type is int, not %s" % type(timeout)
            )

        if (timeout < 0) or (timeout > UNSIGNED_INT_MAX):
            print(
                "DeviceManager.update_all_device_list: "
                "timeout out of bounds, timeout: minimum=0, maximum=%s"
                % hex(UNSIGNED_INT_MAX).__str__()
            )
            return 0, []

        status, dev_num = gx.gx_update_all_device_list(timeout)
        check_return_status(status, "DeviceManager", "update_all_device_list")

        self.__interface_num, self.__interface_info_list = (
            self.__get_interface_info_list()
        )

        status, base_info_list = gx.gx_get_all_device_base_info(dev_num)
        check_return_status(status, "DeviceManager", "update_all_device_list")

        ip_info_list = self.__get_ip_info(base_info_list, dev_num)
        self.__device_num = dev_num
        self.__device_info_list = self.__get_device_info_list(
            base_info_list, ip_info_list, dev_num
        )

        return self.__device_num, self.__device_info_list

    def get_interface_number(self) -> int:
        """
        :brief      Get device number
        :return:    device number
        """
        return self.__interface_num

    def get_interface_info(self) -> list[InterfaceInfo]:
        """
        :brief      Get device number
        :return:    device number
        """
        return self.__interface_info_list

    def get_interface(self, index: int) -> Interface | None:
        """Get the device interface by index.

        Parameters
        ----------
        index : int
            The index of the interface to retrieve.
            Must be a non-zero, positive integer.
        
        Returns
        -------
        Interface | None
            An Interface object if found, or None if the index is invalid.
        """
        if not isinstance(index, int):
            raise ParameterTypeError(
                "DeviceManager.get_interface: "
                "Expected index type is int, not %s" % type(index)
            )

        if index < 1:
            print("DeviceManager.get_interface: index must start from 1")
            return None
        elif index > UNSIGNED_INT_MAX:
            print(
                "DeviceManager.get_interface: index maximum: %s"
                % hex(UNSIGNED_INT_MAX).__str__()
            )
            return None

        if self.__interface_num < index:
            # Re-update the device
            self.update_device_list()
            if self.__interface_num < index:
                raise DeviceNotFoundError("DeviceManager.get_interface: invalid index")

        status, interface_handle = gx.gx_get_interface_handle(index)
        check_return_status(status, "DeviceManager", "get_interface")

        return Interface(interface_handle, self.__interface_info_list[index - 1])

    def get_device_number(self) -> int:
        """
        :brief      Get device number
        :return:    device number
        """
        return self.__device_num

    def get_device_info(self):
        """
        :brief      Get all device info
        :return:    info_dict:      device info list
        """
        return self.__device_info_list

    def open_device_by_index(self, index: int, access_mode: int = GxAccessMode.CONTROL) -> Device | None:
        """Open a new device by index.

        Parameters
        ----------
        index : int
            The index of the device to open.
            Must be a non-zero, positive integer.
        access_mode : int, optional
            The access mode for opening the device. See GxAccessMode for details.
            Default is GxAccessMode.CONTROL.

        :brief      open device by index
                    USB3 device return U3VDevice object
                    USB2 device return U2Device object
                    GEV  device return GEVDevice object
        :param      index:          device index must start from 1
        :param      access_mode:    the access of open device
        :return:    Device object
        """
        if not isinstance(index, int):
            raise ParameterTypeError(
                "DeviceManager.open_device_by_index: "
                "Expected index type is int, not %s" % type(index)
            )

        if not isinstance(access_mode, int):
            raise ParameterTypeError(
                "DeviceManager.open_device_by_index: "
                "Expected access_mode type is int, not %s" % type(access_mode)
            )

        if index < 1:
            print("DeviceManager.open_device_by_index: index must start from 1")
            return None
        elif index > UNSIGNED_INT_MAX:
            print(
                "DeviceManager.open_device_by_index: index maximum: %s"
                % hex(UNSIGNED_INT_MAX).__str__()
            )
            return None

        access_mode_dict = dict(
            (name, getattr(GxAccessMode, name))
            for name in dir(GxAccessMode)
            if not name.startswith("__")
        )
        if access_mode not in access_mode_dict.values():
            print(
                "DeviceManager.open_device_by_index: "
                "access_mode out of bounds, %s" % access_mode_dict.__str__()
            )
            return None

        if self.__device_num < index:
            # Re-update the device
            self.update_device_list()
            if self.__device_num < index:
                raise DeviceNotFoundError(
                    "DeviceManager.open_device_by_index: invalid index"
                )

        # open devices by index
        open_param = gx.GxOpenParam()
        open_param.content = str(index).encode()
        open_param.open_mode = gx.GxOpenMode.INDEX
        open_param.access_mode = access_mode
        status, handle = gx.gx_open_device(open_param)
        check_return_status(status, "DeviceManager", "open_device_by_index")

        # get device class
        device_class = self.__device_info_list[index - 1]["device_class"]

        return self.__create_device(device_class, handle)

    def __get_device_class_by_sn(self, sn):
        """
        :brief:     1.find device by sn in self.__device_info_list
                    2.return different objects according to device class
        :param      sn:      device serial number
        :return:    device class
        """
        for index in range(self.__device_num):
            if self.__device_info_list[index]["sn"] == sn:
                return self.__device_info_list[index]["device_class"]

        # don't find this id in device base info list
        return -1

    def open_device_by_sn(self, sn, access_mode=GxAccessMode.CONTROL):
        """
        :brief      open device by serial number(SN)
                    USB3 device return U3VDevice object
                    USB2 device return U2Device object
                    GEV device return GEVDevice object
        :param      sn:             device serial number, type: str
        :param      access_mode:    the mode of open device[GxAccessMode]
        :return:    Device object
        """
        if not isinstance(sn, str):
            raise ParameterTypeError(
                "DeviceManager.open_device_by_sn: "
                "Expected sn type is str, not %s" % type(sn)
            )

        if not isinstance(access_mode, int):
            raise ParameterTypeError(
                "DeviceManager.open_device_by_sn: "
                "Expected access_mode type is int, not %s" % type(access_mode)
            )

        access_mode_dict = dict(
            (name, getattr(GxAccessMode, name))
            for name in dir(GxAccessMode)
            if not name.startswith("__")
        )
        if access_mode not in access_mode_dict.values():
            print(
                "DeviceManager.open_device_by_sn: "
                "access_mode out of bounds, %s" % access_mode_dict.__str__()
            )
            return None

        # get device class from self.__device_info_list
        device_class = self.__get_device_class_by_sn(sn)
        if device_class == -1:
            # Re-update the device
            self.update_device_list()
            device_class = self.__get_device_class_by_sn(sn)
            if device_class == -1:
                # don't find this sn
                raise DeviceNotFoundError(
                    "DeviceManager.open_device_by_sn: Not found device"
                )

        # open devices by sn
        open_param = gx.GxOpenParam()
        open_param.content = sn.encode()
        open_param.open_mode = gx.GxOpenMode.SN
        open_param.access_mode = access_mode
        status, handle = gx.gx_open_device(open_param)
        check_return_status(status, "DeviceManager", "open_device_by_sn")

        return self.__create_device(device_class, handle)

    def __get_device_class_by_user_id(self, user_id):
        """
        :brief:     1.find device according to sn in self.__device_info_list
                    2.return different objects according to device class
        :param      user_id:        user ID
        :return:    device class
        """
        for index in range(self.__device_num):
            if self.__device_info_list[index]["user_id"] == user_id:
                return self.__device_info_list[index]["device_class"]

        # don't find this id in device base info list
        return -1

    def open_device_by_user_id(self, user_id, access_mode=GxAccessMode.CONTROL):
        """
        :brief      open device by user defined name
                    USB3 device return U3VDevice object
                    GEV  device return GEVDevice object
        :param      user_id:        user defined name, type:str
        :param      access_mode:    the mode of open device[GxAccessMode]
        :return:    Device object
        """
        if not isinstance(user_id, str):
            raise ParameterTypeError(
                "DeviceManager.open_device_by_user_id: "
                "Expected user_id type is str, not %s" % type(user_id)
            )
        elif user_id.__len__() == 0:
            raise InvalidParameterError(
                "DeviceManager.open_device_by_user_id: Don't support user_id's length is 0"
            )

        if not isinstance(access_mode, int):
            raise ParameterTypeError(
                "DeviceManager.open_device_by_user_id: "
                "Expected access_mode type is int, not %s" % type(access_mode)
            )

        access_mode_dict = dict(
            (name, getattr(GxAccessMode, name))
            for name in dir(GxAccessMode)
            if not name.startswith("__")
        )
        if access_mode not in access_mode_dict.values():
            print(
                "DeviceManager.open_device_by_user_id: access_mode out of bounds, %s"
                % access_mode_dict.__str__()
            )
            return None

        # get device class from self.__device_info_list
        device_class = self.__get_device_class_by_user_id(user_id)
        if device_class == -1:
            # Re-update the device
            self.update_device_list()
            device_class = self.__get_device_class_by_user_id(user_id)
            if device_class == -1:
                # don't find this user_id
                raise DeviceNotFoundError(
                    "DeviceManager.open_device_by_user_id: Not found device"
                )

        # open device by user_id
        open_param = gx.GxOpenParam()
        open_param.content = user_id.encode()
        open_param.open_mode = gx.GxOpenMode.USER_ID
        open_param.access_mode = access_mode
        status, handle = gx.gx_open_device(open_param)
        check_return_status(status, "DeviceManager", "open_device_by_user_id")

        return self.__create_device(device_class, handle)

    def open_device_by_ip(self, ip, access_mode=GxAccessMode.CONTROL):
        """
        :brief      open device by device ip address
        :param      ip:             device ip address, type:str
        :param      access_mode:    the mode of open device[GxAccessMode]
        :return:    GEVDevice object
        """
        if not isinstance(ip, str):
            raise ParameterTypeError(
                "DeviceManager.open_device_by_ip: "
                "Expected ip type is str, not %s" % type(ip)
            )

        if not isinstance(access_mode, int):
            raise ParameterTypeError(
                "DeviceManager.open_device_by_ip: "
                "Expected access_mode type is int, not %s" % type(access_mode)
            )

        access_mode_dict = dict(
            (name, getattr(GxAccessMode, name))
            for name in dir(GxAccessMode)
            if not name.startswith("__")
        )
        if access_mode not in access_mode_dict.values():
            print(
                "DeviceManager.open_device_by_ip: access_mode out of bounds, %s"
                % access_mode_dict.__str__()
            )
            return None

        # open device by ip
        open_param = gx.GxOpenParam()
        open_param.content = ip.encode()
        open_param.open_mode = gx.GxOpenMode.IP
        open_param.access_mode = access_mode
        status, handle = gx.gx_open_device(open_param)
        check_return_status(status, "DeviceManager", "open_device_by_ip")

        return self.__create_device(GxDeviceClassList.GEV, handle)

    def open_device_by_mac(self, mac, access_mode=GxAccessMode.CONTROL):
        """
        :brief      open device by device mac address
        :param      mac:            device mac address, type:str
        :param      access_mode:    the mode of open device[GxAccessMode]
        :return:    GEVDevice object
        """
        if not isinstance(mac, str):
            raise ParameterTypeError(
                "DeviceManager.open_device_by_mac: "
                "Expected mac type is str, not %s" % type(mac)
            )

        if not isinstance(access_mode, int):
            raise ParameterTypeError(
                "DeviceManager.open_device_by_mac: "
                "Expected access_mode type is int, not %s" % type(access_mode)
            )

        access_mode_dict = dict(
            (name, getattr(GxAccessMode, name))
            for name in dir(GxAccessMode)
            if not name.startswith("__")
        )
        if access_mode not in access_mode_dict.values():
            print(
                "DeviceManager.open_device_by_mac: access_mode out of bounds, %s"
                % access_mode_dict.__str__()
            )
            return None

        # open device by ip
        open_param = gx.GxOpenParam()
        open_param.content = mac.encode("utf-8")
        open_param.open_mode = gx.GxOpenMode.MAC
        open_param.access_mode = access_mode
        status, handle = gx.gx_open_device(open_param)
        check_return_status(status, "DeviceManager", "open_device_by_mac")

        return self.__create_device(GxDeviceClassList.GEV, handle)

    def gige_reset_device(self, mac_address, reset_device_mode):
        """
        :brief      Reconnection/Reset
        :param      mac_address:        The MAC address of the device(str)
        :param      reset_device_mode:  Reconnection mode, refer to GxResetDeviceModeEntry
        :return:    None
        """
        _InterUtility.check_type(
            mac_address, str, "mac_address", "DeviceManager", "gige_reset_device"
        )
        _InterUtility.check_type(
            reset_device_mode,
            int,
            "reset_device_mode",
            "DeviceManager",
            "gige_reset_device",
        )
        status = gx.gx_gige_reset_device(mac_address, reset_device_mode)
        check_return_status(status, "DeviceManager", "gige_reset_device")

    def gige_force_ip(self, mac_address, ip_address, subnet_mask, default_gate_way):
        """
        :brief      Execute the Force IP
        :param      mac_address:        The MAC address of the device(str)
        :param      ip_address:         Reconnection mode, refer to GxResetDeviceModeEntry
        :param      subnet_mask:        The MAC address of the device(str)
        :param      default_gate_way:  Reconnection mode, refer to GxResetDeviceModeEntry
        :return:    None
        """
        _InterUtility.check_type(
            mac_address, str, "mac_address", "DeviceManager", "gige_force_ip"
        )
        _InterUtility.check_type(
            ip_address, str, "ip_address", "DeviceManager", "gige_force_ip"
        )
        _InterUtility.check_type(
            subnet_mask, str, "subnet_mask", "DeviceManager", "gige_force_ip"
        )
        _InterUtility.check_type(
            default_gate_way, str, "default_gate_way", "DeviceManager", "gige_force_ip"
        )
        status = gx.gx_gige_force_ip(
            mac_address, ip_address, subnet_mask, default_gate_way
        )
        check_return_status(status, "DeviceManager", "gige_force_ip")

    def gige_ip_configuration(
        self,
        mac_address,
        ipconfig_flag,
        ip_address,
        subnet_mask,
        default_gateway,
        user_id,
    ):
        """
        :brief      Execute the Force IP
        :param      mac_address:        The MAC address of the device(str)
        :param      ipconfig_flag:         Reconnection mode, refer to GxResetDeviceModeEntry
        :param      ip_address:        The MAC address of the device(str)
        :param      subnet_mask:         Reconnection mode, refer to GxResetDeviceModeEntry
        :param      default_gateway:        The MAC address of the device(str)
        :param      user_id:  Reconnection mode, refer to GxResetDeviceModeEntry
        :return:    None
        """
        _InterUtility.check_type(
            mac_address, str, "mac_address", "DeviceManager", "gige_ip_configuration"
        )
        _InterUtility.check_type(
            ipconfig_flag,
            int,
            "ipconfig_flag",
            "DeviceManager",
            "gige_ip_configuration",
        )
        _InterUtility.check_type(
            ip_address, str, "ip_address", "DeviceManager", "gige_ip_configuration"
        )
        _InterUtility.check_type(
            subnet_mask, str, "subnet_mask", "DeviceManager", "gige_ip_configuration"
        )
        _InterUtility.check_type(
            default_gateway,
            str,
            "default_gateway",
            "DeviceManager",
            "gige_ip_configuration",
        )
        _InterUtility.check_type(
            user_id, str, "user_id", "DeviceManager", "gige_ip_configuration"
        )
        status = gx.gx_gige_ip_configuration(
            mac_address,
            ipconfig_flag,
            ip_address,
            subnet_mask,
            default_gateway,
            user_id,
        )
        check_return_status(status, "DeviceManager", "gige_ip_configuration")

    def create_image_format_convert(self):
        """
        :brief      create new convert pointer
        :return:    GxImageFormatConvert
        """
        image_format_convert = ImageFormatConvert()
        return image_format_convert

    def create_image_process(self):
        """
        :brief      create image process
        :return:    GxImageFormatConvert
        """
        image_process = ImageProcess()
        return image_process


class _InterUtility:
    def __init__(self):
        pass

    @staticmethod
    def check_type(var, var_type, var_name="", class_name="", func_name=""):
        """
        :chief  check type
        """
        if not isinstance(var, var_type):
            if not isinstance(var_type, tuple):
                raise ParameterTypeError(
                    "{} {}: Expected {} type is {}, not {}".format(
                        class_name,
                        func_name,
                        var_name,
                        var_type.__name__,
                        type(var).__name__,
                    )
                )
            else:
                type_name = ""
                for i, name in enumerate(var_type):
                    type_name = type_name + name.__name__
                    if i != len(var_type) - 1:
                        type_name = type_name + ", "
                raise ParameterTypeError(
                    "{} {}: Expected {} type is ({}), not {}".format(
                        class_name, func_name, var_name, type_name, type(var).__name__
                    )
                )
