* ---- CD4093 gate, inputs tied (Schmitt inverter) with hysteresis + 190 ns delay + ~600 ohm output
.subckt SCHMITT_INV in out vdd
Bth th 0 V = 1.9 + 1.0*(0.5+0.5*tanh((V(q)-2.5)*20))
Bc n1 0 V = V(vdd) * (0.5 - 0.5*tanh((V(in)-V(th))*60))
* note: q is output state; when output high threshold is VP (2.9), when low VN (1.9)
Rd1 n1 n2 50
T1 n2 0 n3 0 Z0=50 TD=190n
Rd2 n3 0 50
Bq qi 0 V = 2*V(n3)
Rq qi qf 1
Cq qf 0 40p
Rs qf q 1m
Ro q out 400
.ends
* ---- CD4093 2-input NAND (clean logic inputs) with delay
.subckt NAND2 a b out vdd
Bc n1 0 V = V(vdd) * (1 - (0.5+0.5*tanh((V(a)-2.5)*20))*(0.5+0.5*tanh((V(b)-2.5)*20)))
Rd1 n1 n2 50
T1 n2 0 n3 0 Z0=50 TD=190n
Rd2 n3 0 50
Bq qi 0 V = 2*V(n3)
Ro qi out 400
.ends
* ---- MCP602-like op amp: GBW 2.8 MHz, A0=1e5, rail-to-rail output (0..5 V)
.subckt OPAMP inp inn out vdd
Gm 0 n1 value={1e-3*tanh((V(inp)-V(inn))*1000)}
Rp n1 0 1e8
Cp n1 0 56.8p
Gcl n1 0 value={0.1*(max(V(n1)-V(vdd),0) + min(V(n1),0))}
Bo oi 0 V = max(min(V(n1), V(vdd)-0.02), 0.02)
Ro oi out 50
.ends
* ---- LM386-like: gain 20, Vout DC = Vs/2, swing +/-1.8 V at 5 V, 50k inputs, BW ~300 kHz
.subckt LM386 inp inn out vs
Rin1 inp 0 50k
Rin2 inn 0 50k
Bg g 0 V = 20*(V(inp)-V(inn))
Rbw g gf 1k
Cbw gf 0 530p
Bo oi 0 V = V(vs)/2 + 1.8*tanh(V(gf)/1.8)
Ro oi out 0.2
.ends
