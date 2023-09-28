__author__ = "Francesco Giannone, Domenico Garlisi"
__copyright__ = "Copyright (c) 2017, Sant'Anna, CNIT"
__version__ = "0.1.0"
__email__ = "{francesco.giannone@santannapisa.it, domenico.garlisi@cnit.it}"

import time
import logging
import subprocess
from subprocess import Popen, PIPE
from datetime import date, datetime
import os
from os import remove
from shutil import move
import sys

import wishful_framework as wishful_module
import functional_split
import wishful_upis as upis
import wishful_upis.lte.meta_radio as radio
import wishful_upis.lte.meta_net as net
import wishful_framework as wishful_module
from wishful_framework.classes import exceptions
from functional_split import Functional_split
from subprocess import check_output


#for setting the environmental variable with the path to the openairinterface root folder.
os.environ["OAI_5G_PATH"] = "/root/openairinterface5g/targets"
OPENAIR_5G_PATH=os.environ["OAI_5G_PATH"]

MME_CONF_FILENAME = "/usr/local/etc/oai/mme.conf"
SPGW_CONF_FILENAME = "/usr/local/etc/oai/spgw.conf"
ENB_CONF_FILENAME = "/usr/local/etc/oai/enb.band7.tm1.usrpb210.conf"
RRU_CONF_FILENAME = "/usr/local/etc/oai/rru.band7.tm1.usrpb210.conf"
RRU_IF5_CONF_FILENAME = "/usr/local/etc/oai/rru.band7.tm1.if5.usrpb210.conf"
RCC_CONF_FILENAME = "/usr/local/etc/oai/rcc.band7.tm1.usrpb210.conf"
RCC_IF5_CONF_FILENAME = "/usr/local/etc/oai/rcc.band7.tm1.if5.usrpb210.conf"

