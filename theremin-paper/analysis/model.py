import numpy as np
from scipy.optimize import brentq
VDD,VP,VN,tpd,ro=5.0,2.9,1.9,190e-9,400.0
def period(R,C):
    RC=(R+ro)*C; e=np.exp(-tpd/RC)
    VH=VDD-(VDD-VP)*e; VL=VN*e
    th=RC*np.log((VDD-VL)/(VDD-VP))+tpd; tl=RC*np.log(VH/VN)+tpd
    return th+tl, th/(th+tl)
f=lambda R,C:1/period(R,C)[0]
if __name__=="__main__":
    fB=f(10e3,100e-12); print("fB",fB,"duty",period(10e3,100e-12)[1],"naive",1/(1.2e-6))
    Cant=8e-12
    rv=brentq(lambda r:f(5.1e3+r,100e-12+Cant)-fB,0,10e3); print("RV1 zero beat",rv)
    fA=lambda C,r=rv: f(5.1e3+r,C)
    S=(fA(108e-12)-fA(108.01e-12))/0.01; print("sens Hz/pF",S)
    tun=(f(5.1e3+rv-1,108e-12)-f(5.1e3+rv,108e-12)); print("Hz/ohm",tun,"kHz/deg",tun*10e3/270/1e3)
    print("range",f(5.1e3,108e-12),f(15.1e3,108e-12))
    print("dC for 1kHz",1000/S)
