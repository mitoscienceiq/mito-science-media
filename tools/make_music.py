"""Original royalty-free lo-fi/ambient background track, synthesized from scratch."""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 53.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/video/music.wav"
BPM = 88
beat = 60 / BPM
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(3)

def midi(m): return 440 * 2 ** ((m - 69) / 12)
def lp(x, fc, order=2): b, a = butter(order, fc / (SR / 2), "low"); return lfilter(b, a, x)
def hp(x, fc, order=2): b, a = butter(order, fc / (SR / 2), "high"); return lfilter(b, a, x)

# Am – F – C – G, one chord per bar (4 beats)
chords = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
bass = [45, 41, 48, 43]
bar = 4 * beat

pad = np.zeros(N); bs = np.zeros(N); arp = np.zeros(N); kick = np.zeros(N); hat = np.zeros(N); snare = np.zeros(N)

nbars = int(np.ceil(DUR / bar))
for b in range(nbars):
    ch = chords[b % 4]; s0 = int(b * bar * SR); s1 = min(N, int((b + 1) * bar * SR))
    if s0 >= N: break
    tt = np.arange(s1 - s0) / SR
    env = np.minimum(1, tt / 0.6) * np.minimum(1, (bar - tt) / 0.4)
    for m in ch:
        f = midi(m)
        tone = sum(np.sin(2 * np.pi * f * k * tt + rng.uniform(0, 6)) / k ** 1.6 for k in range(1, 5))
        tone *= 1 + 0.004 * np.sin(2 * np.pi * 0.3 * tt)  # gentle movement
        pad[s0:s1] += tone * env * 0.12
    fb = midi(bass[b % 4])
    benv = np.minimum(1, tt / 0.02) * np.exp(-tt * 0.9)
    bs[s0:s1] += (np.sin(2 * np.pi * fb * tt) + 0.3 * np.sin(2 * np.pi * 2 * fb * tt)) * benv * 0.35
    # arpeggio in 8ths, an octave up
    for i in range(8):
        a0 = s0 + int(i * beat / 2 * SR); a1 = min(N, a0 + int(beat / 2 * SR * 1.6))
        if a0 >= N: break
        ta = np.arange(a1 - a0) / SR
        m = ch[[0, 1, 2, 3, 2, 1, 2, 3][i]] + 12
        arp[a0:a1] += np.sin(2 * np.pi * midi(m) * ta) * np.exp(-ta * 6) * 0.10

nbeats = int(DUR / beat) + 1
for i in range(nbeats):
    s0 = int(i * beat * SR)
    if s0 >= N: break
    # kick on 1 and 3, soft snare on 2 and 4
    L = min(N - s0, int(0.35 * SR)); tk = np.arange(L) / SR
    if i % 2 == 0:
        f = 110 * np.exp(-tk * 25) + 45
        kick[s0:s0 + L] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tk * 9) * 0.55
    else:
        nz = rng.standard_normal(L) * np.exp(-tk * 18)
        snare[s0:s0 + L] += nz * 0.10
    for h in (0, 0.5):  # hats on 8ths
        h0 = s0 + int(h * beat * SR); Lh = min(N - h0, int(0.06 * SR))
        if Lh > 0:
            th = np.arange(Lh) / SR
            hat[h0:h0 + Lh] += rng.standard_normal(Lh) * np.exp(-th * 70) * (0.06 if h == 0 else 0.04)

pad = lp(pad, 2200); arp = lp(arp, 4000); hat = hp(hat, 6000); snare = lp(hp(snare, 1200), 6000)
mix = pad + bs + arp + kick + snare + hat
# drums enter after the hook (first 2 bars softer)
intro = np.clip(t / (2 * bar), 0, 1)
mix = pad + arp + bs * (0.4 + 0.6 * intro) + (kick + snare + hat) * intro
# vinyl-ish noise bed
mix += lp(rng.standard_normal(N), 3000) * 0.004
# fades
mix *= np.minimum(1, t / 1.0) * np.minimum(1, (DUR - t) / 2.0)
mix = np.tanh(mix * 1.2)
mix = mix / np.max(np.abs(mix)) * 0.5  # leave headroom; ~-6 dBFS peak
stereo = np.stack([mix, np.roll(mix, int(0.012 * SR))], axis=1)
wavfile.write(OUT, SR, (stereo * 32767).astype(np.int16))
print("wrote", OUT)
