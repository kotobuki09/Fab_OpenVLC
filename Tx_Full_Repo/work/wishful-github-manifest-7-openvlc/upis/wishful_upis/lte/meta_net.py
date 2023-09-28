"""The WiSHFUL net control interface, attributes.
Used for configuration/monitoring of the network
layers of the LTE technology
"""
__author__ = "Francesco Giannone, Domenico Garlisi"
__copyright__ = "Copyright (c) 2017, Sant'Anna, CNIT"
__version__ = "0.1.0"
__email__ = "{francesco.giannone@santannapisa.it, domenico.garlisi@cnit.it}"

from ..meta_models import ValueDoc, Attribute, Measurement, Event, Action

# ATTRIBUTES


#********
#EPC Attribute
#********
LTE_EPC_MCC = Attribute(key='LTE_EPC_MCC', type=int, isReadOnly=False)  #: MME Mobile Country Code
LTE_EPC_MNC = Attribute(key='LTE_EPC_MNC', type=int, isReadOnly=False)  #: MME Mobile Network Code
LTE_EPC_OP = Attribute(key='LTE_EPC_OP', type=int, isReadOnly=False)  #: Configures global configuration parameters Global OP
LTE_EPC_AMF = Attribute(key='LTE_EPC_AMF', type=int, isReadOnly=False)  #: Configures global configuration parameters Global AMF
LTE_EPC_ENB_ADD = Attribute(key='LTE_EPC_ENB_ADD', type=int, isReadOnly=False)  #: adds a eNB to be served by the EPC (required: IP address)
LTE_EPC_ENB_DEL = Attribute(key='LTE_EPC_ENB_DEL', type=int, isReadOnly=False)  #: deletes an eNB
LTE_EPC_ENB_LIST = Attribute(key='LTE_EPC_ENB_LIST', type=int, isReadOnly=False)  #: get eNB list
LTE_EPC_SUBSCRIBER_ADD = Attribute(key='LTE_EPC_SUBSCRIBER_ADD', type=int, isReadOnly=False)  #: Add a single UE (required input: IMSI, Subscriber Group)
LTE_EPC_SUBSCRIBER_DEL = Attribute(key='LTE_EPC_SUBSCRIBER_DEL', type=int, isReadOnly=False)  #: deletes connection data for a single subscriber
LTE_EPC_SUBSCRIBER_LIST = Attribute(key='LTE_EPC_SUBSCRIBER_LIST', type=int, isReadOnly=False)  #: get UE list
LTE_EPC_SUBSCRIBER_GROUP_ADD = Attribute(key='LTE_EPC_SUBSCRIBER_GROUP_ADD', type=int, isReadOnly=False)  #: Adds a new subscriber profile (required input: Name, APN, , UL/DL AMBR)
LTE_EPC_SUBSCRIBER_GROUP_DEL = Attribute(key='LTE_EPC_SUBSCRIBER_GROUP_DEL', type=int, isReadOnly=False)  #: deletes a subscriber profile
LTE_EPC_SUBSCRIBER_GROUP_LIST = Attribute(key='LTE_EPC_SUBSCRIBER_GROUP_LIST', type=int, isReadOnly=False)  #: get subscriber profile list
LTE_EPC_APN_ADD = Attribute(key='LTE_EPC_APN_ADD', type=int, isReadOnly=False)  #: adds a new APN (required: Name, PGW address, DHCP pool, DNS server, UL/DL AMBR)
LTE_EPC_APN_DEL = Attribute(key='LTE_EPC_MNC', type=int, isReadOnly=False)  #: deletes an APN
LTE_EPC_APN_LIST = Attribute(key='LTE_EPC_APN_LIST', type=int, isReadOnly=False)  #: get APN list
LTE_EPC_RNTI = Attribute(key='LTE_EPC_RNTI', type=int, isReadOnly=False)  #:
LTE_EPC_HSS_ADDRESS = Attribute(key='LTE_EPC_HSS_ADDRESS', type=int, isReadOnly=False)  #: HSS address


