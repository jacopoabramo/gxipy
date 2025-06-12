#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

from pygxi.gxwrapper import GxStatusList


class UnexpectedError(Exception):
    """Exception raised for unexpected errors."""


class NoTLFoundError(Exception):
    """Exception raised when a Transport Layer (TL) is not found."""


class DeviceNotFoundError(Exception):
    """Exception raised when a device is not found."""


class DeviceOfflineError(Exception):
    """Exception raised when a device is offline or not connected."""


class InvalidParameterError(Exception):
    """Exception raised for invalid parameters."""


class InvalidHandleError(Exception):
    """Exception raised for invalid handle."""


class InvalidCallError(Exception):
    """Exception raised for invalid function calls."""


class InvalidAccessError(Exception):
    """Exception raised for invalid access to a resource."""


class NotEnoughMemoryError(Exception):
    """Exception raised when more memory is needed for an operation."""


class FeatureTypeError(Exception):
    """Exception raised for feature type errors."""


class OutOfRangeError(Exception):
    """Exception raised when a parameter is out of range."""


class APINotInitializedError(Exception):
    """Exception raised when an API is not initialized."""


class ParameterTypeError(Exception):
    """Exception raised when a parameter type is incorrect."""


def raise_error(status: int, error_msg: str) -> None:
    """Check the incoming status flag and raise the corresponding exception.

    Parameters
    ----------
    status : int
        The status code returned by a function.
    error_msg : str
        The error message to be included in the exception.
    """
    match status:
        case GxStatusList.ERROR:
            raise UnexpectedError(error_msg)
        case GxStatusList.NOT_FOUND_TL:
            raise NoTLFoundError(error_msg)
        case GxStatusList.NOT_FOUND_DEVICE:
            raise DeviceNotFoundError(error_msg)
        case GxStatusList.OFFLINE:
            raise DeviceOfflineError(error_msg)
        case GxStatusList.INVALID_PARAMETER:
            raise InvalidParameterError(error_msg)
        case GxStatusList.INVALID_HANDLE:
            raise InvalidHandleError(error_msg)
        case GxStatusList.INVALID_CALL:
            raise InvalidCallError(error_msg)
        case GxStatusList.INVALID_ACCESS:
            raise InvalidAccessError(error_msg)
        case GxStatusList.NEED_MORE_BUFFER:
            raise NotEnoughMemoryError(error_msg)
        case GxStatusList.ERROR_TYPE:
            raise FeatureTypeError(error_msg)
        case GxStatusList.OUT_OF_RANGE:
            raise OutOfRangeError(error_msg)
        case GxStatusList.NOT_IMPLEMENTED:
            raise NotImplementedError(error_msg)
        case GxStatusList.NOT_INIT_API:
            raise APINotInitializedError(error_msg)
        case GxStatusList.TIMEOUT:
            raise TimeoutError(error_msg)
        case GxStatusList.REPEAT_OPENED:
            raise InvalidAccessError(error_msg)
        case _:
            raise Exception(error_msg)
