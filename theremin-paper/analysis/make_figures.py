import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal
plt.rcParams.update({"font.family":"serif","font.serif":["DejaVu Serif"],"font.size":8,"axes.linewidth":0.6,
  "axes.grid":True,"grid.alpha":0.3,"grid.linewidth":0.4,"lines.linewidth":0.9,"savefig.bbox":"tight","savefig.pad_inches":0.02})
C_BLUE="#1f4e79"; C_ORG="#c0504d"; C_GRN="#4f7f3a"; C_GRY="#666666"
import os, sys
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0, HERE); from model import f as fosc, period
VDD=5.0
duty=0.482
W=3.45; H=2.1

# ---- behavioural simulation of mixer + filter ----
fs=100e6; Tsim=3.2e-3; t=np.arange(0,Tsim,1/fs)
f1=692.1e3; fb=1000.0; f2=f1-fb
def sq(f,ph=0.0): return ((np.mod(f*t+ph,1.0))<duty).astype(float)*VDD
A=sq(f1); B=sq(f2,0.13)
AND=np.where((A>0)&(B>0),VDD,0.0)       # Gate C (NAND) followed by Gate D (inverter)
R=10e3;C1=2.2e-9;C2=1e-9
num=[1.0]; den=[R*R*C1*C2, C2*2*R, 1.0]
bz,az=signal.bilinear(num,den,fs); sos=signal.tf2sos(bz,az)
y=signal.sosfilt(sos,AND)
np.save("/tmp/y.npy",y[::100])

car=np.loadtxt(os.path.join(ROOT,"spice","carriers.txt")); tc=car[:,0]; oa=car[:,1]; ob=car[:,3]; an=car[:,5]
full=np.loadtxt(os.path.join(ROOT,"spice","full_out.txt")); tf=full[:,0]; sk=full[:,1]; spk=full[:,3]
fig,ax=plt.subplots(4,1,figsize=(W,4.6))
m=(tc>30e-6)&(tc<36e-6); x=(tc[m]-30e-6)*1e6
ax[0].plot(x,oa[m]+6.0,color=C_BLUE,label="U1A out (antenna)")
ax[0].plot(x,ob[m],color=C_ORG,label="U1B out (reference)")
ax[0].set_yticks([]); ax[0].set_ylim(-0.8,15.5); ax[0].set_xlabel("Time (µs)")
ax[0].legend(loc="upper center",fontsize=6.5,ncol=2,framealpha=0.95,bbox_to_anchor=(0.5,1.02))
ax[0].set_title("(a) Oscillator outputs, ≈692 kHz",fontsize=8,loc="left")
ax[1].plot(x,an[m],color=C_GRY); ax[1].set_ylabel("V"); ax[1].set_xlabel("Time (µs)")
ax[1].set_title("(b) U1D output (AND of the two carriers)",fontsize=8,loc="left")
mf=(tf>0.8e-3)
ax[2].plot(tf[mf]*1e3,sk[mf],color=C_GRN); ax[2].set_ylabel("V"); ax[2].set_xlabel("Time (ms)")
ax[2].set_title("(c) U2A output: 1.00 kHz triangle, 0.02–2.39 V",fontsize=8,loc="left")
ax[3].plot(tf[mf]*1e3,spk[mf],color=C_BLUE); ax[3].set_ylabel("V"); ax[3].set_xlabel("Time (ms)")
ax[3].set_title("(d) Speaker voltage, full volume: 2.7 V p-p",fontsize=8,loc="left")
fig.tight_layout(h_pad=0.3); fig.savefig(os.path.join(ROOT,"paper","figs","waveforms.pdf")); plt.close()

# ---- spectrum ----
seg=AND[t>0.2e-3]; seg2=y[t>0.2e-3]
N=len(seg); win=np.hanning(N)
def spec(x):
    X=np.abs(np.fft.rfft((x-x.mean())*win))/ (win.sum()/2); return 20*np.log10(X+1e-9)
fr=np.fft.rfftfreq(N,1/fs)
fig,ax=plt.subplots(figsize=(W,2.0))
sel=(fr>100)&(fr<5e6)
ax.semilogx(fr[sel],spec(seg)[sel],color=C_GRY,lw=0.5,label="Mixer output")
ax.semilogx(fr[sel],spec(seg2)[sel],color=C_GRN,lw=0.7,label="After LPF")
for k,lab in [(fb,"$f_b$"),(3*fb,"$3f_b$"),(f1,"carrier")]:
    ax.axvline(k,color=C_ORG,lw=0.4,ls="--")
    ax.text(k*1.1,-118,lab,fontsize=6.5,color=C_ORG)
