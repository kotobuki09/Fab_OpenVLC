__author__ = "Francesco Giannone, Domenico Garlisi"
__copyright__ = "Copyright (c) 2017, Sant'Anna, CNIT"
__version__ = "0.1.0"
__email__ = "{francesco.giannone@santannapisa.it, domenico.garlisi@cnit.it}"

class Functional_split:
    __instance = None
    FUNCTIONAL_SPLIT_TYPES = None
    
    def enum(**enums):
        return type('Enum',() ,enums)
    
    def _init_(self):
        if Functional_split.__instance:
            raise Functional_split.__instance
        Functional_split.__instance = self
        self.FUNCTIONAL_SPLIT_TYPES = self.enum(FOURpFIVE = 4.5, FIVE = 5)
        self.__current_functional_split = self.FUNCTIONAL_SPLIT_TYPES.FOURpFIVE

    def set_split_level(self, value):
        self.__current_functional_split = value
        
        return 0

    def get_split_level(self):
        return self.__current_functional_split
