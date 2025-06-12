#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

from pygxi.Exception import raise_error
from pygxi.gxwrapper import GxStatusList, gx_get_last_error

ERROR_SIZE = 1024


def check_return_status(status: GxStatusList, class_name: str, function_name: str) -> None:
    """
    Check the return status of a function and raise an exception if the status indicates an error.

    Parameters
    ----------
    status : GxStatusList
        The status code returned by a function.
    class_name : str
        The name of the class where the function is defined.
    function_name : str
        The name of the function being checked.

    Notes
    -----
    The appropriate exception is raised based on the status code.
    """
    if status != GxStatusList.SUCCESS:
        _, _, string = gx_get_last_error(ERROR_SIZE)
        error_message = "%s.%s:%s" % (class_name, function_name, string)
        raise_error(status, error_message)
