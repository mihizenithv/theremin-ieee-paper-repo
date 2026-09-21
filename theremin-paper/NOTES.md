# Design Notes

Working notes behind the paper: what was built, what was reconstructed, what changed from the first draft, how the design was verified, and what is still left to do.

---

## 1. Status at a glance

| Item | Status |
|---|---|
| Breadboard prototype | ✅ Built and working (pitch follows the hand, 5–25 cm range) |
| Documented schematic | ⚠️ **Reconstructed**, because the final breadboard was never drawn. Check it against your board (Section 2) |
| Analytical model | ✅ Done (`analysis/model.py`) |
| SPICE verification | ✅ Full-circuit netlist matches the hand analysis to within 0.05 % |
| Bench measurements | ❌ Not done yet; see the checklist in Section 7 |

---

## 2. Things to verify on the real breadboard

The first draft, the slides and the website notes all described slightly different circuits. The final build used **CD4093 + MCP602 + LM386 + 7805**, as shown on the slides. The schematic in this repo is a clean reconstruction of that build, with fixes wherever the earlier diagrams would not have worked electrically.

**Check these against your board before submitting:**

- [ ] **Pitch pot position.** In the schematic, RV1 (10 kΩ) is in series with R1 (5.1 kΩ) in the *antenna* oscillator's feedback path. Is that where yours is?
- [ ] **Volume pot.** The schematic has RV2 = 10 kΩ with R5 = 100 kΩ in series. What value did you use?
- [ ] **Mixer.** The schematic uses gate 3 of the CD4093 as the mixer and gate 4 as an inverter. Did your build mix with a gate, or by summing into the op-amp?
- [ ] **Filter capacitors** C3 = 2.2 nF and C4 = 1 nF are **my design values**.
- [ ] **LM386 output parts**: C7 = 220 µF, Zobel R6 = 10 Ω + C8 = 47 nF, pin-7 bypass C6 = 10 µF. These are **my values** from the datasheet recommendations.
- [ ] **The 1 MΩ resistor** in the original parts list has no identified position, so it was left out. Where did it go?
- [ ] **Antenna** length and type (twisted copper pair in the photo).

If anything differs, update `schematic/schematic.tex` and `spice/full.cir` together, then run `make all`.

---

## 3. Corrections compared with `docs/draft1_original.pdf`

| Draft said | Problem | Fixed to |
|---|---|---|
| Oscillators at 833 kHz and 122 kHz | Their difference (711 kHz) is not audible | Two matched oscillators at ≈692 kHz; the beat is set by the pot and the hand |
| Oscillator f = 1/(1.2RC) = 833 kHz | Ignores propagation delay and threshold overshoot | Full model gives **692 kHz**; the rule overestimates by 20 % |
| Sensitivity 8 kHz/pF | Uses the wrong frequency and ignores the delay term | **3.9 kHz/pF** |
| Low-pass cutoff 16 Hz (100 kΩ, 100 nF) | Would block the whole audio band (likely an nF/pF slip) | Sallen–Key filter, f_c = 10.7 kHz |
| MCP602 on 9 V | MCP602 is rated for 6 V maximum | Everything runs on the 5 V rail from the 7805 |
| MCP602 driving the 8 Ω speaker directly | An op-amp cannot drive 8 Ω | LM386 power amplifier |
| Ref [3] "Tewfik & Vries, IEEE Trans. ASSP 1990" | Could not be found; appears fabricated | Removed |
| Ref [4] "R. Moog, CMOS theremin, unpublished" | Not a real source | Replaced with Moog, *Electronics World*, Jan. 1961 (verified) |

## 4. Changes found during SPICE cross-checking (second revision)

- **Oscillator equation corrected.** During the 190 ns gate delay, the timing capacitor keeps charging past the threshold. Including that overshoot (Eq. 2–3 in the paper) moved the frequency from 839 kHz to **692 kHz**, and every dependent number was updated.
- **C5: 10 µF → 1 µF.** With 10 µF and the 108 kΩ load (τ = 1.1 s), the switch-on transient kept the LM386 saturated for seconds. With 1 µF, τ = 0.11 s, and the corner is still 1.5 Hz.
- **C9: 0.1 µF → 0.33 µF**, as the 7805 datasheet recommends.
- Explicit decoupling (C12–C15) and the unused op-amp half (U2B, wired as a follower at 0 V) are now drawn on the schematic.

---

## 5. Design values and key equations

**Oscillator period** (Schmitt thresholds V_P = 2.9 V, V_N = 1.9 V; t_pd = 190 ns; r_o ≈ 400 Ω; τ = (R + r_o)C):

```
V_H = V_DD − (V_DD − V_P)·e^(−t_pd/τ)      V_L = V_N·e^(−t_pd/τ)
T   = τ·[ ln((V_DD − V_L)/(V_DD − V_P)) + ln(V_H/V_N) ] + 2·t_pd
```

