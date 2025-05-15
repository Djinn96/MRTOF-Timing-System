import numpy as np
import pandas as pd
from pythonlib.tcplib import timingTCPSocket
from pythonlib.timinglib import TimingCalculator, DurationParam, oneShotArrayMap

PORT = 4001
IP = "202.13.199.70"

class timingController:
    def __init__(self):
        self.socket = timingTCPSocket(IP,PORT)
        self.__timingCalculator__ = TimingCalculator(200)
        self.updateDurationsFromFile()
        return

    # READ OPERATIONS

    def updateDurationsFromFile(self):
        durations = pd.read_csv("../settings/fpga_durations.csv")
        for i,row in durations.iterrows(): self.__timingCalculator__.setDurationParam(DurationParam[row["name"]],row["value"])
        self.__timingCalculator__.calcTimings()
        self.__timingCalculator__.populateOSAFromTimings()
        return

    def updateDurationParameters(self,data:dict):
        for i in data: self.__timingCalculator__.setDurationParam(DurationParam[i],data[i])
        self.__timingCalculator__.calcTimings()
        self.__timingCalculator__.populateOSAFromTimings()
        return

    def readOneShotElementInFPGAviaTCP(self,idx:int):
        """
        Read one element in OneShotArray from FPGA.
        WARNING socket connection is not handled.
        """
        # get address in hex string format (2 digits, leading zeros)
        addrLow = '{:02x}'.format(idx*2    )
        addrUpp = '{:02x}'.format(idx*2 + 1)

        # response contains 16-bit data each in hex string
        dataLow = self.socket.sendWaitResponse("R"+addrLow+"\r\n")
        dataUpp = self.socket.sendWaitResponse("R"+addrUpp+"\r\n")

        # concatenate data and parse hex to int
        return int(dataUpp + dataLow,16)

    def readOneShotArrayInFPGAviaTCP(self):
        """
        Read full OneShotArray from FPGA.
        WARNING socket connection is not handled.
        """
        oneShotArray = np.zeros(64,dtype=np.dtype('u4'))
        print("Reading from FPGA...")
        for i in range(len(oneShotArray)): oneShotArray[i] = self.readOneShotElementInFPGAviaTCP(i)
        print("Reading Done!")
        return oneShotArray
    
    def updateFPGATimings(self):
        """
        Read full OneShotArray from FPGA and converts it to timing values in microseconds.
        Values are populated in tPar array.
        """
        # connect to FPGA, read, then close connection
        self.socket.connect()
        data = self.readOneShotArrayInFPGAviaTCP()
        self.socket.close()

        self.__timingCalculator__.setFPGAOneShotArray(data)
        self.__timingCalculator__.populateFPGATimingsFromFGPAOSA()

        return

    def readDurations(self):   return self.__timingCalculator__.getDurationParams()
    def readTimings(self):     return self.__timingCalculator__.getTimingParams()
    def readFPGATimings(self): return self.__timingCalculator__.getFPGATimingParams()

    # WRITE OPERATIONS

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