ax.set_ylim(-130,10); ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Magnitude (dBV)")
ax.legend(fontsize=6.5,loc="lower left")
fig.savefig(os.path.join(ROOT,"paper","figs","spectrum.pdf")); plt.close()
Xs=spec(seg2); i1=np.argmin(abs(fr-fb)); i3=np.argmin(abs(fr-3*fb)); ic=np.argmin(abs(fr-f1))
print("fund",Xs[i1-3:i1+4].max(),"3rd",Xs[i3-3:i3+4].max(),"carrier",Xs[ic-50:ic+50].max())

# ---- Bode ----
f=np.logspace(1,6.5,600); s=2j*np.pi*f
Hsk=1/(s*s*R*R*C1*C2+s*C2*2*R+1)
Hhp=(s*1e-6*108.3e3)/(1+s*1e-6*108.3e3)
Hout=(s*220e-6*8)/(1+s*220e-6*8)
fig,ax=plt.subplots(figsize=(W,1.9))
ax.semilogx(f,20*np.log10(abs(Hsk)),color=C_BLUE,label="Sallen–Key LPF (U2A)")
ax.semilogx(f,20*np.log10(abs(Hsk*Hhp*Hout)),color=C_ORG,ls="--",label="Full audio path (normalised)")
ax.axvline(10.73e3,color=C_GRY,lw=0.5,ls=":"); ax.text(12e3,-8,"$f_c$=10.7 kHz",fontsize=6.5)
ax.axvline(692e3,color=C_GRY,lw=0.5,ls=":"); ax.text(250e3,-20,"carrier\n692 kHz",fontsize=6.5)
ax.axvspan(200,5e3,color=C_GRN,alpha=0.08); ax.text(260,-110,"playing band",fontsize=6.5,color=C_GRN)
ax.set_ylim(-120,8); ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Gain (dB)"); ax.legend(fontsize=6.5,loc="lower left")
fig.savefig(os.path.join(ROOT,"paper","figs","bode.pdf")); plt.close()

# ---- pitch vs distance model + pot tuning ----
S=3.879e3  # Hz/pF
d=np.linspace(3,35,300)
Ch=1.29*(5/d)**2   # pF, illustrative model
fig,ax=plt.subplots(1,2,figsize=(7.1,1.95))
for off,c,lab in [(0,C_BLUE,"Zero-beat at rest"),(300,C_ORG,"Pot offset +300 Hz (hybrid)")]:
    ax[0].plot(d,S*Ch+off,color=c,label=lab)
ax[0].axvspan(5,25,color=C_GRN,alpha=0.08); ax[0].text(6,6800,"observed playing range 5–25 cm",fontsize=6.5,color=C_GRN)
ax[0].set_yscale("log"); ax[0].set_ylim(40,12000); ax[0].set_xlabel("Hand–antenna distance (cm)"); ax[0].set_ylabel("Beat frequency (Hz)")
ax[0].legend(fontsize=6.5,loc="lower left"); ax[0].set_title("(a) Pitch vs. distance (model)",fontsize=8,loc="left")
Rp=np.linspace(0,10e3,400)
fv=np.array([fosc(5.1e3+r,108e-12) for r in Rp]); fr_=fosc(10e3,100e-12)
ax[1].plot(Rp/1e3,fv/1e3,color=C_BLUE,label="$f_A$ (antenna osc.)")
ax[1].axhline(fr_/1e3,color=C_ORG,ls="--",label="$f_B$ (reference)")
ax[1].plot([4.13],[fr_/1e3],'o',ms=3,color='k'); ax[1].annotate("zero beat\n$RV_1$≈4.13 kΩ",(4.13,fr_/1e3),(5.6,850),fontsize=6.5,arrowprops=dict(arrowstyle="-",lw=0.4))
ax[1].set_xlabel("Pitch pot setting $RV_1$ (kΩ)"); ax[1].set_ylabel("Frequency (kHz)"); ax[1].legend(fontsize=6.5)
ax[1].set_title("(b) Coarse tuning by the pitch pot",fontsize=8,loc="left")
fig.tight_layout(w_pad=1.5); fig.savefig(os.path.join(ROOT,"paper","figs","pitch.pdf")); plt.close()
print("beat at 5cm",S*0.95,"at 25cm",S*0.95*(5/25)**2)
