from enum import Enum, unique, auto
import numpy as np

@unique
class DurationParam(Enum):
    M_Period = 0
    Ma       = 1

    fQTacc   = 2
    fQTcool  = 3
    fQTeje   = 4
    fQTthru  = 5

    rQTacc   = 6
    rQTcool  = 7
    rQTeje   = 8
    rQTthru  = 9

    FTacc1   = 10
    FTcool1  = 11
    FTdmp1   = 12
    FTthru1  = 13

    FTacc2   = 14
    FTcool2  = 15
    FTdmp2   = 16
    FTthru2  = 17

    FTejeW   = 18

    rfoff2eje     = 19
    MTinjW2       = 20
    QTc2FTa       = 21
    FT1eje2DT     = 22
    FT1DTW        = 23
    FT1eje2MTinj  = 24
    MTinjW        = 25
    FT1eje2MTeje  = 26
    MTejeW        = 27
    FTeje2dmp     = 28
    FT1eje2FT2eje = 29
    toffset       = 30
    FT2eje2MTinj  = 31
    FT2eje2MTeje  = 32
    
    BNon       = 33
    BNwidth    = 34
    x1         = 35
    extra      = 36
    BNon2      = 37
    BNwidth2   = 38
    FT2eje2DT2 = 39
    FT2DTW     = 40
    FTrfclk    = 41
    rf2acc     = 42

#@unique
#class TimingParam(Enum):
timingParams = ["Period",  "p",
                "fQT_acc", "fQT_cool", "fQT_thru", "fQT_eje",  "FT_acc1", "FT_cool1", "FT_thru1",
                "rQT_acc", "rQT_cool", "rQT_eje",  "rQT_thru", "FT_acc2", "FT_cool2", "FT_thru2",
                "DT_on_1", "DT_off_1",
                "FT_eje_on_1", "FT_eje_off_1", "FT_rf_on_1",  "FT_rf_off_1",
                "MT_inj_on_1", "MT_inj_off_1", "MT_eje_on_1", "MT_eje_off_1",
                "DT_on_2", "DT_off_2",
                "FT_eje_on_2", "FT_eje_off_2", "FT_rf_on_2",  "FT_rf_off_2",
                "MT_inj_on_2", "MT_inj_off_2", "MT_eje_on_2", "MT_eje_off_2",
                "TAG_on",  "TAG_off", "BN_on", "BN_off", "BN_on_2", "BN_off_2",
                "Not_Used",
                ]

TimingParam = Enum('TimingParam', timingParams, start=0)


oneShotArrayMap = [
    TimingParam.Period,      TimingParam.p,
    TimingParam.fQT_acc,     TimingParam.fQT_cool,
    TimingParam.fQT_cool,    TimingParam.fQT_thru,
    TimingParam.fQT_eje,     TimingParam.fQT_thru,
    TimingParam.FT_acc1,     TimingParam.FT_cool1,
    TimingParam.FT_cool1,    TimingParam.FT_thru1,
    TimingParam.Not_Used,    TimingParam.Not_Used,
    TimingParam.rQT_acc,     TimingParam.rQT_cool,
    
    TimingParam.rQT_cool,    TimingParam.rQT_thru,
    TimingParam.rQT_eje,     TimingParam.rQT_thru,
    TimingParam.FT_acc2,     TimingParam.FT_cool2,
    TimingParam.FT_acc2,     TimingParam.FT_thru2,
    TimingParam.Not_Used,    TimingParam.Not_Used,
    TimingParam.DT_on_1,     TimingParam.DT_off_1,
    TimingParam.FT_eje_on_1, TimingParam.FT_eje_off_1,
    TimingParam.FT_rf_on_1,  TimingParam.FT_rf_off_1,

    TimingParam.MT_inj_on_1, TimingParam.MT_inj_off_1,
    TimingParam.MT_eje_on_1, TimingParam.MT_eje_off_1,
    TimingParam.DT_on_2,     TimingParam.DT_off_2,
    TimingParam.FT_eje_on_2, TimingParam.FT_eje_off_2,
    TimingParam.FT_rf_on_2,  TimingParam.FT_rf_off_2,
    TimingParam.MT_inj_on_2, TimingParam.MT_inj_off_2,
    TimingParam.MT_eje_on_2, TimingParam.MT_eje_off_2,
    TimingParam.TAG_on,      TimingParam.TAG_off,
    
    TimingParam.BN_on,       TimingParam.BN_off,
]

