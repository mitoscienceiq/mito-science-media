"""Vertical 1080x1920 short: GLP-1 & muscle (Langer et al., Cell Reports Medicine 2026)."""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FONT = "assets/Cairo.ttf"
AVATAR = "assets/mito_avatar.png"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/video/glp1_muscle.mp4"

BG1, BG2 = (10, 23, 38), (22, 50, 74)
TEAL, LIME, GOLD, CORAL, WHITE, MUTED = (46, 205, 190), (182, 255, 92), (255, 209, 102), (255, 120, 110), (245, 248, 250), (150, 175, 195)

_fc = {}
def font(size, weight="Bold"):
    k = (size, weight)
    if k not in _fc:
        f = ImageFont.truetype(FONT, size); f.set_variation_by_name(weight); _fc[k] = f
    return _fc[k]

def ease(t):  # easeOutBack-ish clamp
    t = max(0.0, min(1.0, t)); c = 1.4
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

def lin(t): return max(0.0, min(1.0, t))

def text_img(txt, size, color=WHITE, weight="Bold", max_w=940, align="center", spacing=14):
    f = font(size, weight)
    # wrap RTL text word by word
    words, lines, cur = txt.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.getlength(trial, direction="rtl", language="ar") <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    lh = int(size * 1.45)
    img = Image.new("RGBA", (max_w + 40, lh * len(lines) + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        lw = f.getlength(ln, direction="rtl", language="ar")
        x = (img.width - lw) / 2 if align == "center" else img.width - lw - 20
        d.text((x, 10 + i * lh), ln, font=f, fill=color, direction="rtl", language="ar")
    return img

def ltr_img(txt, size, color=WHITE, weight="Bold"):
    f = font(size, weight)
    w = int(f.getlength(txt)) + 20
    img = Image.new("RGBA", (w, int(size * 1.5)), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((10, 0), txt, font=f, fill=color)
    return img

def with_alpha(img, a):
    if a >= 1: return img
    im = img.copy(); al = im.getchannel("A").point(lambda v: int(v * max(0, a))); im.putalpha(al); return im

def place(frame, img, cx, cy, t_in, t, scale_anim=True, fade_out_at=None, dur=0.45):
    p = (t - t_in) / dur
    if p <= 0: return
    a = lin(p)
    if fade_out_at is not None and t > fade_out_at: a *= lin(1 - (t - fade_out_at) / 0.3)
    if a <= 0: return
    s = ease(p) if scale_anim else 1
    s = max(0.01, 0.6 + 0.4 * s) if scale_anim else 1
    im = img if s == 1 else img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
    dy = 0 if scale_anim else int((1 - ease(p)) * 40)
    frame.alpha_composite(with_alpha(im, a), (int(cx - im.width / 2), int(cy - im.height / 2 + dy)))

# ---------- background ----------
def make_bg():
    bg = Image.new("RGB", (W, H), BG1); d = ImageDraw.Draw(bg)
    for r in range(1400, 0, -10):
        t = r / 1400; col = tuple(int(BG2[i] * (1 - t) + BG1[i] * t) for i in range(3))
        d.ellipse([W / 2 - r, H * 0.42 - r, W / 2 + r, H * 0.42 + r], fill=col)
    return bg.convert("RGBA")
BG = make_bg()

# floating particles
import random; random.seed(7)
PARTS = [(random.uniform(0, W), random.uniform(0, H), random.uniform(3, 7), random.uniform(10, 30), random.uniform(0, 6.28)) for _ in range(40)]
def particles(frame, t):
    d = ImageDraw.Draw(frame)
    for x, y, r, sp, ph in PARTS:
        yy = (y - t * sp) % H; xx = x + 12 * math.sin(t * 0.6 + ph)
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(46, 205, 190, 40))

def mito_icon(size):
    S = 4; w = size * S; im = Image.new("RGBA", (w, w), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    k = w / 1080
    d.rounded_rectangle([215 * k, 365 * k, 865 * k, 715 * k], radius=175 * k, fill=TEAL)
    d.rounded_rectangle([250 * k, 400 * k, 830 * k, 680 * k], radius=140 * k, fill=(12, 70, 86))
    pts = [((300 + i) * k, (540 - 95 * math.sin(i / 60 * math.pi)) * k) for i in range(481)]
    d.line(pts, fill=LIME, width=int(30 * k), joint="curve")
    im = im.rotate(30, resample=Image.BICUBIC)
    return im.resize((size, size), Image.LANCZOS)

# progress bar + watermark
WM = ltr_img("@mito.science", 34, MUTED, "SemiBold")
def chrome(frame, t, total):
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([60, 70, W - 60, 80], radius=5, fill=(255, 255, 255, 40))
    d.rounded_rectangle([60, 70, 60 + (W - 120) * t / total, 80], radius=5, fill=TEAL)
    frame.alpha_composite(WM, (W - WM.width - 50, 100))

SRC = text_img("المصدر: Langer et al., Cell Reports Medicine (2026)", 30, MUTED, "Medium", max_w=980)

# ---------- scenes ----------
scenes = []
def scene(start, end):
    def deco(fn): scenes.append((start, end, fn)); return fn
    return deco

# 1 Hook
h1 = text_img("تاخذ إبر أوزمبيك أو مونجارو؟", 92, WHITE, "Black")
h2 = text_img("وخايف تخسر عضلاتك؟", 100, GOLD, "Black")
syr = None
@scene(0, 4.2)
def s1(f, t):
    place(f, h1, W / 2, 640, -1, t, fade_out_at=3.9)  # hook visible on frame 1
    place(f, h2, W / 2, 950, -1, t, fade_out_at=3.9)
    s = 1 + 0.06 * math.sin(t * 6)
    big = text_img("؟", 260, CORAL, "Black")
    place(f, big.resize((int(big.width * s), int(big.height * s))), W / 2, 1250, -1, t, fade_out_at=3.9)

# 2 context
c1 = text_img("أدوية GLP-1 مثل سيماغلوتايد", 76, WHITE, "Bold")
c2 = text_img("تنزّل الوزن بقوة", 90, LIME, "Black")
c3 = text_img("بس شگد من الوزن النازل… عضلات؟", 72, WHITE, "Bold")
@scene(4.2, 10)
def s2(f, t):
    place(f, c1, W / 2, 600, 4.3, t, fade_out_at=9.7)
    place(f, c2, W / 2, 820, 4.9, t, fade_out_at=9.7)
    place(f, c3, W / 2, 1100, 6.4, t, fade_out_at=9.7)

# 3 study card
st1 = text_img("دراسة جديدة 2026", 96, GOLD, "Black")
st2 = ltr_img("Cell Reports Medicine", 70, WHITE, "Bold")
st3 = text_img("تجارب على فئران + بشر", 66, WHITE, "SemiBold")
@scene(10, 15)
def s3(f, t):
    place(f, st1, W / 2, 600, 10.1, t, fade_out_at=14.7)
    p = lin((t - 10.6) / 0.4)
    if p > 0:
        card = Image.new("RGBA", (900, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
        d.rounded_rectangle([0, 0, 899, 199], radius=36, fill=(255, 255, 255, 22), outline=TEAL, width=4)
        card.alpha_composite(st2, ((900 - st2.width) // 2, 50))
        place(f, card, W / 2, 830, 10.6, t, fade_out_at=14.7)
    place(f, st3, W / 2, 1060, 11.4, t, fade_out_at=14.7)

def hbar(f, y, label, pct, color, t0, t, maxpct=50, fade=None):
    a = lin((t - t0) / 0.4)
    if fade and t > fade: a *= lin(1 - (t - fade) / 0.3)
    if a <= 0: return
    lab = text_img(label, 58, WHITE, "Bold", max_w=900)
    f.alpha_composite(with_alpha(lab, a), ((W - lab.width) // 2, y - 110))
    prog = lin((t - t0 - 0.2) / 1.2); prog = 1 - (1 - prog) ** 3
    x0, x1 = 300, W - 90; full = x1 - x0
    d = ImageDraw.Draw(f)
    d.rounded_rectangle([x0, y, x1, y + 70], radius=35, fill=(255, 255, 255, int(30 * a)))
    wbar = max(70, full * (pct / maxpct) * prog)
    d.rounded_rectangle([x1 - wbar, y, x1, y + 70], radius=35, fill=color + (int(255 * a),))
    num = ltr_img(f"-{pct * prog:.0f}%", 64, color, "Black")
    f.alpha_composite(with_alpha(num, a), (int(x0 - num.width - 20), y - 10))

# 4 mice
m1 = text_img("بالفئران: سيماغلوتايد 28 يوم", 64, GOLD, "Black")
m3 = text_img("وقوة القبضة نسبةً للوزن تحسنت", 62, LIME, "Bold")
@scene(15, 23)
def s4(f, t):
    place(f, m1, W / 2, 480, 15.1, t, fade_out_at=22.7)
    hbar(f, 760, "الدهون", 46, CORAL, 15.7, t, fade=22.7)
    hbar(f, 1010, "الكتلة غير الدهنية", 4, TEAL, 16.6, t, fade=22.7)
    place(f, m3, W / 2, 1230, 18.6, t, fade_out_at=22.7)
    if t > 15.4: f.alpha_composite(with_alpha(SRC, lin((t - 15.4) / 0.4) * (lin(1 - (t - 22.7) / 0.3) if t > 22.7 else 1)), ((W - SRC.width) // 2, 1440))

# 5 humans – stacked bar
u1 = text_img("بالبشر: 12 أسبوع", 80, GOLD, "Black")
u2 = text_img("من الوزن النازل:", 60, WHITE, "SemiBold")
u3 = text_img("وقوة العضلات ما نقصت", 72, LIME, "Black")
lf = text_img("دهون", 48, WHITE, "Black", max_w=300)
ll = text_img("غير دهنية", 40, MUTED, "Black", max_w=300)
@scene(23, 31)
def s5(f, t):
    place(f, u1, W / 2, 480, 23.1, t, fade_out_at=30.7)
    place(f, u2, W / 2, 640, 23.6, t, fade_out_at=30.7)
    a = lin((t - 24.0) / 0.4) * (lin(1 - (t - 30.7) / 0.3) if t > 30.7 else 1)
    if a > 0:
        prog = 1 - (1 - lin((t - 24.2) / 1.4)) ** 3
        x0, x1, y0, y1 = 90, W - 90, 760, 900; full = x1 - x0
        d = ImageDraw.Draw(f)
        d.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=(255, 255, 255, int(30 * a)))
        fat_w = full * 0.70 * prog; lean_w = full * 0.30 * prog
        d.rounded_rectangle([x1 - fat_w, y0, x1, y1], radius=30, fill=CORAL + (int(255 * a),))
        if lean_w > 40: d.rounded_rectangle([x1 - fat_w - lean_w, y0, x1 - fat_w + 30, y1], radius=30, fill=TEAL + (int(255 * a),))
        if prog > 0.9:
            n1 = ltr_img("70%", 72, WHITE, "Black"); n2 = ltr_img("30%", 56, WHITE, "Black")
            f.alpha_composite(with_alpha(n1, a), (int(x1 - fat_w / 2 - n1.width / 2), y0 + 18))
            f.alpha_composite(with_alpha(n2, a), (int(x1 - fat_w - lean_w / 2 - n2.width / 2), y0 + 30))
            f.alpha_composite(with_alpha(lf, a), (int(x1 - fat_w / 2 - lf.width / 2), y1 + 10))
            f.alpha_composite(with_alpha(ll, a), (int(x1 - fat_w - lean_w / 2 - ll.width / 2), y1 + 16))
    place(f, u3, W / 2, 1170, 26.4, t, fade_out_at=30.7)
    if t > 23.4: f.alpha_composite(with_alpha(SRC, lin((t - 23.4) / 0.4) * (lin(1 - (t - 30.7) / 0.3) if t > 30.7 else 1)), ((W - SRC.width) // 2, 1440))

# 6 why
w1 = text_img("والسبب؟", 110, GOLD, "Black")
w2 = text_img("قلة الأكل نفسها… مو الدواء", 80, WHITE, "Black")
w3 = text_img("فئران أكلت نفس السعرات بدون دواء خسرت نفس العضلات تقريباً", 58, MUTED, "SemiBold")
@scene(31, 37)
def s6(f, t):
    place(f, w1, W / 2, 580, 31.1, t, fade_out_at=36.7)
    place(f, w2, W / 2, 790, 31.9, t, fade_out_at=36.7)
    place(f, w3, W / 2, 1040, 33.0, t, scale_anim=False, fade_out_at=36.7)

# 7 mito bonus
ICON = mito_icon(420)
b1 = text_img("وبونص 😉".replace("😉", ""), 90, GOLD, "Black")
b2 = text_img("الدواء زاد بروتينات الميتوكوندريا بالعضلة", 70, WHITE, "Black")
@scene(37, 41.5)
def s7(f, t):
    place(f, b1, W / 2, 470, 37.1, t, fade_out_at=41.2)
    ic = ICON.rotate(6 * math.sin(t * 2.5), resample=Image.BICUBIC)
    place(f, ic, W / 2, 800, 37.4, t, fade_out_at=41.2)
    place(f, b2, W / 2, 1120, 38.0, t, fade_out_at=41.2)

# 8 caveat + takeaway
k1 = text_img("انتبه: الجزء البشري كان 10 مرضى بس", 64, CORAL, "Black")
k2 = text_img("الخلاصة إذا تاخذ GLP-1:", 70, GOLD, "Black")
k3 = text_img("• بروتين كافي", 76, WHITE, "Black")
k4 = text_img("• تمارين مقاومة", 76, WHITE, "Black")
k5 = text_img("• وكلشي بإشراف طبيبك", 76, WHITE, "Black")
@scene(41.5, 48)
def s8(f, t):
    place(f, k1, W / 2, 470, 41.6, t, fade_out_at=47.7)
    place(f, k2, W / 2, 700, 42.8, t, fade_out_at=47.7)
    place(f, k3, W / 2, 870, 43.6, t, scale_anim=False, fade_out_at=47.7)
    place(f, k4, W / 2, 1000, 44.3, t, scale_anim=False, fade_out_at=47.7)
    place(f, k5, W / 2, 1130, 45.0, t, scale_anim=False, fade_out_at=47.7)

# 9 outro
av = Image.open(AVATAR).convert("RGBA").resize((520, 520), Image.LANCZOS)
mk = Image.new("L", av.size, 0); ImageDraw.Draw(mk).ellipse([0, 0, 519, 519], fill=255); av.putalpha(mk)
o1 = text_img("تابع ميتوكوندريا", 96, WHITE, "Black")
o2 = ltr_img("@mito.science", 64, TEAL, "Bold")
o3 = text_img("أبحاث البايوكيمستري والصيدلة… مبسّطة", 52, MUTED, "SemiBold")
o4 = text_img("محتوى تعليمي، مو نصيحة طبية", 40, MUTED, "Medium")
@scene(48, 53)
def s9(f, t):
    place(f, av, W / 2, 700, 48.1, t)
    place(f, o1, W / 2, 1060, 48.6, t)
    place(f, o2, W / 2, 1180, 49.0, t)
    place(f, o3, W / 2, 1290, 49.4, t, scale_anim=False)
    place(f, o4, W / 2, 1400, 49.8, t, scale_anim=False)

TOTAL = 53.0
OLD_B = [0, 4.2, 10, 15, 23, 31, 37, 41.5, 48, 53.0]
import os, json
NEW_B = json.loads(os.environ["SCENE_BOUNDS"]) if os.environ.get("SCENE_BOUNDS") else OLD_B
if os.environ.get("OLD_ANCHORS"): OLD_B = json.loads(os.environ["OLD_ANCHORS"])
assert len(OLD_B) == len(NEW_B)
OUT_TOTAL = NEW_B[-1]

def warp(nt):
    for i in range(len(NEW_B) - 1):
        a, b = NEW_B[i], NEW_B[i + 1]
        if nt < b or i == len(NEW_B) - 2:
            return OLD_B[i] + (OLD_B[i + 1] - OLD_B[i]) * min(1.0, (nt - a) / (b - a))
    return OLD_B[-1]

def render(nt):
    t = warp(nt)
    f = BG.copy(); particles(f, nt)
    for s, e, fn in scenes:
        if s <= t < e + 0.05: fn(f, t)
    chrome(f, nt, OUT_TOTAL)
    return f.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "stills":
        for tt in [2.5, 8, 13, 20, 28, 35, 40, 46, 51]:
            render(tt).save(f"/home/claude/video/still_{tt:04.1f}.png")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT],
                         stdin=subprocess.PIPE)
    n = int(OUT_TOTAL * FPS)
    for i in range(n):
        p.stdin.write(render(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("done", OUT)
