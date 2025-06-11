import numpy as np
import pandas as pd
from pythonlib.tcplib import timingTCPSocket
from pythonlib.timinglib import TimingCalculator, DurationParam, oneShotArrayMap

PORT = 4001
IP = "202.13.199.70"

class timingController:
    def __init__(self,durationsFilePath:str="../settings/fpga_durations.csv",bpaFilePath:str="../settings/fpga_bitPatternArray.csv"):
        self.socket = timingTCPSocket(IP,PORT)
        self.__timingCalculator__ = TimingCalculator(200)
        self.fpgaDurationsFile = durationsFilePath
        self.fpgaBPAFilePath = bpaFilePath
        self.updateDurationsFromFile()
        self.updateBitPatternArrayFromFile()
        return

    # FILE READ OPERATIONS

    def updateDurationsFromFile(self):
        durations = pd.read_csv(self.fpgaDurationsFile)
        for i,row in durations.iterrows(): self.__timingCalculator__.setDurationParam(DurationParam[row["name"]],row["value"])
        self.__timingCalculator__.calcTimings()
        self.__timingCalculator__.populateOSAFromTimings()
        return
    
    def updateBitPatternArrayFromFile(self):
        bpaDF = pd.read_csv(self.fpgaBPAFilePath)
        bpa = np.array(bpaDF['value'],dtype=np.dtype(int)) # us
        self.__timingCalculator__.setBitPatternArray(bpa)
        xorMask = np.array([v*2**i for i,v in enumerate(bpaDF['xorMask'])]).sum()
        self.__timingCalculator__.setXORMask(xorMask)
        return
    
    # FRONTEND READ OPERATIONS

    def updateDurationParameters(self,data:dict):
        '''
        To be used by frontend. User sets intended values in the UI and sends it to API Server via REST API.
        '''
        for i in data: self.__timingCalculator__.setDurationParam(DurationParam[i],data[i])
        self.__timingCalculator__.calcTimings()
        self.__timingCalculator__.populateOSAFromTimings()
        return
    
    # FPGA READ OPERATIONS
    
    def read32BitRegister(self,addrLowInt:int):
        """
        Read one element in OneShotArray from FPGA.
        WARNING socket connection is not handled. Use updateFPGATimings()
        """
        # get address in hex string format (2 digits, leading zeros)
        addrLow = '{:02x}'.format(addrLowInt)
        addrUpp = '{:02x}'.format(addrLowInt + 1)

        # response contains 16-bit data each in hex string
        dataLow = self.socket.sendWaitResponse("R"+addrLow+"\r\n")
        dataUpp = self.socket.sendWaitResponse("R"+addrUpp+"\r\n")

        # concatenate data and parse hex to int
        return int(dataUpp + dataLow,16)

    def readOneShotArrayInFPGAviaTCP(self):
        """
        Read full OneShotArray from FPGA.
        WARNING socket connection is not handled. Use updateFPGATimings()
        """
        oneShotArray = np.zeros(64,dtype=np.dtype('u4'))
        for i in range(len(oneShotArray)): oneShotArray[i] = self.read32BitRegister(i*2) # addrLow = idx*2, addrUpp = idx*2 + 1
        return oneShotArray
    
    def readBitPatternArrayInFPGAviaTCP(self):
        """
        Read full BitPatternArray from FPGA.
        WARNING socket connection is not handled. Use updateFPGATimings()
        """
        bitPatternArray = np.zeros(16,dtype=np.dtype('u4'))
        for i in range(len(bitPatternArray)): bitPatternArray[i] = self.read32BitRegister(i*2 + 132) # addrLow = idx*2 + 132, addrUpp = idx*2 + 1 + 132
        return bitPatternArray

    
    def readXORMaskInFPGAviaTCP(self):
        """
        Read XORMask from FPGA.
        WARNING socket connection is not handled. Use updateFPGATimings()
        """
        return self.read32BitRegister(198)
    
    def updateFPGATimings(self):
        """
        Read full OneShotArray from FPGA and converts it to timing values in microseconds.
        Values are populated in tPar array.
        Reads BitPatternArray and XOR Mask from FPGA
        """
        # connect to FPGA, read, then close connection
        self.socket.connect()
        data_osa = self.readOneShotArrayInFPGAviaTCP()
        data_bpa = self.readBitPatternArrayInFPGAviaTCP()
        data_xor = self.readXORMaskInFPGAviaTCP()
        self.socket.close()

        self.__timingCalculator__.setFPGAOneShotArray(data_osa)
        self.__timingCalculator__.populateFPGATimingsFromFGPAOSA()
        self.__timingCalculator__.setFPGABitPatternArray(data_bpa)
        self.__timingCalculator__.setFPGAXORMask(data_xor)
        return

    def readDurations(self):   return self.__timingCalculator__.getDurationParams()
    def readTimings(self):     return self.__timingCalculator__.getTimingParams()
    def readFPGATimings(self): return self.__timingCalculator__.getFPGATimingParams()

    # FPGA WRITE OPERATIONS

    def writeOneShotElementInFPGAviaTCP(self,idx:int):
        """
        Write one element in OneShotArray from FPGA.
        WARNING socket connection is not handled.
        """
        # get address in hex string format (2 digits, leading zeros)
        addrLow = '{:02x}'.format(idx*2    )
        addrUpp = '{:02x}'.format(idx*2 + 1)

        timingValue = self.__timingCalculator__.getOneShotArrayElement(idx)
        timingHexVal = '{:08x}'.format(timingValue)
        timingHexUpp = timingHexVal[:4]
        timingHexLow = timingHexVal[4:]

        # response contains 16-bit data each in hex string
        dataLow = self.socket.sendWaitResponse("W"+addrLow+timingHexLow+"\r\n")
        dataUpp = self.socket.sendWaitResponse("W"+addrUpp+timingHexUpp+"\r\n")
        # int(dataUpp+dataLow,16) # is the existing value in FPGA before writing new value

        return
    
    def writeOneShotArrayInFPGAviaTCP(self):
        """
        Write full OneShotArray from FPGA.
        """
        self.socket.connect()
        print("Writing to FPGA...")
        for i in range(self.__timingCalculator__.getOneShotArrayLength()): self.writeOneShotElementInFPGAviaTCP(i)
        self.socket.close()
        print("Writing Done!")
        return
    
    def executeTimingsInFPGAviaTCP(self):
        """
        Execute current timings in FPGA
        """
        self.socket.connect()
        print("Executing FPGA...")
        response = self.socket.sendWaitResponse("Z00\r\n")
        print(response)
        self.socket.close()
        print("Execution Done!")

    # Getters

    def getBPATimingPulses(self): return self.__timingCalculator__.getBitPatternArrayPulses()
    def getXORMask(self): return self.__timingCalculator__.getXORMask()