@wishful_module.build_module
class LteModule(wishful_module.AgentModule):
    def __init__(self):
        super(LteModule, self).__init__()
        self.log = logging.getLogger('lte_module.main')

        # Dictionary for the matching the value to the relative SET/GET functions of NET_UPI
        self.param_key_functions_dict = {
            'LTE_EPC_MCC' : {'set': self.set_mme_mcc, 'get': self.get_mme_mcc},
            'LTE_EPC_MNC' : {'set': self.set_mme_mnc, 'get': self.get_mme_mnc},            
            'LTE_EPC_OP' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_AMF' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_ENB_ADD' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_ENB_DEL' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_ENB_LIST' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_SUBSCRIBER_ADD' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_SUBSCRIBER_DEL' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_SUBSCRIBER_LIST' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_SUBSCRIBER_GROUP_ADD' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_SUBSCRIBER_GROUP_DEL' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_SUBSCRIBER_GROUP_LIST' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_APN_ADD' : {'set': self.set_default_dns_addr, 'get': self.get_default_dns_addr},
            'LTE_EPC_APN_DEL' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_APN_LIST' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_RNTI' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_EPC_HSS_ADDRESS' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},

            # 'LTE_EPC_HSS_DIAMETER_ADDRESS' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_EPC_SGW_GTPU_IP_ADDRESS' : {'set': self.set_sgw_addr_s1u_s12_s4, 'get': self.get_sgw_addr_s1u_s12_s4},
            # 'LTE_EPC_SGW_GTPC_IP_ADDRESS ' : {'set': self.set_sgw_addr_s11, 'get': self.get_sgw_addr_s11},
            # 'LTE_EPC_MME_NAME' : {'set': self.set_mme_realm, 'get': self.get_mme_realm},
            # 'LTE_EPC_MME_CODE' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_EPC_MME_GID' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_EPC_MME_GUMMEI' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_EPC_MME_MAX_ENB' : {'set': self.set_mme_served_enb, 'get': self.get_mme_served_enb},
            # 'LTE_EPC_MME_MAX_UE' : {'set': self.set_mme_served_ue, 'get': self.get_mme_served_ue},
            # 'LTE_EPC_MME_TAI_LIST' : {'set': self.set_mme_tai_list, 'get': self.get_mme_tai_list},
            # 'LTE_EPC_MME_GUMMEI_LIST' : {'set': self.set_mme_gummei_list, 'get': self.get_mme_gummei_list},
            # 'LTE_EPC_MME_GTPC_ADDRESS' : {'set': self.set_mme_addr_s11, 'get': self.get_mme_addr_s11},
            # 'LTE_EPC_MME_S1AP_ADDRESS' : {'set': self.set_mme_addr_s1, 'get': self.get_mme_addr_s1},
            # 'LTE_EPC_MME_DIAMETER_ADDRESS' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_EPC_PGW_GTPU_IP_ADDRESS': {'set': self.set_sgw_addr_s5_s8, 'get': self.get_sgw_addr_s5_s8},
            # 'LTE_EPC_PGW_GTPC_IP_ADDRESS': {'set': self.set_sgw_addr_s5_s8, 'get': self.get_sgw_addr_s5_s8},
            # 'LTE_EPC_PGW_DL_AMBR' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_EPC_PGW_UL_AMBR' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_EPC_RESTART' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_EPC_DETACH_UE' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'SPLIT_LEVEL': {'set': Functional_split.set_split_level, 'get': Functional_split.get_split_level},
            # 'FRONTHAUL_TRANSPORT_MODE': {'set': self.set_fronthaul_transport_mode, 'get': self.get_fronthaul_transport_mode},     

            # 'mme_S1_name': {'set': self.set_mme_name_s1, 'get': self.get_mme_name_s1},
            # 'mme_S11_name': {'set': self.set_mme_name_s11, 'get': self.get_mme_name_s11},
            # 'mme_s11_port': {'set': self.set_mme_port_s11, 'get': self.get_mme_port_s11},
            # 'sgw_S11_name': {'set': self.set_sgw_name_s11, 'get': self.get_sgw_name_s11},
            # 'sgw_S1U_S12_S4_name': {'set': self.set_sgw_name_s1u_s12_s4, 'get': self.get_sgw_name_s1u_s12_s4},
            # 'sgw_S5_S8_name': {'set': self.set_sgw_name_s5_s8, 'get': self.get_sgw_name_s5_s8},
            # 'pgw_S5_S8_name': {'set': self.set_pgw_name_s5_s8, 'get': self.get_pgw_name_s5_s8},
            # 'enb_name_s1': {'set': self.set_enb_name_s1, 'get': self.get_enb_name_s1},
            # 'enb_s1_addr': {'set': self.set_enb_addr_s1, 'get': self.get_enb_addr_s1},
            # 'enb_name_s1u': {'set': self.set_enb_name_s1u, 'get': self.get_enb_name_s1u}, 
            # 'rcc_name_s1': {'set': self.set_rcc_name_s1, 'get': self.get_rcc_name_s1},
            # 'rcc_addr_s1': {'set': self.set_rcc_addr_s1, 'get': self.get_rcc_addr_s1},
            # 'rcc_name_s1u': {'set': self.set_rcc_name_s1u, 'get': self.get_rcc_name_s1u},
            # 'rcc_port_s1u': {'set': self.set_rcc_port_s1u, 'get': self.get_rcc_port_s1u},

            'LTE_ENB_NM': {'set': self.set_enb_name, 'get': self.get_enb_name},
            'LTE_ENB_ID': {'set': self.set_enb_id, 'get': self.get_enb_id},
            'LTE_ENB_CT': {'set': self.set_enb_cell_type, 'get': self.get_enb_cell_type},
            'LTE_ENB_PLMN': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_ENB_TAC': {'set': self.set_enb_tracking_area_code, 'get': self.get_enb_tracking_area_code},
            'LTE_ENB_MME': {'set': self.set_enb_mme_ip_addr, 'get': self.get_enb_mme_ip_addr},
            'LTE_ENB_PGW': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_ENB_SGW': {'set': self.set_enb_addr_s1u, 'get': self.get_enb_addr_s1u},           
            'LTE_ENB_PHY_CELL_ID' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_ENB_MCC': {'set': self.set_enb_mcc, 'get': self.get_enb_mcc},
            'LTE_ENB_MNC': {'set': self.set_enb_mnc, 'get': self.get_enb_mnc},

            # 'LTE_ENB_LOCAL_SCTP_PORT' : {'set': self.set_enb_port_s1u, 'get': self.get_enb_port_s1u},
            # 'LTE_ENB_EPC_SCTP_PORT' : {'set': self.set_sgw_port_s1u_s12_s4, 'get': self.get_sgw_port_s1u_s12_s4},
            # 'LTE_ENB_MAX_ERAB' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_PUSCH_POWER_CONTROL_STATE' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_PDCCH_POWER_CONTROL_STATE' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_SINR_PUCCH_POWER_CONTROL_STATE' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_HARQ_PUCCH_POWER_CONTROL_STATE' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_FREQUENCY_PUSCH_POWER_CONTROL_STATE' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_PUCCH_TARGET_SINR' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_PUCCH_TARGET_BLER' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_PDCH_POWER_OFFSET' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_PSCH_POWER_OFFSET' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_SSCH_POWER_OFFSET' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_RACH_PREAMBLES' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_MCS_DL' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_MCS_UL' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_RADIO_STATE' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_CQI_REPORT_STATE' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_UE_REPORT_STATE' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_UE_INACTIVITY_TIMER' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            # 'LTE_ENB_CIPHER_ALGORITHM_LIST' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},

            'LTE_ENB_DL_BW': {'set': self.set_tx_bandwidth_enb, 'get': self.get_tx_bandwidth_enb},
            'LTE_ENB_UL_BW': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_ENB_DL_FREQ': {'set': self.set_tx_channel_enb, 'get': self.get_tx_channel_enb},
            'LTE_ENB_UL_FREQ': {'set': self.set_ul_freq_offset_enb, 'get': self.get_ul_freq_offset_enb},
            'LTE_ENB_FREQ_BAND': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_ENB_N_TX_ANT': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_ENB_N_RX_ANT': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_ENB_REF_SIG_POWER': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_ENB_TX_GAIN': {'set': self.set_tx_gain_enb, 'get': self.get_tx_gain_enb},
            'LTE_ENB_RX_GAIN': {'set': self.set_rx_gain_enb, 'get': self.get_rx_gain_enb},
            'LTE_ENB_DUPLEX_MODE': {'set': self.set_tx_mode_enb, 'get': self.get_tx_mode_enb},
            'LTE_ENB_TDD_CONFIGURATION': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'PUCCH_ENB': {'set': self.set_pucch_enb, 'get': self.get_pucch_enb},
            #'PUSCH_ENB': {'set': self.set_pusch_enb, 'get': self.get_pusch_enb},

            #'LTE_RCC_NM': {'set': self.set_rcc_name, 'get': self.get_rcc_name},
            #'LTE_RCC_ID': {'set': self.set_rcc_id, 'get': self.get_rcc_id},
            #'LTE_RCC_CT': {'set': self.set_rcc_cell_type, 'get': self.get_rcc_cell_type},
            #'LTE_RCC_PLMN': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RCC_TAC': {'set': self.set_rcc_tracking_area_code, 'get': self.get_rcc_tracking_area_code},
            #'LTE_RCC_MME': {'set': self.set_rcc_mme_ip_addr, 'get': self.get_rcc_mme_ip_addr},
            #'LTE_RCC_PGW': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RCC_SGW': {'set': self.set_rcc_addr_s1u, 'get': self.get_rcc_addr_s1u},
            'LTE_RCC_FRONTHAUL_IF_NAME_LOCAL': {'set': self.set_rcc_local_if_name, 'get': self.get_rcc_local_if_name},
            'LTE_RCC_FRONTHAUL_IP_ADDRESS_LOCAL': {'set': self.set_rcc_local_addr, 'get': self.get_rcc_local_addr},
            'LTE_RCC_FRONTHAUL_PORT_LOCAL': {'set': self.set_rcc_local_port, 'get': self.get_rcc_local_port},
            'LTE_RCC_FRONTHAUL_IP_ADDRESS_REMOTE': {'set': self.set_rcc_remote_addr, 'get': self.get_rcc_remote_addr},
            'LTE_RCC_FRONTHAUL_PORT_REMOTE': {'set': self.set_rcc_remote_port, 'get': self.get_rcc_remote_port},
            #'LTE_RCC_MCC': {'set': self.set_rcc_mcc, 'get': self.get_rcc_mcc},
            #'LTE_RCC_MNC': {'set': self.set_rcc_mnc, 'get': self.get_rcc_mnc},
            #'LTE_RCC_DL_BW': {'set': self.set_tx_bandwidth_rcc, 'get': self.get_tx_bandwidth_rcc},
            #'LTE_RCC_UL_BW': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RCC_DL_FREQ': {'set': self.set_tx_channel_rcc, 'get': self.get_tx_channel_rcc},
            #'LTE_RCC_UL_FREQ': {'set': self.set_ul_freq_offset_rcc, 'get': self.get_ul_freq_offset_rcc},
            #'LTE_RCC_FREQ_BAND': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RCC_N_TX_ANT': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RCC_N_RX_ANT': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RCC_REF_SIG_POWER': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RCC_TX_GAIN': {'set': self.set_tx_gain_rcc, 'get': self.get_tx_gain_rcc},
            #'LTE_RCC_RX_GAIN': {'set': self.set_rx_gain_rcc, 'get': self.get_rx_gain_rcc},
            #'LTE_RCC_DUPLEX_MODE': {'set': self.set_tx_mode_rcc, 'get': self.get_tx_mode_rcc},
            #'LTE_RCC_TDD_CONFIGURATION': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'PUCCH_RCC': {'set': self.set_pucch_rcc, 'get': self.get_pucch_rcc},
            #'PUSCH_RCC': {'set': self.set_pusch_rcc, 'get': self.get_pusch_rcc}, 

            #'LTE_RRU_NM': {'set': self.set_rru_name, 'get': self.get_rru_name},
            #'LTE_RRU_ID': {'set': self.set_rru_id, 'get': self.get_rru_id},
            #'LTE_RRU_CT': {'set': self.set_rru_cell_type, 'get': self.get_rru_cell_type},
            #'LTE_RRU_PLMN': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RRU_TAC': {'set': self.set_rru_tracking_area_code, 'get': self.get_rru_tracking_area_code},
            'LTE_RRU_FRONTHAUL_IF_NAME_LOCAL': {'set': self.set_rru_local_if_name, 'get': self.get_rru_local_if_name},
            'LTE_RRU_FRONTHAUL_IP_ADDRESS_LOCAL': {'set': self.set_rru_local_addr, 'get': self.get_rru_local_addr},
            'LTE_RRU_FRONTHAUL_PORT_LOCAL': {'set': self.set_rru_local_port, 'get': self.get_rru_local_port},
            'LTE_RRU_FRONTHAUL_IP_ADDRESS_REMOTE': {'set': self.set_rru_remote_addr, 'get': self.get_rru_remote_addr},  
            'LTE_RRU_FRONTHAUL_PORT_REMOTE': {'set': self.set_rru_remote_port, 'get': self.get_rru_remote_port},          
            #'LTE_RRU_MCC': {'set': self.set_rru_mcc, 'get': self.get_rru_mcc},
            #'LTE_RRU_MNC': {'set': self.set_rru_mnc, 'get': self.get_rru_mnc},      
            #'LTE_RRU_DL_BW': {'set': self.set_tx_bandwidth_rru, 'get': self.get_tx_bandwidth_rru},
            #'LTE_RRU_UL_BW': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RRU_DL_FREQ': {'set': self.set_tx_channel_rru, 'get': self.get_tx_channel_rru},
            #'LTE_RRU_UL_FREQ': {'set': self.set_ul_freq_offset_rru, 'get': self.get_ul_freq_offset_rru},
            #'LTE_RRU_FREQ_BAND': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RRU_N_TX_ANT': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RRU_N_RX_ANT': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RRU_REF_SIG_POWER': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'LTE_RRU_TX_GAIN': {'set': self.set_tx_gain_rru, 'get': self.get_tx_gain_rru},
            #'LTE_RRU_RX_GAIN': {'set': self.set_rx_gain_rru, 'get': self.get_rx_gain_rru},
            #'LTE_RRU_DUPLEX_MODE': {'set': self.set_tx_mode_rru, 'get': self.get_tx_mode_rru},
            #'LTE_RRU_TDD_CONFIGURATION': {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            #'PUCCH_RRU': {'set': self.set_pucch_rru, 'get': self.get_pucch_rru},
            #'PUSCH_RRU': {'set': self.set_pusch_rru, 'get': self.get_pusch_rru},

            'LTE_UE_APN' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_UE_PLMN' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_UE_DL_FREQ' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_UE_DL_BW' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_UE_UL_BW' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_UE_TX_GAIN' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_UE_RX_GAIN' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_UE_N_TX_ANT' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_UE_N_RX_ANT' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},
            'LTE_UE_RADIO_STATE' : {'set': self.set_not_implemented, 'get': self.get_not_implemented},

            # 'UE_network_address_pool ': {'set': self.set_ue_ip_addr_pool, 'get': self.get_ue_ip_addr_pool},
        }

    @wishful_module.bind_function(upis.net.set_parameters)
    def set_parameters(self, param_key_values_dict):
        """The UPI_N interface is able to configure the protocol (routing, transport, application) behavior by changing parameters.
        Parameters correspond to the  variables used in the protocols.
        This function (re)set the value(s) of the parameters specified in the dictionary argument.
        The list of available parameters supported by all platforms/OS are defined in this module.
        Parameters specific to a subgroup of platforms/OS are defined in the corresponding submodules.
        A list of supported parameters can be dynamically obtained using the get_info function on each module.
        Examples:
            .. code-block:: python
                >> param_key_values = {ROUTING_MAX_TTL : 5}
                >> result = control_engine.net.set_parameters(param_key_values)
                >> print result
                {ROUTING_MAX_TTL : 0}
        Args:
            param_key_values_dict (dict): dictionary containing the key (string) value (any) pairs for each parameter.
                An example is {CSMA_CW : 15, CSMA_CW_MIN : 15, CSMA_CW_MAX : 15}
        Returns:
            dict: A dictionary containing key (string name) error (0 = success, 1=fail, +1=error code) pairs for each parameter.
        """
        dict_return_set = {}
        for param_key, value in param_key_values_dict.items():
            try:
                print(param_key)
                print(value)
                ret = self.param_key_functions_dict[param_key]['set'](value)
            except (Exception) as err:
                print("exception", err)
                print("Error: unable to performs set_parameters")
                ret = 1
            dict_return_set[param_key] = ret
        return dict_return_set

    @wishful_module.bind_function(upis.net.get_parameters)
    def get_parameters(self, param_key_list):
        """Get the parameter on higher layers of protocol stack (higher MAC and above)
        Args:
             param_key_list: must a list of the parameters identified by their key.
        Returns:
            a dictionary of the pair (parameter key , value)
        """

        dict_return_get = {}
        for key in param_key_list:
            try:
                value = self.param_key_functions_dict[key]['get']()
                dict_return_get[key] = value
            except:
                pass
        return dict_return_get

    @wishful_module.bind_function(upis.net.HSS_activation)
    def HSS_activation(self):
        cmd = 'sudo /root/openair-cn/scripts/run_hss'
        # os.system(cmd_1)
        #return
        p1 = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        output1 = p1.communicate()[0]
        return

    @wishful_module.bind_function(upis.net.HSS_deactivation)
    def HSS_deactivation(self):
        cmd_1 = 'sudo pkill oai_hss'
        os.system(cmd_1)
        print("HSS_Deactivated")
        return

    @wishful_module.bind_function(upis.net.MME_activation)
    def MME_activation(self):
        cmd = 'sudo /root/openair-cn/scripts/run_mme'
        #os.system(cmd_1)
        #return
        p2 = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        output2 = p2.communicate()[0]
        return

    @wishful_module.bind_function(upis.net.MME_deactivation)
    def MME_deactivation(self):
        cmd_1 = 'sudo pkill mme'
        os.system(cmd_1)
        print("MME Dectivated")
        return

    @wishful_module.bind_function(upis.net.SPGW_activation)
    def SPGW_activation(self):
        cmd = 'sudo /root/openair-cn/scripts/run_spgw'
        #os.system(cmd_1)
        #return
        p3 = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        output3 = p3.communicate()[0]
        return

    @wishful_module.bind_function(upis.net.SPGW_deactivation)
    def SPGW_deactivation(self):
        cmd_1 = 'sudo pkill spgw'
        os.system(cmd_1)
        print("SPGW Deactivated")
        return
        
    @wishful_module.bind_function(upis.net.eNB_activation)
    def eNB_activation(self):
        #md = 'sudo -E /root/openairinterface5g/targets/bin/classic_eNB/lte-softmodem.Rel14'
        #option = '-O /usr/local/etc/oai/enb.band7.tm1.usrpb210.conf'
        # os.system(cmd_1)
        # return
        p4 = subprocess.Popen(['sudo -E /root/openairinterface5g/targets/bin/classic_eNB/lte-softmodem.Rel14 -O /usr/local/etc/oai/enb.band7.tm1.usrpb210.conf'], stdout=subprocess.PIPE, shell=True)
        output4 = p4.communicate()[0]
        return

    @wishful_module.bind_function(upis.net.eNB_deactivation)
    def eNB_deactivation(self):
        os.system('sudo pkill lte-softmodem')
        return
         
    @wishful_module.bind_function(upis.net.RRU_activation)
    def RRU_activation(self):
        # cmd_1 = 'sudo -E /root/openairinterface5g/targets/bin/C-RAN/lte-softmodem.Rel14 -O /usr/local/etc/oai/rru.band7.tm1.usrpb210.conf'
        # os.system(cmd_1)
        p5 = subprocess.Popen(['sudo -E /root/openairinterface5g/targets/bin/C-RAN/lte-softmodem.Rel14 -O /usr/local/etc/oai/rru.band7.tm1.usrpb210.conf'], stdout=subprocess.PIPE, shell=True)
        output5 = p5.communicate()[0]
        return

    @wishful_module.bind_function(upis.net.RRU_deactivation)
    def RRU_deactivation(self):
        os.system('sudo pkill lte-softmodem')
        return

    @wishful_module.bind_function(upis.net.RCC_activation)
    def RCC_activation(self):
        # cmd_1 = 'sudo -E /root/openairinterface5g/targets/bin/lte-softmodem.Rel14 -O /usr/local/etc/oai/rcc.band7.tm1.usrpb210.conf'
        # os.system(cmd_1)
        p6 = subprocess.Popen(['sudo -E /root/openairinterface5g/targets/bin/C-RAN/lte-softmodem.Rel14 -O /usr/local/etc/oai/rcc.band7.tm1.usrpb210.conf'], stdout=subprocess.PIPE, shell=True)
        output6 = p6.communicate()[0]
        return

    @wishful_module.bind_function(upis.net.RCC_deactivation)
    def RCC_deactivation(self):
        os.system('sudo pkill lte-softmodem')
        print("RRU Deactivated")
        return

    @wishful_module.bind_function(upis.net.RRU_container_activation)
    def RRU_container_activation(self):
        #os.system('sudo docker start RRU1')
        #print("Docker Container RRU Started")
        # os.system('sudo docker exec -d RRU1 ./openairinterface5g/targets/bin/lte-softmodem.Rel14 -O usr/local/etc/oai/rru.band7.tm1.usrpb210.conf')
        # print("Docker Containerized RRU process started")
        p7 = subprocess.Popen(['sudo docker exec -d RRU1 ./openairinterface5g/targets/bin/lte-softmodem.Rel14 -O usr/local/etc/oai/rru.band7.tm1.usrpb210.conf'], stdout=subprocess.PIPE, shell=True)
        output7 = p7.communicate()[0]
        return

    @wishful_module.bind_function(upis.net.RRU_container_deactivation)
    def RRU_container_deactivation(self):
        #os.system('sudo docker stop RRU1')
        #print("Docker Container RRU Stopped")
        os.system('sudo docker exec -d RRU1 pkill -u root -f lte-softmodem.Rel14')
        print("Docker Containerized RRU process killed")
        return

    @wishful_module.bind_function(upis.net.RCC_container_activation)
    def RCC_container_activation(self):
        #os.system('sudo docker start RCC1')
        #print("Docker Container RCC Started")
        # os.system('sudo docker exec -d RCC1 ./openairinterface5g/targets/bin/lte-softmodem.Rel14 -O usr/local/etc/oai/rcc.band7.tm1.usrpb210.conf')
        # print("Docker Containerized RCC process started")
        p8 = subprocess.Popen(['sudo docker exec -d RCC1 ./openairinterface5g/targets/bin/lte-softmodem.Rel14 -O usr/local/etc/oai/rcc.band7.tm1.usrpb210.conf'], stdout=subprocess.PIPE, shell=True)
        output8 = p8.communicate()[0]
        return

    @wishful_module.bind_function(upis.net.RCC_container_deactivation)
    def RCC_container_deactivation(self):
        #os.system('sudo docker stop RCC1')
        #print("Docker Container RRU Stopped")
        os.system('sudo docker exec -d RCC1 pkill -u root -f lte-softmodem.Rel14')
        print("Docker Containerized RRU process killed")
        return

    # @wishful_module.bind_function(upis.net.UE_activation)
    # def UE_activation(self, central_freq, N_RB, tx_gain, rx_gain):
    #   #cmd_1 = 'sudo -E /root/openairinterface5g/targets/bin/lte-softmodem.Rel14 -U --ue-scan-carrier -C %sL -r %s --ue-txgain %s --ue-rxgain %s' %(central_freq, N_RB, tx_gain, rx_gain)
    #   #cmd_1 = 'sudo sh -c "cd /root/openairinterface5g/targets/bin/; sudo -E ./lte-softmodem.Rel14 -U --ue-scan-carrier -C %sL -r %s --ue-txgain %s --ue-rxgain %s"' %(central_freq, N_RB, tx_gain, rx_gain)
    #   os.system('sudo sh -c "cd /root/openairinterface5g/cmake_targets/tools/; sudo ./init_nas_s1 UE"')
    #   #os.system('sudo sh -c "cd /root/openairinterface5g/targets/bin/; sudo -E ./lte-softmodem.Rel14 -U --ue-scan-carrier -C %s -r %s --ue-txgain %s --ue-rxgain %s"' %(central_freq, N_RB, tx_gain, rx_gain))
    #   #return

    @wishful_module.bind_function(upis.net.UE_interface_activation)
    def UE_interface_activation(self):
        os.system("cd /root/openairinterface5g/cmake_targets/tools/")
        p9 = subprocess.Popen(['sudo ./init_nas_s1 UE'], stdout=subprocess.PIPE, shell=True)
        output9 = p9.communicate()[0]
        return

    @wishful_module.bind_function(upis.net.UE_activation)
    def UE_activation(self, central_freq, N_RB, tx_gain, rx_gain):
        # cmd_1 = '''
        #         ./openairinterface5g/targets/bin/lte-softmodem.Rel14 -U --ue-scan-carrier -C 2660000000 -r 25 --ue-txgain 95 --ue-rxgain 110
        #         '''
        #os.system('sudo sh -c "cd /root/openairinterface5g/cmake_targets/tools/; sudo ./init_nas_s1 UE"')
        p10 = subprocess.Popen(['sudo -E /root/openairinterface5g/targets/bin/lte-softmodem.Rel14 -U --ue-scan-carrier -C %s -r %s --ue-txgain %s --ue-rxgain %s' %(central_freq, N_RB, tx_gain, rx_gain)], stdout=subprocess.PIPE, shell=True)
        output10 = p10.communicate()[0]
        return

    @wishful_module.bind_function(upis.net.UE_deactivation)
    def UE_deactivation(self):
        os.system('sudo pkill lte-softmodem')
        print("UE Deactivated")
        return

    @wishful_module.bind_function(upis.net.UE_attach)
    #UPI valid when a LTE dongle is used as UE. 
    def UE_attach(self, central_freq, N_RB, tx_gain, rx_gain):
        cmd_1 = 'cd /root/openairinterface5g/targets/bin/'
        os.system(cmd_1)
        cmd_2 = 'sudo -E ./lte-softmodem.Rel14 -U --ue-scan-carrier -C %sL -r %s --ue-txgain %s --ue-rxgain %s' %(central_freq, N_RB, tx_gain, rx_gain)
        os.system(cmd_2)
        return

    @wishful_module.bind_function(upis.net.UE_detach)
    #UPI valid when a LTE dongle is used as UE
    def UE_detach(self):
        os.system('sudo pkill lte-softmodem')
        return

    @wishful_module.bind_function(upis.net.check_UE_activation)
    def check_UE_activation(self):
        #ping_result = os.system('ping -c 1 172.16.0.1 > /dev/null ; echo $?')
        ping_result = check_output('ping -c 1 172.16.0.1 > /dev/null ; echo $?', shell=True)
        print('Ping results' ,ping_result)
        if ping_result == 0:
            UE_ping_status_flag = 0
            print("UE_ping_status_flag", UE_ping_status_flag)
            return 0
        else:
            print("UE mpt attached...Retrying....")
            UE_ping_status_flag = 1
            print("UE_ping_status_flag", UE_ping_status_flag)
            return 1

    #CHECK if the environmental variable is properly set
    def check_environment_variable(self):
        if "OAI_5G_PATH" in os.environ:
            return True
        print("Please set the environmental variable OPENAIR_5G_PATH with the path to the openairinterface root folder.")
        return False

    # SET FUNCTIONS of NET_UPI
    def set_generic(self, filename, key, value):
        # for setting the number of eNB served by the same MME.
        #track_name = filename
        conf_path_1 = filename
        conf_path_2 = filename + "_temp"
        try:
            f_1 = open(conf_path_1)
            f_2 = open(conf_path_2, 'w')
        except (Exception) as err:
            print("exception", err)
            print("Error: unable to open configuration file")
            return 1
        line = f_1.readline()

        ## If the file is not empty keep reading line one at a time till the file is empty
        check_find = False
        while line:
            finded = line.find(key)
            if finded != -1:
                check_find = True
                newline = key + " = " + str(value) + ";\n"
                splits = line.split('#', 1)
                if (len(splits) > 1):
                    newline += "#" + splits[1]
                f_2.write(newline)
            else:
                f_2.write(line)
            line = f_1.readline()
        f_1.close()
        f_2.close()

        os.rename(conf_path_2,conf_path_1)
        
        if check_find  == False:
            return 1
        return 0

    def set_not_implemented(self, value):
        print("The inserted parameter is not consider in OAI implementation")
        return

    # def set_mme_realm(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "REALM"
    #     return self.set_generic(MME_CONF_FILENAME, TO_FIND, value)

    def set_mme_mcc(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "MCC"
        return self.set_generic(MME_CONF_FILENAME, TO_FIND, value)

    def set_mme_mnc(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "MNC"
        return self.set_generic(MME_CONF_FILENAME, TO_FIND, value)

    # def set_mme_served_enb(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MAXENB"
    #     return self.set_generic(MME_CONF_FILENAME, TO_FIND, value)

    # def set_mme_served_ue(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MAXUE"
    #     return self.set_generic(MME_CONF_FILENAME, TO_FIND, value)

    # def set_mme_tai_list(self, mcc, mnc, tac):
    #     if not self.check_environment_variable():
    #         return
    #     # for setting the TAI list in the MME.
    #     conf_path_1 = my_path_epc + "/mme.conf"
    #     conf_path_2 = my_path_epc + "/mme_new.conf"
    #     try:
    #         f_1 = open(conf_path_1)
    #         f_2 = open(conf_path_2, 'w')
    #     except IOError:
    #         return 1
    #     line = f_1.readline()
    #     ## If the file is not empty keep reading line one at a time till the file is empty
    #     check_find = False
    #     while line:
    #         finded = line.find("    TAI_LIST")
    #         f_2.write(line)
    #         if finded != -1:
    #             check_find = True
    #             line1 = f_1.readline()
    #             while line1.find(");") == -1:
    #                 f_2.write(
    #                     "         {{MCC=\"{}\" ; MNC=\"{}\";  TAC = \"{}\"; }}                                   # YOUR TAI CONFIG HERE\n".format(
    #                         mcc, mnc, tac))
    #                 line1 = f_1.readline()
    #             f_2.write(line1)
    #         line = f_1.readline()
    #     f_1.close()
    #     f_2.close()
    #     remove(conf_path_1)
    #     move(conf_path_1, conf_path_2)
    #     if check_find  == False:
    #         return 1
    #     return 0

    # def set_mme_gummei_list(self, mcc, mnc, mme_gid, mme_code):
    #     if not self.check_environment_variable():
    #         return
    #     # for setting the GUMMEI list in the MME.
    #     conf_path_1 = my_path_epc + "/mme.conf"
    #     conf_path_2 = my_path_epc + "/mme_new.conf"
    #     try:
    #         f_1 = open(conf_path_1)
    #         f_2 = open(conf_path_2, 'w')
    #     except IOError:
    #         return 1
    #     ## Read the first line
    #     line = f_1.readline()
    #     ## If the file is not empty keep reading line one at a time till the file is empty
    #     check_find == False
    #     while line:
    #         f_2.write(line)
    #         finded = line.find("    GUMMEI_LIST = (")
    #         if finded != -1:
    #             check_find = True
    #             line1 = f_1.readline()
    #             while line1.find(");") == -1:
    #                 f_2.write(
    #                     "         {{MCC=\"{}\" ; MNC=\"{}\";  MME_GID = \"{}\"; MME_CODE = \"{}\"; }}                                   # YOUR TAI CONFIG HERE\n".format(
    #                         mcc, mnc, mme_gid, mme_code))
    #                 line1 = f_1.readline()
    #             f_2.write(line1)
    #         line = f_1.readline()
    #     f_1.close()
    #     f_2.close()
    #     remove(conf_path_1)
    #     move(conf_path_1, conf_path_2)
    #     if check_find  == False:
    #         return 1
    #     return 0

    def set_enb_name(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND_1 = "Active_eNBs"
        TO_FIND_2 = "eNB_name"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND_1, value + "_LTE_Box")
        ret_2 = self.set_generic(ENB_CONF_FILENAME, TO_FIND_2, value + "_LTE_Box")

        ret_3 = self.set_generic(RCC_CONF_FILENAME, TO_FIND_1, value + "_LTE_Box")
        ret_4 = self.set_generic(RCC_CONF_FILENAME, TO_FIND_2, value + "_LTE_Box")

        ret_5 = self.set_generic(RRU_CONF_FILENAME, TO_FIND_1, value + "_LTE_Box")
        ret_6 = self.set_generic(RRU_CONF_FILENAME, TO_FIND_2, value + "_LTE_Box")

    def set_enb_id(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "eNB_ID"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def set_enb_cell_type(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "cell_type"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def set_enb_tracking_area_code(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "tracking_area_code"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def set_enb_mcc(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "mobile_country_code"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)       

    def set_enb_mnc(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "mobile_network_code"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)        

    # def set_rru_name(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND_1 = "eNB_name"
    #     TO_FIND_2 = "Active_eNBs"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         ret_1 = self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND_1, value + "LTE_Box")
    #         if ret_1 != 0:
    #             return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND_2, value + "LTE_Box")
    #         return ret_1
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         ret_1 = self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND_1, value + "LTE_Box")
    #         if ret_1 != 0:
    #             return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND_2, value + "LTE_Box")
    #         return ret_1

    # def set_rru_id(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "eNB_ID"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)

    # def set_rru_cell_type(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "cell_type"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)

    # def set_rru_tracking_area_code(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "tracking_area_code"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)

    # def set_rru_mcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "mobile_country_code"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)

    # def set_rru_mnc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "mobile_network_code"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)

    # def set_rcc_name(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND_1 = "eNB_name"
    #     TO_FIND_2 = "Active_eNBs"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         ret_1 = self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND_1, value + "LTE_Box")
    #         if ret_1 != 0:
    #             return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND_2, value + "LTE_Box")
    #         return ret_1
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         ret_1 = self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND_1, value + "LTE_Box")
    #         if ret_1 != 0:
    #             return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND_2, value + "LTE_Box")
    #         return ret_1

    # def set_rcc_id(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "eNB_ID"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value + "LTE_Box")
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value + "LTE_Box")

    # def set_rcc_cell_type(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "cell_type"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)

    # def set_rcc_tracking_area_code(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "tracking_area_code"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_rcc_mcc(value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "mobile_country_code"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_rcc_mnc(value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "mobile_network_code"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_fronthaul_transport_mode(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "tr_preference"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_mme_name_s1(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MME_INTERFACE_NAME_FOR_S1_MME"
    #     return self.set_generic(MME_CONF_FILENAME, TO_FIND, value)

    # def set_mme_addr_s1(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MME_IPV4_ADDRESS_FOR_S1_MME"
    #     return self.set_generic(MME_CONF_FILENAME, TO_FIND, value)

    # def set_mme_name_s11(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MME_INTERFACE_NAME_FOR_S11_MME"
    #     return self.set_generic(MME_CONF_FILENAME, TO_FIND, value)

    # def set_mme_addr_s11(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = " MME_IPV4_ADDRESS_FOR_S11_MME"
    #     return self.set_generic(MME_CONF_FILENAME, TO_FIND, value)

    # def set_mme_port_s11(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MME_PORT_FOR_S11_MME"
    #     return self.set_generic(MME_CONF_FILENAME, TO_FIND, value)

    # def set_sgw_name_s11(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "SGW_INTERFACE_NAME_FOR_S11"
    #     return self.set_generic(SPGW_CONF_FILENAME, TO_FIND, value)

    # def set_sgw_addr_s11(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = " SGW_IPV4_ADDRESS_FOR_S11"
    #     return self.set_generic(MME_CONF_FILENAME, TO_FIND, value)

    # def set_sgw_name_s1u_s12_s4(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "SGW_INTERFACE_NAME_FOR_S1U_S12_S4_UP"
    #     return self.set_generic(SPGW_CONF_FILENAME, TO_FIND, value)

    def set_sgw_addr_s1u_s12_s4(value):
        if not self.check_environment_variable():
            return
        TO_FIND = "SGW_IPV4_ADDRESS_FOR_S1U_S12_S4_UP"
        return self.set_generic(SPGW_CONF_FILENAME, TO_FIND, value)

    # def set_sgw_port_s1u_s12_s4(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "SGW_IPV4_PORT_FOR_S1U_S12_S4_UP"
    #     return self.set_generic(SPGW_CONF_FILENAME, TO_FIND, value)

    # def set_sgw_name_s5_s8(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "SGW_INTERFACE_NAME_FOR_S5_S8_UP"
    #     return self.set_generic(SPGW_CONF_FILENAME, TO_FIND, value)

    # def set_sgw_addr_s5_s8(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "SGW_IPV4_ADDRESS_FOR_S5_S8_UP"
    #     return self.set_generic(SPGW_CONF_FILENAME, TO_FIND, value)

    # def set_pgw_name_s5_s8(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "PGW_INTERFACE_NAME_FOR_S5_S8"
    #     return self.set_generic(SPGW_CONF_FILENAME, TO_FIND, value)

    def set_pgw_name_sgi(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "PGW_INTERFACE_NAME_FOR_SGI"
        return self.set_generic(SPGW_CONF_FILENAME, TO_FIND, value)

    # def set_ue_ip_addr_pool(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "IPV4_LIST"
    #     return self.set_generic(SPGW_CONF_FILENAME, TO_FIND, value)

    def set_default_dns_addr(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "DEFAULT_DNS_IPV4_ADDRESS"
        return self.set_generic(SPGW_CONF_FILENAME, TO_FIND, value)

    def set_enb_mme_ip_addr(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "mme_ip_address"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)

    # def set_enb_name_s1(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_INTERFACE_NAME_FOR_S1_MME"
    #     return self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)

    # def set_enb_addr_s1(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_IPV4_ADDRESS_FOR_S1_MME"
    #     return self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)

    # def set_enb_name_s1u(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_INTERFACE_NAME_FOR_S1U"
    #     return self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)

    def set_enb_addr_s1u(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "ENB_IPV4_ADDRESS_FOR_S1U"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)       

    # def set_enb_port_s1u(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_PORT_FOR_S1U"
    #     return self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)

    # def set_rcc_mme_ip_addr(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "mme_ip_address"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_rcc_name_s1(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_INTERFACE_NAME_FOR_S1_MME"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_rcc_addr_s1(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_IPV4_ADDRESS_FOR_S1_MME"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_rcc_name_s1u(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_INTERFACE_NAME_FOR_S1U"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_rcc_addr_s1u(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_IPV4_ADDRESS_FOR_S1U"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_rcc_port_s1u(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_PORT_FOR_S1U"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    def set_rcc_local_if_name(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_if_name"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
        return

    def set_rcc_local_addr(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_address"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
        return

    def set_rcc_local_port(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_port"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
        return

    def set_rcc_remote_addr(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "remote_address"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
        return

    def set_rcc_remote_port(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "remote_port"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
        return

    def set_rru_local_if_name(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_if_name"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
        return

    def set_rru_local_addr(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_address"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
        return

    def set_rru_local_port(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_port"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
        return

    def set_rru_remote_addr(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "remote_address"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
        return

    def set_rru_remote_port(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "remote_port"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
        return

    # SET FUNCTIONS OF RADIO UPI

    # def set_pucch_enb(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pucch_p0_Nominal"
    #     return self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)

    # def set_pusch_enb(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pusch_p0_Nominal"
    #     return self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)

    def set_rx_gain_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "rx_gain"
        ret_1 =  self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 =  self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 =  self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def set_tx_gain_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "tx_gain"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def set_tx_bandwidth_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "N_RB_DL"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def set_tx_channel_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "downlink_frequency"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def set_tx_mode_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "frame_type"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)        

    def set_ul_freq_offset_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "uplink_frequency_offset"
        ret_1 = self.set_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.set_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.set_generic(RRU_CONF_FILENAME, TO_FIND, value)

    # def set_pucch_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pucch_p0_Nominal"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_pusch_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pusch_p0_Nominal"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_rx_gain_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "rx_gain"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_tx_gain_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "tx_gain"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_tx_bandwidth_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "N_RB_DL"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_tx_channel_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "downlink_frequency"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_tx_mode_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "frame_type"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_ul_freq_offset_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "uplink_frequency_offset"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_pucch_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pucch_p0_Nominal"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_pusch_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pusch_p0_Nominal"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_rx_gain_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "rx_gain"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_tx_gain_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "tx_gain"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_tx_bandwidth_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "N_RB_DL"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_tx_channel_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "downlink_frequency"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_tx_mode_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "frame_type"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def set_ul_freq_offset_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "uplink_frequency_offset"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.set_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.set_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # GET FUNCTIONS OF NET UPI
    def get_generic(self, filename, key):
        # for setting the number of eNB served by the same MME.
        conf_path_1 = filename
        try:
            f_1 = open(conf_path_1)
        except (Exception) as err:
            print("exception", err)
            print("Error: unable to open configuration file")
            return 1
        line = f_1.readline()
        ## If the file is not empty keep reading line one at a time till the file is empty
        while line:
            finded = line.find(key)
            if finded != -1:
                splits = line.split('=', 1)
                if (len(splits) > 1):
                    splits_2 = splits[1].split(';', 1)
                    value = splits_2[0].replace(" ", "")
                    f_1.close()
                    return value
        f_1.close()
        return

    def get_not_implemented(self, value):
        print("The inserted parameter is not consider in OAI implementation")
        return

    def get_mme_mcc(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "MCC"
        return self.get_generic(MME_CONF_FILENAME, TO_FIND)

    def get_mme_mnc(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "MNC"
        return self.get_generic(MME_CONF_FILENAME, TO_FIND)

    # def get_mme_realm(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "REALM"
    #     return self.get_generic(MME_CONF_FILENAME, TO_FIND)

    # def get_mme_served_enb(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MAXENB"
    #     return self.get_generic(MME_CONF_FILENAME, TO_FIND)

    # def get_mme_served_ue(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MAXUE"
    #     return self.get_generic(MME_CONF_FILENAME, TO_FIND)

    # def get_mme_tai_list(self):
    #     if not self.check_environment_variable():
    #         return
    #     # for getting the TAI list in the MME.
    #     conf_path_1 = my_path_epc + "/mme.conf"
    #     conf_path_2 = my_path_epc + "/mme_new.conf"
    #     f_1 = open(conf_path_1)
    #     f_2 = open(conf_path_2, 'w')
    #     line = f_1.readline()
    #     ## If the file is not empty keep reading line one at a time till the file is empty
    #     while line:
    #         finded = line.find("    TAI_LIST")
    #         f_2.write(line)
    #         if finded != -1:
    #             line1 = f_1.readline()
    #             while line1.find(");") == -1:
    #                 f_2.write(
    #                     "         {{MCC=\"{}\" ; MNC=\"{}\";  TAC = \"{}\"; }}                                   # YOUR TAI CONFIG HERE\n".format(
    #                         mcc, mnc, tac))
    #                 line1 = f_1.readline()
    #             f_2.write(line1)
    #         line = f_1.readline()
    #     f_1.close()
    #     f_2.close()
    #     remove(conf_path_1)
    #     move(conf_path_1, conf_path_2)
    #     return

    # def get_mme_gummei_list(self):
    #     if not self.check_environment_variable():
    #         return
    #     # for getting the GUMMEI list in the MME.
    #     conf_path_1 = my_path_epc + "/mme.conf"
    #     conf_path_2 = my_path_epc + "/mme_new.conf"
    #     f_1 = open(conf_path_1)
    #     f_2 = open(conf_path_2, 'w')
    #     ## Read the first line
    #     line = f_1.readline()
    #     ## If the file is not empty keep reading line one at a time till the file is empty
    #     while line:
    #         f_2.write(line)
    #         finded = line.find("    GUMMEI_LIST = (")
    #         if finded != -1:
    #             line1 = f_1.readline()
    #             while line1.find(");") == -1:
    #                 f_2.write(
    #                     "         {{MCC=\"{}\" ; MNC=\"{}\";  MME_GID = \"{}\"; MME_CODE = \"{}\"; }}                                   # YOUR TAI CONFIG HERE\n".format(
    #                         mcc, mnc, mme_gid, mme_code))
    #                 line1 = f_1.readline()
    #             f_2.write(line1)
    #         line = f_1.readline()
    #     f_1.close()
    #     f_2.close()
    #     remove(conf_path_1)
    #     move(conf_path_1, conf_path_2)
    #     return

    def get_enb_name(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "eNB_name"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND_1)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND_1)
        ret_1 = self.get_generic(RRU_CONF_FILENAME, TO_FIND_1)

    def get_enb_id(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "eNB_ID"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND)

    def get_enb_cell_type(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "cell_type"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND)

    def get_enb_tracking_area_code(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "tracking_area_code"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND)

    def get_enb_mcc(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "mobile_country_code"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND)

    def get_enb_mnc(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "mobile_network_code"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND)

    # def get_rru_name(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "eNB_name"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_rru_id(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "eNB_ID"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_rru_cell_type(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "cell_type"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_rru_tracking_area_code(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "tracking_area_code"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_rru_mcc(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "mobile_country_code"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_rru_mnc(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "mobile_network_code"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
    #     return

    def get_rcc_name(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "eNB_name"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rcc_id(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "eNB_ID"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rcc_cell_type(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "cell_type"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rcc_tracking_area_code(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "tracking_area_code"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
        return

    # def get_rcc_mcc(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "mobile_country_code"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_rcc_mnc(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "mobile_network_code"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_fronthaul_transport_mode(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "tr_preference"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_mme_name_s1(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MME_INTERFACE_NAME_FOR_S1_MME"
    #     return self.get_generic(MME_CONF_FILENAME, TO_FIND)

    # def get_mme_addr_s1(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MME_IPV4_ADDRESS_FOR_S1_MME"
    #     return self.get_generic(MME_CONF_FILENAME, TO_FIND)

    # def get_mme_name_s11(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MME_INTERFACE_NAME_FOR_S11_MME"
    #     return self.get_generic(MME_CONF_FILENAME, TO_FIND)

    # def get_mme_addr_s11(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = " MME_IPV4_ADDRESS_FOR_S11_MME"
    #     return self.get_generic(MME_CONF_FILENAME, TO_FIND)

    # def get_mme_port_s11(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "MME_PORT_FOR_S11_MME"
    #     return self.get_generic(MME_CONF_FILENAME, TO_FIND)

    # def get_sgw_name_s11(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "SGW_INTERFACE_NAME_FOR_S11"
    #     return self.get_generic(SPGW_CONF_FILENAME, TO_FIND)

    # def get_sgw_addr_s11(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = " SGW_IPV4_ADDRESS_FOR_S11"
    #     return self.get_generic(MME_CONF_FILENAME, TO_FIND)

    # def get_sgw_name_s1u_s12_s4(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "SGW_INTERFACE_NAME_FOR_S1U_S12_S4_UP"
    #     return self.get_generic(SPGW_CONF_FILENAME, TO_FIND)

    # def get_sgw_addr_s1u_s12_s4(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "SGW_IPV4_ADDRESS_FOR_S1U_S12_S4_UP"
    #     return self.get_generic(SPGW_CONF_FILENAME, TO_FIND)

    # def get_sgw_port_s1u_s12_s4(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "SGW_IPV4_PORT_FOR_S1U_S12_S4_UP"
    #     return self.get_generic(SPGW_CONF_FILENAME, TO_FIND)

    # def get_sgw_name_s5_s8(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "SGW_INTERFACE_NAME_FOR_S5_S8_UP"
    #     return self.get_generic(SPGW_CONF_FILENAME, TO_FIND)

    # def get_sgw_addr_s5_s8(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "SGW_IPV4_ADDRESS_FOR_S5_S8_UP"
    #     return self.get_generic(SPGW_CONF_FILENAME, TO_FIND)

    # def get_pgw_name_s5_s8(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "PGW_INTERFACE_NAME_FOR_S5_S8"
    #     return self.get_generic(SPGW_CONF_FILENAME, TO_FIND)

    def get_pgw_name_sgi(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "PGW_INTERFACE_NAME_FOR_SGI"
        return self.get_generic(SPGW_CONF_FILENAME, TO_FIND)

    # def get_ue_ip_addr_pool(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "IPV4_LIST"
    #     return self.get_generic(SPGW_CONF_FILENAME, TO_FIND)

    def get_default_dns_addr(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "DEFAULT_DNS_IPV4_ADDRESS"
        return self.get_generic(SPGW_CONF_FILENAME, TO_FIND)

    def get_enb_mme_ip_addr(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "mme_ip_address"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND)

    # def get_enb_name_s1(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_INTERFACE_NAME_FOR_S1_MME"
    #     return self.get_generic(ENB_CONF_FILENAME, TO_FIND)

    # def get_enb_addr_s1(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_IPV4_ADDRESS_FOR_S1_MME"
    #     return self.get_generic(ENB_CONF_FILENAME, TO_FIND)

    # def get_enb_name_s1u(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_INTERFACE_NAME_FOR_S1U"
    #     return self.get_generic(ENB_CONF_FILENAME, TO_FIND)

    def get_enb_addr_s1u(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "ENB_IPV4_ADDRESS_FOR_S1U"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND)

    # def get_enb_port_s1u(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_PORT_FOR_S1U"
    #     return self.get_generic(ENB_CONF_FILENAME, TO_FIND)

    def get_rru_local_if_name(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_if_name"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rru_local_addr(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_address"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rru_local_if_name(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_if_name"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rru_local_port(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_port"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rru_remote_addr(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "remote_address"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rru_remote_port(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "remote_port"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rcc_mme_ip_addr(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "mme_ip_address"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
        return

    # def get_rcc_name_s1(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_INTERFACE_NAME_FOR_S1_MME"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_rcc_addr_s1(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_IPV4_ADDRESS_FOR_S1_MME"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_rcc_name_s1u(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_INTERFACE_NAME_FOR_S1U"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_rcc_addr_s1u(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_IPV4_ADDRESS_FOR_S1U"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
    #     return

    # def get_rcc_port_s1u(self):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "ENB_PORT_FOR_S1U"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
    #     elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
    #     return

    def get_rcc_local_if_name(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_if_name"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rcc_local_addr(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_address"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rcc_local_if_name(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_if_name"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rcc_local_port(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "local_port"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rcc_remote_addr(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "remote_address"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
        return

    def get_rcc_remote_port(self):
        if not self.check_environment_variable():
            return
        TO_FIND = "remote_port"
        if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
            return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND)
        elif Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FIVE:
            return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND)
        return

    #GET FUNCTIONS OF RADIO_UPI
    # def get_pucch_enb(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pucch_p0_Nominal"
    #     return self.get_generic(ENB_CONF_FILENAME, TO_FIND, value)

    # def get_pusch_enb(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pusch_p0_Nominal"
    #     return self.get_generic(ENB_CONF_FILENAME, TO_FIND, value)

    def get_rx_gain_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "rx_gain"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def get_tx_gain_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "tx_gain"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def get_tx_bandwidth_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "N_RB_DL"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def get_tx_channel_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "downlink_frequency"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def get_tx_mode_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "frame_type"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND, value)

    def get_ul_freq_offset_enb(self, value):
        if not self.check_environment_variable():
            return
        TO_FIND = "uplink_frequency_offget"
        ret_1 = self.get_generic(ENB_CONF_FILENAME, TO_FIND, value)
        ret_2 = self.get_generic(RCC_CONF_FILENAME, TO_FIND, value)
        ret_3 = self.get_generic(RRU_CONF_FILENAME, TO_FIND, value)

    # def get_pucch_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pucch_p0_Nominal"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_pusch_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pusch_p0_Nominal"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_rx_gain_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "rx_gain"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_tx_gain_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "tx_gain"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_tx_bandwidth_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "N_RB_DL"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_tx_channel_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "downlink_frequency"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_tx_mode_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "frame_type"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_ul_freq_offset_rcc(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "uplink_frequency_offget"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RCC_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RCC_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_pucch_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pucch_p0_Nominal"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_pusch_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "pusch_p0_Nominal"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_rx_gain_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "rx_gain"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_tx_gain_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "tx_gain"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_tx_bandwidth_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "N_RB_DL"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_tx_channel_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "downlink_frequency"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_tx_mode_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "frame_type"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return

    # def get_ul_freq_offset_rru(self, value):
    #     if not self.check_environment_variable():
    #         return
    #     TO_FIND = "uplink_frequency_offset"
    #     if Functional_split.get_split_level() == Functional_split.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE:
    #         return self.get_generic(RRU_IF4p5_CONF_FILENAME, TO_FIND, value)
    #     elif current_functional_split == FUNCTIONAL_SLPIT_TYPES.FIVE:
    #         return self.get_generic(RRU_IF5_CONF_FILENAME, TO_FIND, value)
    #     return