# LTE_EPC_HSS_DIAMETER_ADDRESS = Attribute(key='LTE_EPC_HSS_DIAMETER_ADDRESS', type=str, isReadOnly=False)  #: sets the configuration of the HSS (diameter bind IP address)
# LTE_EPC_SGW_GTPU_IP_ADDRESS = Attribute(key='LTE_EPC_SGW_GTPU_IP_ADDRESS', type=str, isReadOnly=False)  #:sets the configuration params of the SGW (GTP-U and GTP-C bind addresses)
# LTE_EPC_SGW_GTPC_IP_ADDRESS = Attribute(key='LTE_EPC_SGW_GTPC_IP_ADDRESS', type=str, isReadOnly=False)  #:sets the configuration params of the SGW (GTP-U and GTP-C bind addresses)
# LTE_EPC_MME_NAME = Attribute(key='LTE_EPC_MME_NAME', type=str, isReadOnly=False)  #: sets the configuration of the MME "name"
# LTE_EPC_MME_CODE = Attribute(key='LTE_EPC_MME_CODE', type=int, isReadOnly=False)  #: sets the configuration of the MME "code"
# LTE_EPC_MME_GID = Attribute(key='LTE_EPC_MME_GID', type=int, isReadOnly=False)  #: sets the configuration of the MME "gid"
# LTE_EPC_MME_GUMMEI = Attribute(key='LTE_EPC_MME_GUMMEI', type=str, isReadOnly=False)  #: sets the configuration of the MME "GUMMEI"
# LTE_EPC_MME_MAX_ENB = Attribute(key='LTE_EPC_MME_MAX_ENB', type=int, isReadOnly=False)  #: number of eNB served by the same MME
# LTE_EPC_MME_MAX_UE = Attribute(key='LTE_EPC_MME_MAX_UE', type=int, isReadOnly=False)  #: number of UE served by the same MME
# LTE_EPC_MME_TAI_LIST = Attribute(key='LTE_EPC_MME_TAI_LIST', type=list, isReadOnly=False)  #: MME TAI list (TAI, MNC, MCC)
# LTE_EPC_MME_GUMMEI_LIST = Attribute(key='LTE_EPC_MME_GUMMEI_LIST', type=list, isReadOnly=False)  #: MME GUMMEI LIST (MCC,MNC,MME_GID, MME_CODE)
# LTE_EPC_MME_GTPC_ADDRESS = Attribute(key='LTE_EPC_MME_GTPC_ADDRESS', type=str, isReadOnly=False)  #: set the GTPC ADDRESS
# LTE_EPC_MME_S1AP_ADDRESS = Attribute(key='LTE_EPC_MME_S1AP_ADDRESS', type=str, isReadOnly=False)  #: set the S1AP ADDRESS
# LTE_EPC_MME_DIAMETER_ADDRESS = Attribute(key='LTE_EPC_MME_DIAMETER_ADDRESS', type=str, isReadOnly=False)  #: set the DIAMETER ADDRESS
# LTE_EPC_PGW_GTPU_IP_ADDRESS = Attribute(key='LTE_EPC_PGW_GTPU_IP_ADDRESS', type=str, isReadOnly=False)  #:sets the configuration params of the PGW (GTP-U bind addresses)
# LTE_EPC_PGW_GTPC_IP_ADDRESS = Attribute(key='LTE_EPC_PGW_GTPC_IP_ADDRESS', type=str, isReadOnly=False)  #:sets the configuration params of the PGW (GTP-C bind addresses)
# LTE_EPC_PGW_DL_AMBR = Attribute(key='LTE_EPC_PGW_DL_AMBR', type=int, isReadOnly=False)  #: sets the configuration params of the PGW (DL AMBR)
# LTE_EPC_PGW_UL_AMBR = Attribute(key='LTE_EPC_PGW_UL_AMBR', type=int, isReadOnly=False)  #: sets the configuration params of the PGW (UL AMBR)
# LTE_EPC_RESTART = Attribute(key='LTE_EPC_RESTART', type=bool, isReadOnly=False)  #: Restarts the system
# LTE_EPC_DETACH_UE = Attribute(key='LTE_EPC_DETACH_UE', type=str, isReadOnly=False)  #: Detaches a single UE (required input: IMSI)
# SPLIT_LEVEL = Attribute(key='SPLIT_LEVEL', type=int, isReadOnly=False)  #: point where the lte protocol stack is splitted
# FRONTHAUL_TRANSPORT_MODE = Attribute(key='FRONTHAUL_TRANSPORT_MODE', type=int, isReadOnly=False) #: Fronthaul link transport mode(UDP or RAW are the possible options)'''