class TimingCalculator:
    def __init__(self,clockFreq:int=200):
        NumDurationParams = len(DurationParam)
        NumTimingParams = len(TimingParam)
        self.__dPar__       = np.zeros(NumDurationParams,dtype=np.dtype(float))   # __dPar__              can be updated from file or from webserver
        self.__tPar__       = np.zeros(NumTimingParams,dtype=np.dtype(float))     # __tPar__              is to be calculated from __dPar__ only
        self.__oneShotArray__ = np.zeros(64,dtype=np.dtype('u4'))                 # __oneShotArray__      is to be calculated from __tPar__ only
        self.__oneShotArray_FPGA__ = np.zeros(64,dtype=np.dtype('u4'))            # __oneShotArray_FPGA__ is to be populated direct from FPGA only
        self.__tPar_FPGA__  = np.zeros(NumTimingParams,dtype=np.dtype(float))     # __tPar_FPGA__         is to be calculated from __oneShotArray_FPGA__ only
        self.clockFreq    = clockFreq #MHz
    
    def setDurationParam(self,param:DurationParam,value): self.__dPar__[param.value] = value
    def setFPGAOneShotArray(self,osa:np.ndarray): self.__oneShotArray_FPGA__ = osa

    def getTimingParam(self,par:TimingParam): return self.__tPar__[par]
    def getOneShotArrayElement(self,idx:int): return self.__oneShotArray__[idx]
    def getOneShotArrayLength(self): return len(self.__oneShotArray__)

    def getDurationParams(self): return self.__dPar__.copy()
    def getTimingParams(self): return self.__tPar__.copy()
    def getFPGATimingParams(self): return self.__tPar_FPGA__.copy()

    def calcTimings(self):
        """
        Calculate timings given the duration parameters.
        READS from self.dPar and WRITES to self.tPars ONLY.
        See: Watanabe-san's document on timing calculations.
        """
        Freq    = 1e6/self.__dPar__[DurationParam.M_Period.value]
        oPeriod = self.__dPar__[DurationParam.M_Period.value]
        op      = 0.05

        ofQT_cool = 1.0
        ofQT_eje  = ofQT_cool + self.__dPar__[DurationParam.fQTcool.value]
        ofQT_thru = ofQT_eje  + self.__dPar__[DurationParam.fQTeje.value]

        ofQT_acc = ofQT_thru+self.__dPar__[DurationParam.fQTthru.value]
        if (self.__dPar__[DurationParam.M_Period.value]-self.__dPar__[DurationParam.fQTacc.value]) > ofQT_acc:
            ofQT_acc = self.__dPar__[DurationParam.M_Period.value]-self.__dPar__[DurationParam.fQTacc.value]

        ABSfQTacc = self.__dPar__[DurationParam.M_Period.value]-ofQT_acc

        oFT_acc1  = ofQT_eje  - self.__dPar__[DurationParam.QTc2FTa.value]
        oFT_cool1 = oFT_acc1  + self.__dPar__[DurationParam.FTacc1.value]
        oFTdmp1   = oFT_cool1 + self.__dPar__[DurationParam.FTcool1.value]
        oFT_thru1 = oFTdmp1   + self.__dPar__[DurationParam.FTdmp1.value]

        oFT_eje_on_1  = oFTdmp1      - self.__dPar__[DurationParam.FTeje2dmp.value] #*c/c
        oFT_eje_off_1 = oFT_eje_on_1 + self.__dPar__[DurationParam.FTejeW.value]

        oFT_rf_off_1 = oFT_eje_on_1 - (self.__dPar__[DurationParam.rfoff2eje.value]/self.__dPar__[DurationParam.FTrfclk.value]) #*c/c
        oFT_rf_on_1  = oFT_acc1     - self.__dPar__[DurationParam.rf2acc.value]

        oDT_on_1  = oFT_eje_on_1 + self.__dPar__[DurationParam.FT1eje2DT.value]
        oDT_off_1 = oDT_on_1     + self.__dPar__[DurationParam.FT1DTW.value]

        oMT_inj_on_1  = oFT_eje_on_1 + self.__dPar__[DurationParam.FT1eje2MTinj.value]
        oMT_inj_off_1 = oMT_inj_on_1 + self.__dPar__[DurationParam.MTinjW.value]
        oMT_eje_on_1  = oFT_eje_on_1 + self.__dPar__[DurationParam.FT1eje2MTeje.value]
        oMT_eje_off_1 = oMT_eje_on_1 + self.__dPar__[DurationParam.MTejeW.value]

        oFT_eje_on_2 = oFT_eje_on_1 + self.__dPar__[DurationParam.FT1eje2FT2eje.value] #*c/c

        orQT_cool = (oFT_eje_on_2 + self.__dPar__[DurationParam.FTeje2dmp.value])-(self.__dPar__[DurationParam.FTcool2.value]+self.__dPar__[DurationParam.FTacc2.value]-self.__dPar__[DurationParam.QTc2FTa.value])-self.__dPar__[DurationParam.rQTcool.value]
        orQT_eje  = orQT_cool     + self.__dPar__[DurationParam.rQTcool.value]
        orQT_thru = orQT_eje      + self.__dPar__[DurationParam.rQTeje.value]

        orQT_acc = (orQT_cool-self.__dPar__[DurationParam.rQTacc.value])
        if (self.__dPar__[DurationParam.rQTacc.value] >= orQT_cool):
            if ((self.__dPar__[DurationParam.M_Period.value] - orQT_thru - self.__dPar__[DurationParam.rQTthru.value] + orQT_cool) < self.__dPar__[DurationParam.rQTacc.value]):
                orQT_acc = orQT_thru+self.__dPar__[DurationParam.rQTthru.value]
            else:
                orQT_acc = self.__dPar__[DurationParam.M_Period.value]-(self.__dPar__[DurationParam.rQTacc.value]-orQT_cool)
        
        ABSrQTacc = (orQT_cool-orQT_acc) if (orQT_acc < orQT_cool) else (self.__dPar__[DurationParam.M_Period.value]-orQT_acc)+orQT_cool

        oFT_acc2  = orQT_eje  - self.__dPar__[DurationParam.QTc2FTa.value]
        oFT_cool2 = oFT_acc2  + self.__dPar__[DurationParam.FTacc2.value]
        oFTdmp2   = oFT_cool2 + self.__dPar__[DurationParam.FTcool2.value]
        oFT_thru2 = oFTdmp2   + self.__dPar__[DurationParam.FTdmp2.value]

        oFT_eje_off_2 = oFT_eje_on_2 + self.__dPar__[DurationParam.FTejeW.value]

        oFT_rf_off_2 = oFT_eje_on_2 - (self.__dPar__[DurationParam.rfoff2eje.value]/self.__dPar__[DurationParam.FTrfclk.value]) #*c/c
        oFT_rf_on_2  = oFT_acc2     - self.__dPar__[DurationParam.rf2acc.value]

        Thalf     = oFT_eje_on_2 - oFT_eje_on_1
        oDT_on_2  = oFT_eje_on_2 + self.__dPar__[DurationParam.FT2eje2DT2.value]
        oDT_off_2 = oDT_on_2     + self.__dPar__[DurationParam.FT2DTW.value]

        oMT_inj_on_2  = oFT_eje_on_2 + self.__dPar__[DurationParam.FT2eje2MTinj.value]
        oMT_inj_off_2 = oMT_inj_on_2 + self.__dPar__[DurationParam.MTinjW2.value]
        oMT_eje_on_2  = oFT_eje_on_2 + self.__dPar__[DurationParam.FT2eje2MTeje.value]
        oMT_eje_off_2 = oMT_eje_on_2 + self.__dPar__[DurationParam.MTejeW.value]

        oTAG_on   = oFT_eje_on_2 - 2.0
        oTAG_off  = oFT_eje_on_1 - 2.0
        oBN_on    = oFT_eje_on_1 + self.__dPar__[DurationParam.BNon.value]
        oBN_off   = oBN_on       + self.__dPar__[DurationParam.BNwidth.value]
        oBN_on_2  = oFT_eje_on_2 + self.__dPar__[DurationParam.BNon2.value]
        oBN_off_2 = oBN_on_2     + self.__dPar__[DurationParam.BNwidth2.value]
        x1 = oFT_eje_on_2 - oMT_eje_off_1
        if x1 < 0: x1 += self.__dPar__[DurationParam.M_Period.value]
        x2 = oFT_eje_on_1 - oMT_eje_off_2
        if x2 < 0: x2 += self.__dPar__[DurationParam.M_Period.value]
        dMTejetoFT = x1 - x2

        self.__tPar__ = np.array([oPeriod,  op,
                                  ofQT_acc, ofQT_cool, ofQT_thru, ofQT_eje,  oFT_acc1, oFT_cool1, oFT_thru1,
                                  orQT_acc, orQT_cool, orQT_eje,  orQT_thru, oFT_acc2, oFT_cool2, oFT_thru2,
                                  oDT_on_1, oDT_off_1,
                                  oFT_eje_on_1, oFT_eje_off_1, oFT_rf_on_1,  oFT_rf_off_1,
                                  oMT_inj_on_1, oMT_inj_off_1, oMT_eje_on_1, oMT_eje_off_1,
                                  oDT_on_2, oDT_off_2,
                                  oFT_eje_on_2, oFT_eje_off_2, oFT_rf_on_2,  oFT_rf_off_2,
                                  oMT_inj_on_2, oMT_inj_off_2, oMT_eje_on_2, oMT_eje_off_2,
                                  oTAG_on,  oTAG_off, oBN_on, oBN_off, oBN_on_2, oBN_off_2,
                                  0,
                                 ],dtype=np.dtype(float))
        
        self.__tPar__[2:] = self.__tPar__[2:] + self.__dPar__[DurationParam.toffset.value]

    def populateOSAFromTimings(self):
        """
        Populate OneShotArray with values from TimingParams according to FPGA specification
        """
        if np.any(self.__tPar__ < 0): print("[WARNING] Negative timing parameter found!")

        tPar_32bit = (self.__tPar__ * self.clockFreq).astype(np.dtype('u4'))
        # May be necessary to add toffset

        for i,par in enumerate(oneShotArrayMap): self.__oneShotArray__[i] = tPar_32bit[par.value]

    def populateFPGATimingsFromFGPAOSA(self):
        """
        Populate timingParams with values from OneShotArray according to FPGA specification
        """
        OSA_time = self.__oneShotArray_FPGA__.astype(float) / self.clockFreq

        for i,par in enumerate(oneShotArrayMap):
            self.__tPar_FPGA__[par.value] = OSA_time[i]
