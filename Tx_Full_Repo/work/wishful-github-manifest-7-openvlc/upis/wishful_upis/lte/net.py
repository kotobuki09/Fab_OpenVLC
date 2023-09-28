__author__ = "Francesco Giannone, Domenico Garlisi"
__copyright__ = "Copyright (c) 2017, Sant'Anna, CNIT"
__version__ = "0.1.0"
__email__ = "{francesco.giannone@santannapisa.it, domenico.garlisi@cnit.it}"

'''
The protocol-specific definition of the WiSHFUL network control interface, UPI_N, for configuration/monitoring of the higher
layers of the network protocol stack (upper MAC and higher).
LTE protocol family
'''


# Generic API to control the lower layers, i.e. key-value configuration.
def set_parameters(param_key_values_dict):
    '''This function (re)set the value(s) of the parameters specified in the dictionary argument.
    The list of available parameters supported by all platforms/OS are defined in this module.
    Parameters specific to a subgroup of platforms/OS are defined in the corresponding submodules.
    A list of supported parameters can be dynamically obtained using the get_info function on each module.

    Examples:
        .. code-block:: python

            >> UPIargs_eNB = {radio.TX_GAIN_enb.key: 90}
            >> result = controller.node(enb_node).radio.set_parameters(UPIargs_eNB)
            >> print result
                    {TX_GAIN_enb.key: 90}

    Args:
        param_key_values_dict (dict): dictionary containing the key (string) value (any) pairs for each parameter.
        An example is {PUCCH_ENB : -96, MME_REALM : wishful_lte, TX_BANDWIDTH_enb : 25}

    Returns:
        dict: A dictionary containing key (string name) error (0 = success, 1=fail, +1=error code) pairs for each parameter.
    '''
    return


def get_parameters(param_key_list):
    '''This function get(s) the value(s) of the parameters specified in the list argument.
    The list of available parameters supported by all platforms are defined in this module.
    Parameters specific to a subgroup of platforms are defined in the corresponding submodules.

    Example:
        .. code-block:: python

            >> UPIargs_eNB = [TX_GAIN_enb]
            >> result = controller.node(enb_node).radio.get_parameters(UPIargs_eNB)
            >> print result
                {TX_GAIN_enb.key: 90}

    Args:
        param_key_list (list): list of parameter names, an example is [UPI_RN.CSMA_CW, UPI_RN.CSMA_CW_MIN, UPI_RN.CSMA_CW_MAX].

    Returns:
        dict: A dictionary containing key (string name) and values of the requested parameters.
    '''
    return


def MME_activation():
    '''Once set the MME parameters using the set_parameters(param_key_values_dict), MME_activation is to be used for running the MME

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.MME_activation()

    Args:
        controller:
        node: physical machine where the MME run

    Returns:
        0 = success, 1=fail, +1=error code
    '''
    return


def MME_deactivation():
    '''MME_deactivation is to be used for stopping the MME

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.MME_deactivation()

    Args:
        controller:
        node: physical machine where the MME run

    Returns:
        0 = success, 1=fail, +1=error code
    '''
    return


def HSS_activation():
    '''Once set the HSS parameters using the set_parameters(param_key_values_dict), HSS_activation is to be used for running the HSS

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.HSS_activation()

    Args:
        controller:
        node: physical machine where the HSS run

    Returns:
        0 = success, 1=fail, +1=error code
    '''
    return


def HSS_deactivation():
    '''HSS_deactivation is to be used for stopping the HSS

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.HSS_deactivation()

    Args:
        controller:
        node: physical machine where the HSS run

    Returns:
        0 = success, 1=fail, +1=error code
    '''
    return


def SPGW_activation():
    '''Once set the SPGW parameters using the set_parameters(param_key_values_dict), SPGW_activation is to be used for running the SPGW

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.SPGW_activation()

    Args:
        controller:
        node: physical machine where the SPGW run

    Returns:
        0 = success, 1=fail, +1=error code
    '''
    return


def SPGW_deactivation():
    '''SPGW_deactivation is to be used for stopping the SPGW

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.SPGW_deactivation()

    Args:
        controller:
        node: physical machine where the SPGW run

    Returns:
        0 = success, 1=fail, +1=error code
    '''
    return


def eNB_activation():
    '''Once set the eNB parameters using the set_parameters(param_key_values_dict), eNB_activation is to be used for running the eNB

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.eNB_activation()

    Args:
        controller:
        node: physical machine where the eNB run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return


def eNB_deactivation():
    '''eNB_deactivation is to be used for stopping the eNB

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.eNB_deactivation()

    Args:
        controller:
        node: physical machine where the eNB run

    Returns:
        0 = success, 1=fail, +1=error code
    '''
    return


def RRU_activation():
    '''Once set the RRU parameters using the set_parameters(param_key_values_dict), RRU_activation is to be used for running the RRU

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.RRU_activation()

    Args:
        controller:
        node: physical machine where the RRU run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return


def RRU_deactivation():
    '''RRU_deactivation is to be used for stopping the RRU

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.RRU_deactivation()

    Args:
        controller:
        node: physical machine where the RRU run

    Returns:
        0 = success, 1=fail, +1=error code
    '''
    return


def RCC_activation():
    '''Once set the RCC parameters using the set_parameters(param_key_values_dict), RCC_activation is to be used for running the RCC

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.RCC_activation()

    Args:
        controller:
        node: physical machine where the RCC run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return


def RCC_deactivation():
    '''RCC_deactivation is to be used for stopping the RCC

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.RCC_deactivation()

    Args:
        controller:
        node: physical machine where the RCC run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return


def RRU_container_activation():
    '''RRU_container_activation is to be used for running the RRU in a Docker container.

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.RRU_container_activation()

    Args:
        controller:
        node: physical machine where the RRU run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return


def RRU_container_deactivation():
    '''RRU_container_deactivation is to be used for stopping the RRU in a Docker container.

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.RRU_container_activation()

    Args:
        controller:
        node: physical machine where the RRU run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return


def RCC_container_activation():
    '''RCC_container_activation is to be used for running the RCC in a Docker container.

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.RCC_container_deactivation()

    Args:
        controller:
        node: physical machine where the RCC run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return


def RCC_container_deactivation():
    '''RCC_container_deactivation is to be used for stopping the RCC in a Docker container.

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.RCC_container_activation()

    Args:
        controller:
        node: physical machine where the RCC run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return


def UE_activation(central_freq, tx_gain, rx_gain, N_RB):
    '''UE_activation is to be used for running the UE

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.UE_activation()

    Args:
        controller:
        node: physical machine where the UE run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return


def UE_deactivation():
    '''UE_deactivation is to be used for stopping the UE

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.UE_deactivation()

    Args:
        controller:
        node: physical machine where the UE run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return


def UE_attach(central_freq, tx_gain, rx_gain, N_RB):
    '''UE_attach is to be used for attaching the UE to the MME. You can use this UPI only in the multiple eNBs/RRUs scenario

    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.UE_attach()

    Args:
        controller:
        node: physical machine where the UE run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return


def UE_detach():
    '''UE_detach is to be used for detaching the UE without stopping it. You can use this UPI only in the multiple eNBs/RRUs scenario.
    Examples:
        .. code-block:: python

            >> controller.blocking(False).node(node).net.UE_detach()

    Args:
        controller:
        node: physical machine where the UE run

    Returns:
        0 = success, 1=fail, +1=error code'''
    return