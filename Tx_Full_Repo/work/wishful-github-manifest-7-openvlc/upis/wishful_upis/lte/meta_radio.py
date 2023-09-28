"""The WiSHFUL radio control interface, attributes.
Used for configuration/monitoring of the radio
layers of the LTE technology
"""
__author__ = "Francesco Giannone, Domenico Garlisi"
__copyright__ = "Copyright (c) 2017, Sant'Anna, CNIT"
__version__ = "0.1.0"
__email__ = "{francesco.giannone@santannapisa.it, domenico.garlisi@cnit.it}"

from ..meta_models import ValueDoc, Attribute, Measurement, Event, Action

# ATTRIBUTES


#********
#ENB Attribute
#********
LTE_ENB_DL_BW = Attribute(key='LTE_ENB_DL_BW', type=int, isReadOnly=False)  #: eNB Bandwidth DL
LTE_ENB_UL_BW = Attribute(key='LTE_ENB_UL_BW', type=int, isReadOnly=False)  #: eNB bandwidth UL
LTE_ENB_DL_FREQ = Attribute(key='LTE_ENB_DL_FREQ', type=int, isReadOnly=False)  #: eNB DL center frequency
LTE_ENB_UL_FREQ = Attribute(key='LTE_ENB_UL_FREQ', type=int, isReadOnly=False)  #: eNB UL center frequency
LTE_ENB_FREQ_BAND = Attribute(key='LTE_ENB_FREQ_BAND', type=int, isReadOnly=False)  #: 3GPP eNB Frequency band indicator
LTE_ENB_N_TX_ANT = Attribute(key='LTE_ENB_N_TX_ANT', type=int, isReadOnly=False)  #: eNB Number of TX antennas
LTE_ENB_N_RX_ANT = Attribute(key='LTE_ENB_N_RX_ANT', type=int, isReadOnly=False)  #: eNB Number of RX antennas
LTE_ENB_REF_SIG_POWER = Attribute(key='LTE_ENB_REF_SIG_POWER', type=int, isReadOnly=False)  #: eNB Reference signal power
LTE_ENB_TX_GAIN = Attribute(key='LTE_ENB_TX_GAIN', type=int, isReadOnly=False)  #: eNB TX gain
LTE_ENB_RX_GAIN = Attribute(key='LTE_ENB_RX_GAIN', type=int, isReadOnly=False)  #: eNB RX gain
LTE_ENB_DUPLEX_MODE = Attribute(key='LTE_ENB_DUPLEX_MODE', type=int, isReadOnly=False)  #: eNB Duplex Mode (TDD/FDD)
LTE_ENB_TDD_CONFIGURATION = Attribute(key='LTE_ENB_TDD_CONFIGURATION', type=int, isReadOnly=False)  #: 3GPP eNB TDD configuration mode

