STATES = ('S','V1','V2','EV1','E', 'I', 'M', 'O', 'H')
NUM_STATES = len(STATES)
NUM_TRANS = 15
COLORS = ['green', 'orange', 'red', 'pink', 'gray', 'blue','purple','lightblue','yellow']


class STATE:
    S = 0  # susceptible
    V1 = 1
    V2 = 2
    EV1 = 3 
    E = 4  # exposed without symptom
    I = 5  # infected and with symptom
    M = 6  # with medical care
    O = 7  # out of system, dead  or cured
    H = 8  # maximum number of beds in hospital


class TRANS:
    S2E = 0
    E2I =1
    S2V1=2
    S2V2=3
    V12EV1=4
    I2M = 5
    I2O = 6
    M2O = 7
    EV12O=8
    #V22O=9
    EbyE = 9
    EbyI = 10
    EbyEV1=11
    EV1byE=12
    EV1byI=13
    EV1byEV1=14

      