# mme_S1_name = Attribute(key='mme_S1_name', type=int, isReadOnly=False)  #: S1 interface name of MME
# mme_S1_addr = Attribute(key='mme_S1_addr', type=int, isReadOnly=False)  #: S1 interface address of MME
# mme_S11_name = Attribute(key='mme_S11_name', type=int, isReadOnly=False)  #: S11 interface name of MME
# mme_S11_addr = Attribute(key='mme_S11_addr', type=int, isReadOnly=False)  #: S11 interface address of MME
# mme_S11_port = Attribute(key='mme_S11_port', type=int, isReadOnly=False)  #: S11 interface port of MME
# sgw_s11_name = Attribute(key='sgw_S1_name', type=int, isReadOnly=False)  #: S11 interface name of S-GW
# sgw_s11_addr = Attribute(key='sgw_S1_addr', type=int, isReadOnly=False)  #: S11 interface addr of S-GW
# sgw_S1U_S12_S4_name = Attribute(key='sgw_S1U_S12_S4_name', type=int, isReadOnly=False) #: S1-U,S12,S4 interface name of S-GW
# sgw_S1U_S12_S4_addr = Attribute(key='sgw_S1U_S12_S4_addr', type=int, isReadOnly=False) #: S1-U,S12,S4 interface addr of S-GW
# sgw_S1U_S12_S4_port = Attribute(key='sgw_S1U_S12_S4_port', type=int, isReadOnly=False) #: S1-U,S12,S4 interface port of S-GW
# sgw_S5_S8_name = Attribute(key='sgw_S5_S8_name', type=int, isReadOnly=False)  #: S5, S8 interface name of S-GW
# sgw_S5_S8_addr = Attribute(key='sgw_S5_S8_addr', type=int, isReadOnly=False)  #: S5, S8 interface addr of S-GW
# pgw_S5_S8_name = Attribute(key='pgw_S5_S8_name_PGW', type=int, isReadOnly=False)  #: S5, S8 interface name of P-GW
# pgw_SGi_name = Attribute(key='pgw_SGi_name', type=int, isReadOnly=False)  #: SGi interface name of P-GW
# enb_name_s1 = Attribute(key='enb_name_s1', type=int, isReadOnly=False)  #: S1-C interface name of the eNB
# enb_addr_s1 = Attribute(key='enb_addr_s1', type=int, isReadOnly=False)  #: S1-C interface address of the eNB
# enb_name_s1u = Attribute(key='enb_name_s1u', type=int, isReadOnly=False)  #: S1-U interface name of the eNB
# enb_port_s1u = Attribute(key='enb_port_s1u', type=int, isReadOnly=False)  #: S1-U interface port of the eNB
# rcc_name_s1 = Attribute(key='rcc_name_s1', type=int, isReadOnly=False)  #:S1-C interface name of the RCC
# rcc_addr_s1 = Attribute(key='rcc_addr_s1', type=int, isReadOnly=False)  #:S1-C interface address of the RCC
# rcc_name_s1u = Attribute(key='rcc_name_s1u', type=int, isReadOnly=False)  #: S1-U interface name of the RCC
# rcc_port_s1u = Attribute(key='rcc_port_s1u', type=int, isReadOnly=False)  #: S1-U interface port of the RCC