# LTE_RCC_DL_BW = Attribute(key='LTE_RCC_DL_BW', type=int, isReadOnly=False)  #: RCC Bandwidth DL
# LTE_RCC_UL_BW = Attribute(key='LTE_RCC_UL_BW', type=int, isReadOnly=False)  #: RCC Bandwidth UL
# LTE_RCC_DL_FREQ = Attribute(key='LTE_RCC_DL_FREQ', type=int, isReadOnly=False)  #: RCC DL center frequency
# LTE_RCC_UL_FREQ = Attribute(key='LTE_RCC_UL_FREQ', type=int, isReadOnly=False)  #: RCC UL center frequency
# LTE_RCC_FREQ_BAND = Attribute(key='LTE_RCC_FREQ_BAND', type=int, isReadOnly=False)  #: 3GPP RCC Frequency band indicator
# LTE_RCC_N_TX_ANT = Attribute(key='LTE_RCC_N_TX_ANT', type=int, isReadOnly=False)  #: RCC Number of TX antennas
# LTE_RCC_N_RX_ANT = Attribute(key='LTE_RCC_N_RX_ANT', type=int, isReadOnly=False)  #: RCC Number of RX antennas
# LTE_RCC_REF_SIG_POWER = Attribute(key='LTE_RCC_REF_SIG_POWER', type=int, isReadOnly=False)  #: RCC Reference signal power
# LTE_RCC_TX_GAIN = Attribute(key='LTE_RCC_TX_GAIN', type=int, isReadOnly=False)  #: RCC TX gain
# LTE_RCC_RX_GAIN = Attribute(key='LTE_RCC_RX_GAIN', type=int, isReadOnly=False)  #: RCC RX gain
# LTE_RCC_DUPLEX_MODE = Attribute(key='LTE_RCC_DUPLEX_MODE', type=int, isReadOnly=False)  #: RCC Duplex Mode (TDD/FDD)
# LTE_RCC_TDD_CONFIGURATION = Attribute(key='LTE_RCC_TDD_CONFIGURATION', type=int, isReadOnly=False)  #: 3GPP RCC TDD configuration mode
#
# LTE_RRU_DL_BW = Attribute(key='LTE_RRU_DL_BW', type=int, isReadOnly=False)  #: RRU Bandwidth DL
# LTE_RRU_UL_BW = Attribute(key='LTE_RRU_UL_BW', type=int, isReadOnly=False)  #: RRU Bandwidth UL
# LTE_RRU_DL_FREQ = Attribute(key='LTE_RRU_DL_FREQ', type=int, isReadOnly=False)  #: RCC DL center frequency
# LTE_RRU_UL_FREQ = Attribute(key='LTE_RRU_UL_FREQ', type=int, isReadOnly=False)  #: RCC UL center frequency
# LTE_RRU_FREQ_BAND = Attribute(key='LTE_RRU_FREQ_BAND', type=int, isReadOnly=False)  #: 3GPP RRU Frequency band indicator
# LTE_RRU_N_TX_ANT = Attribute(key='LTE_RRU_N_TX_ANT', type=int, isReadOnly=False)  #: RRU Number of TX antennas
# LTE_RRU_N_RX_ANT = Attribute(key='LTE_RRU_N_RX_ANT', type=int, isReadOnly=False)  #: RRU Number of RX antennas
# LTE_RRU_REF_SIG_POWER = Attribute(key='LTE_RRU_REF_SIG_POWER', type=int, isReadOnly=False)  #: RRU Reference signal power
# LTE_RRU_TX_GAIN = Attribute(key='LTE_RRU_TX_GAIN', type=int, isReadOnly=False)  #: RRU TX gain
# LTE_RRU_RX_GAIN = Attribute(key='LTE_RRU_RX_GAIN', type=int, isReadOnly=False)  #: RRU RX gain
# LTE_RRU_DUPLEX_MODE = Attribute(key='LTE_RRU_DUPLEX_MODE', type=int, isReadOnly=False)  #: RRU Duplex Mode (TDD/FDD)
# LTE_RRU_TDD_CONFIGURATION = Attribute(key='LTE_RRU_TDD_CONFIGURATION', type=int, isReadOnly=False)  #: 3GPP RRU TDD configuration mode

# PUCCH_ENB = Attribute(key='PUCCH_ENB', type=int, isReadOnly=False)  #: eNB PUCCH channel power
# PUSCH_ENB = Attribute(key='PUSCH_ENB', type=int, isReadOnly=False)  #: eNB PUSCH channel power
# PUCCH_RCC = Attribute(key='PUCCH_RCC', type=int, isReadOnly=False)  #: RCC PUCCH channel power
# PUSCH_RCC = Attribute(key='PUSCH_RCC', type=int, isReadOnly=False)  #: RCC PUSCH channel power
# PUCCH_RRU = Attribute(key='PUCCH_RRU', type=int, isReadOnly=False)  #: RRU PUCCH channel power
# PUSCH_RRU = Attribute(key='PUSCH_RRU', type=int, isReadOnly=False)  #: RRU PUSCH channel power

#********
#UE net Attribute
#********

LTE_UE_DL_FREQ = Attribute(key='LTE_UE_DL_FREQ', type=int, isReadOnly=False)  #: DL center frequency
LTE_UE_DL_BW = Attribute(key='LTE_UE_DL_BW', type=int, isReadOnly=False)  #: UL center frequency
LTE_UE_UL_BW = Attribute(key='LTE_UE_UL_BW', type=int, isReadOnly=False)  #: Bandwidth DL
LTE_UE_TX_GAIN = Attribute(key='LTE_UE_TX_GAIN', type=int, isReadOnly=False)  #: Bandwidth UL
LTE_UE_RX_GAIN = Attribute(key='LTE_UE_RX_GAIN', type=int, isReadOnly=False)  #: RRU RX gain
LTE_UE_N_TX_ANT = Attribute(key='LTE_UE_N_TX_ANT', type=int, isReadOnly=False)  #: Number of TX antennas
LTE_UE_N_RX_ANT = Attribute(key='LTE_UE_N_RX_ANT', type=int, isReadOnly=False)  #: Number of RX antennas
LTE_UE_RADIO_STATE = Attribute(key='LTE_UE_RADIO_STATE', type=bool, isReadOnly=False)  #: UE State