| Quantity | Value |
|---|---|
| f_B (10 kΩ, 100 pF) | 692.1 kHz, duty cycle 48.2 % |
| f_A over the pot's travel (RV1 = 0 → 10 kΩ) | 941.6 → 507.2 kHz |
| Zero beat | RV1 = 4.13 kΩ (assumes C_ant ≈ 8 pF) |
| Pot slope | 43.5 Hz/Ω ≈ 1.6 kHz per degree (270° pot) |
| Antenna sensitivity | 3.9 kHz/pF → 1 kHz per 0.26 pF |
| Mixer output after filter | Triangle, 0 to V_DD·D = 2.41 V, mean 1.2 V |
| Triangle harmonics | 3rd −19.1 dB, 5th −28 dB, THD ≈ 12 % |
| Sallen–Key | f_c = 10.7 kHz, Q = 0.74, −72 dB at 692 kHz |
| Attenuator (R5 + RV2 ∥ 50 kΩ LM386 input) | 1:13 → 0.19 V p-p into the LM386 at full volume |
| LM386 | Gain 20, ≈3.6 V p-p maximum at 5 V |
| Speaker coupling | 220 µF → 90 Hz corner |

**Why the inverter (U1D) is needed:** the NAND output averages between 2.59 V and 5 V, which is above the MCP602's input limit of V_DD − 1.2 = 3.8 V. The AND form (after inversion) sits at 0–2.41 V instead.

---

## 6. SPICE verification log

The netlist `spice/full.cir` models the whole circuit, from antenna to speaker, using behavioural models in `spice/models.inc`.

| Quantity | Analysis | SPICE |
|---|---|---|
| f_B | 692.1 kHz | 692.2 kHz |
| f_A @ RV1 = 0 / 2 k / 4.16 k | 941.6 / 800.1 / 690.8 kHz | 941.3 / 799.8 / 690.6 kHz |
| Beat @ RV1 = 4152.6 Ω | 1.00 kHz | 1.00 kHz |
| U2A output | 0–2.41 V, mean 1.20 V | 0.02–2.39 V, mean 1.16 V |
| Speaker, full volume | ≤ 3.6 V p-p | 2.7 V p-p |

**Simulation pitfalls hit along the way** (worth knowing if you re-run it):

1. **Time-step quantisation hides the beat.** A 1 kHz beat is only about 2 ns of phase drift per carrier cycle. Hard `u()` comparators snap edges to the time grid, so use smooth `tanh` comparators with a maximum step of 0.5 ns.
2. **Op-amp integrator windup.** A saturated macromodel took milliseconds to recover. Clamp its internal node (`Gcl` in `models.inc`).
3. **Initial conditions.** Starting an oscillator exactly at its threshold leaves it stuck until noise kicks it. Start it at 1 V instead.

These were all modelling artifacts, not circuit problems.

---

## 7. Bench-measurement checklist (to strengthen Section VI)

With an oscilloscope and multimeter, about 20 minutes:

- [ ] U1 pin 4 (reference) frequency. Expect ~600–800 kHz; it varies from chip to chip.
- [ ] U1 pin 3 frequency with no hand, then with a hand at 5, 10, 15, 20 and 25 cm. Record the beat (U2A pin 1) at each distance.
- [ ] U2A pin 1 waveform. It should be a triangle, 0 to ~2.4 V.
- [ ] Supply current at idle and while playing (multimeter in series with the battery).
- [ ] Any "dead zone" (silence) near zero beat, and how wide it is.

Put the distance–frequency data into Fig. 3(a) to replace the calibrated model with real measurements.

---

## 8. Tuning procedure

1. Switch on with your hands at least 50 cm from the antenna.
2. Turn RV1 slowly until the tone sweeps down through zero beat (a low growl, then silence).
3. Keep turning a few degrees in the direction where an approaching hand makes the pitch **rise**, and stop at the base note you want.
4. Set the level with RV2.

## 9. Future work

- Multi-turn trimmer or varactor for fine pitch tuning (the current pot is coarse at 1.6 kHz per degree)
- A second antenna for volume control
- A low-dropout regulator (the 7805 wastes about 44 % of the battery power)
- A PCB with a guarded antenna trace and short supply leads

## 10. References (all verified)

1. L. S. Theremin, US Patent 1,661,058 (1928). Verified on Google Patents: filed 5 Dec 1925, granted 28 Feb 1928.
2. Skeldon et al., "Physics of the Theremin," *Am. J. Phys.* 66(11), 945–955 (1998).
3. R. A. Moog, "A Transistorized Theremin," *Electronics World*, Jan. 1961 (Moog Foundation archive).
4. Datasheets: TI CD4093B, Microchip MCP601/2/3/4 (DS21314), TI LM386, TI LM340/LM7805 (`lm7800.pdf`).
5. Sallen & Key, *IRE Trans. Circuit Theory* CT-2 (1955); Adler, *Proc. IRE* 34 (1946).