#********
#ENB Attribute
#********

LTE_ENB_NM = Attribute(key='LTE_ENB_NM', type=int, isReadOnly=False)  #: eNB name
LTE_ENB_ID = Attribute(key='LTE_ENB_ID', type=int, isReadOnly=False)  #: eNB identifier 
LTE_ENB_CT = Attribute(key='LTE_ENB_CT', type=int, isReadOnly=False)  #: eNB cell type (macro, pico, femto)
LTE_ENB_PLMN = Attribute(key='LTE_ENB_PLMN', type=int, isReadOnly=False)  #: eNB PLMN Code
LTE_ENB_TAC = Attribute(key='LTE_ENB_TAC', type=int, isReadOnly=False)  #: eNB Tracking Area Code
LTE_ENB_MME = Attribute(key='LTE_ENB_MME', type=int, isReadOnly=False)  #: MME address in the eNB config file
LTE_ENB_PGW = Attribute(key='LTE_ENB_PGW', type=int, isReadOnly=False)  #: PGW address in the eNB config file
LTE_ENB_SGW = Attribute(key='LTE_ENB_SGW', type=int, isReadOnly=False)  #: SGW address in the eNB config file
LTE_ENB_PHY_CELL_ID = Attribute(key='LTE_ENB_PHY_CELL_ID', type=int, isReadOnly=False) #: Cell identity
LTE_ENB_MCC = Attribute(key='LTE_ENB_MCC', type=int, isReadOnly=False)  #: eNB Mobile Country Code
LTE_ENB_MNC = Attribute(key='LTE_ENB_MNC', type=int, isReadOnly=False)  #: eNB Mobile Network Code

# LTE_ENB_LOCAL_SCTP_PORT = Attribute(key='LTE_ENB_LOCAL_SCTP_PORT', type=int, isReadOnly=False)  #: SCTP port on the eNB to listen to S1 messages
# LTE_ENB_EPC_SCTP_PORT = Attribute(key='LTE_ENB_EPC_SCTP_PORT', type=int, isReadOnly=False)  #: SCTP port for the remote EPC
# LTE_ENB_MAX_ERAB = Attribute(key='LTE_ENB_MAX_ERAB', type=int, isReadOnly=False)  #: maximum RAB per UE
# LTE_ENB_PUSCH_POWER_CONTROL_STATE = Attribute(key='LTE_ENB_PUSCH_POWER_CONTROL_STATE', type=bool, isReadOnly=False)  #: Enable/disable PUSCH Power control
# LTE_ENB_PDCCH_POWER_CONTROL_STATE = Attribute(key='LTE_ENB_PDCCH_POWER_CONTROL_STATE', type=bool, isReadOnly=False)  #: Enable/disable PDCCH power control
# LTE_ENB_SINR_PUCCH_POWER_CONTROL_STATE = Attribute(key='LTE_ENB_SINR_PUCCH_POWER_CONTROL_STATE', type=bool, isReadOnly=False)  #: enable/disable SINR based power control for PUCCH
# LTE_ENB_HARQ_PUCCH_POWER_CONTROL_STATE = Attribute(key='LTE_ENB_HARQ_PUCCH_POWER_CONTROL_STATE', type=bool, isReadOnly=False)  #: enable/disable HARQ based power control for PUCCH
# LTE_ENB_FREQUENCY_PUSCH_POWER_CONTROL_STATE = Attribute(key='LTE_ENB_FREQUENCY_PUSCH_POWER_CONTROL_STATE', type=bool, isReadOnly=False)  #: enable/disable frequency based PUSCH power control
# LTE_ENB_PUCCH_TARGET_SINR = Attribute(key='LTE_ENB_PUCCH_TARGET_SINR', type=int, isReadOnly=False)  #: Set the SINR target for PUCCH power control
# LTE_ENB_PUCCH_TARGET_BLER = Attribute(key='LTE_ENB_PUCCH_TARGET_BLER', type=int, isReadOnly=False)  #: set the BLER target for PUCCH power control
# LTE_ENB_PDCH_POWER_OFFSET = Attribute(key='LTE_ENB_PDCH_POWER_OFFSET', type=int, isReadOnly=False)  #: PDSCH power offset
# LTE_ENB_PSCH_POWER_OFFSET = Attribute(key='LTE_ENB_PSCH_POWER_OFFSET', type=int, isReadOnly=False)  #: PSCH power offset
# LTE_ENB_SSCH_POWER_OFFSET = Attribute(key='LTE_ENB_SSCH_POWER_OFFSET', type=int, isReadOnly=False)  #: SSCH power offset
# LTE_ENB_RACH_PREAMBLES = Attribute(key='LTE_ENB_RACH_PREAMBLES', type=int, isReadOnly=False)  #: Number of RA preambles
# LTE_ENB_MCS_DL = Attribute(key='LTE_ENB_MCS_DL', type=int, isReadOnly=False)  #: MCS profile to be used for DL
# LTE_ENB_MCS_UL = Attribute(key='LTE_ENB_MCS_UL', type=int, isReadOnly=False)  #: MCS profile to be used for UL
# LTE_ENB_RADIO_STATE = Attribute(key='LTE_ENB_RADIO_STATE', type=bool, isReadOnly=False)  #: Set radio on/off
# LTE_ENB_CQI_REPORT_STATE = Attribute(key='LTE_ENB_CQI_REPORT_STATE', type=bool, isReadOnly=False)  #: Enable/disable CQI reporting
# LTE_ENB_UE_REPORT_STATE = Attribute(key='LTE_ENB_UE_REPORT_STATE', type=bool, isReadOnly=False)  #: Enable/Disable UE reporting
# LTE_ENB_UE_INACTIVITY_TIMER = Attribute(key='LTE_ENB_UE_INACTIVITY_TIMER', type=int, isReadOnly=False)  #: UE inactivity timer
# LTE_ENB_CIPHER_ALGORITHM_LIST = Attribute(key='LTE_ENB_CIPHER_ALGORITHM_LIST', type=list, isReadOnly=False)  #: List for the desired Ciphering algorithms

# LTE_RCC_NM = Attribute(key='RRC_LTE_RCC_NM', type=int, isReadOnly=False)  #: RCC name
# LTE_RCC_ID = Attribute(key='LTE_RCC_ID', type=int, isReadOnly=False)  #: RCC identifier
# LTE_RCC_CT = Attribute(key='LTE_RCC_CT', type=int, isReadOnly=False)  #: RCC cell type (macro, pico, femto)
# LTE_RCC_PLMN = Attribute(key='LTE_RCC_PLMN', type=int, isReadOnly=False)  #: RCC PLMN Code
# LTE_RCC_TAC = Attribute(key='LTE_RCC_TAC', type=int, isReadOnly=False)  #: RRU Tracking Area Code
# LTE_RCC_MME = Attribute(key='LTE_RCC_MME', type=int, isReadOnly=False)  #: MME address in the eNB config file
# LTE_RCC_PGW = Attribute(key='LTE_RCC_PGW', type=int, isReadOnly=False)  #: PGW address in the eNB config file
# LTE_RCC_SGW = Attribute(key='LTE_RCC_SGW', type=int, isReadOnly=False)  #: SGW address in the eNB config file
LTE_RCC_FRONTHAUL_IF_NAME_LOCAL = Attribute(key='LTE_RCC_FRONTHAUL_IF_NAME_LOCAL', type=int, isReadOnly=False)  #: Interface of the local fronthaul
LTE_RCC_FRONTHAUL_IP_ADDRESS_LOCAL = Attribute(key='LTE_RCC_FRONTHAUL_IP_ADDRESS_LOCAL', type=int, isReadOnly=False)  #: IP of the local fronthaul
LTE_RCC_FRONTHAUL_PORT_LOCAL = Attribute(key='LTE_RCC_FRONTHAUL_PORT_LOCAL', type=int, isReadOnly=False)  #: port of the local fronthaul
LTE_RCC_FRONTHAUL_IP_ADDRESS_REMOTE = Attribute(key='LTE_RCC_FRONTHAUL_IP_ADDRESS_REMOTE', type=int, isReadOnly=False)  #: IP of the remote fronthaul
LTE_RCC_FRONTHAUL_PORT_REMOTE = Attribute(key='LTE_RCC_FRONTHAUL_PORT_REMOTE', type=int, isReadOnly=False)  #: port of the remote fronthaul
# LTE_RCC_MCC = Attribute(key='LTE_RCC_MCC', type=int, isReadOnly=False)  #: RCC Mobile Country Code
# LTE_RCC_MNC = Attribute(key='LTE_RCC_MNC', type=int, isReadOnly=False)  #: RCC Mobile Network Code

# LTE_RRU_NM = Attribute(key='LTE_RRU_NM', type=int, isReadOnly=False)  #: RRU name
# LTE_RRU_ID = Attribute(key='LTE_RRU_ID', type=int, isReadOnly=False)  #: RRU identifier
# LTE_RRU_CT = Attribute(key='LTE_RRU_CT', type=int, isReadOnly=False)  #: RRU cell type (macro, pico, femto)
# LTE_RRU_PLMN = Attribute(key='LTE_RRU_PLMN', type=int, isReadOnly=False)  #: RRU PLMN Code
# LTE_RRU_TAC = Attribute(key='LTE_RRU_TAC', type=int, isReadOnly=False) #: RRU Tracking Area Code
LTE_RRU_FRONTHAUL_IF_NAME_LOCAL = Attribute(key='LTE_RRU_FRONTHAUL_IF_NAME_LOCAL', type=int, isReadOnly=False)  #: Interface of the local fronthaul
LTE_RRU_FRONTHAUL_IP_ADDRESS_LOCAL = Attribute(key='LTE_RRU_FRONTHAUL_IP_ADDRESS_LOCAL', type=int, isReadOnly=False)  #: IP of the local fronthaul
LTE_RRU_FRONTHAUL_PORT_LOCAL = Attribute(key='LTE_RRU_FRONTHAUL_PORT_LOCAL', type=int, isReadOnly=False)  #: port of the local fronthaul
LTE_RRU_FRONTHAUL_IP_ADDRESS_REMOTE = Attribute(key='LTE_RRU_FRONTHAUL_IP_ADDRESS_REMOTE', type=int, isReadOnly=False)  #: IP of the remote fronthaul
LTE_RRU_FRONTHAUL_PORT_REMOTE = Attribute(key='LTE_RRU_FRONTHAUL_PORT_REMOTE', type=int, isReadOnly=False)  #: port of the remote fronthaul
# LTE_RRU_MCC = Attribute(key='LTE_RRU_MCC', type=int, isReadOnly=False)  #: RRU Mobile Country Code
# LTE_RRU_MNC = Attribute(key='LTE_RRU_MNC', type=int, isReadOnly=False)  #: RRU Mobile Network Code

#********
#UE net Attribute
#********

LTE_UE_APN = Attribute(key='LTE_UE_APN', type=str, isReadOnly=False)  #: APN
LTE_UE_PLMN = Attribute(key='LTE_UE_PLMN', type=int, isReadOnly=False)  #: PLMNID

# UE_network_address_pool = Attribute(key='UE_network_address_pool', type=int, isReadOnly=False)  #: pool of IP addressess. The MME will assign at the UE one address from the such pool
# default_DNS_addr = Attribute(key='default_DNS_addr', type=int, isReadOnly=False)  #: default DNS IP address





























