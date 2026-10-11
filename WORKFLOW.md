# ميتوكوندريا | Mito Science — daily short workflow

Page: TikTok / Instagram / YouTube, all `@mito.science`. Owner is a biochemistry & pharmacy specialist.
Topic focus: recent, peer-reviewed research that is NEW and SURPRISING ("جديد وغريب") across:
- medicine and new drugs/pharmacology (mechanisms, unexpected effects, repurposed drugs)
- food and nutrition (surprising findings about common foods, supplements, diets)
- public health
- everyday human habits and practices (sleep, exercise, screens, coffee, cooking, hygiene…)
- biochemistry & metabolism, weight loss and bodybuilding (the original core)
Pick studies that grab the general public AND are interesting to specialists (doctors, pharmacists, nutritionists, students): a counter-intuitive result, a new mechanism, or a finding that changes daily practice. Prefer strong designs; flag weak ones.
Language: Iraqi Arabic, simple, accurate. Always cite the study on screen and in the caption. Educational, never medical advice; no dosing instructions.

## Step 1 — propose studies (do NOT build anything yet)
- Search for 3–4 studies published in the last ~60 days in peer-reviewed journals (PubMed, Nature, Cell, Lancet, JAMA, NEJM, BMJ, AJCN, Cell Metabolism, Obesity…). Prefer human RCTs/meta-analyses; flag animal or tiny studies clearly.
- Skip topics already covered (see `published.md`).
- Mix categories across the options (e.g. one drug, one food/nutrition, one daily habit/public health, one metabolism/fitness) so the owner gets variety.
- Present each option: title, journal + date, design & sample size, the one-line hook, why it fits the page, and caveats. Ask the owner to pick one. Wait for the choice.

## Step 2 — script (after the owner picks)
- 30–45 s total (NOT longer — first Reel averaged only 3.8 s watch time on a 68 s video). ~6–8 numbered segments, one idea per segment (each segment = one scene).
- Segment 1 = the hook: open with the surprising RESULT itself as a bold claim (e.g. "أوزمبيك ما ياكل عضلاتك… بس بشرط"), not a generic question. Max ~2.5 s.
- Second-to-last segment: a question to the audience to drive comments (e.g. "تاخذ GLP-1؟ اكتب بالتعليقات").
- Write numbers as spoken words. End with: "تابعوا ميتوكوندريا."
- Tell the owner: leave ~1 s silence between segments; on a mistake pause 3 s and redo the whole segment; record in iPhone Voice Memos (Lossless) + Enhance Recording.

## Step 3 — visuals
- Frame 1 must already show the hook text and a strong visual (no fade-in on the first scene; use t_in=-1 as in the template).
- Copy `tools/example_glp1_video.py` to a new file and rewrite the scenes for the new study (same style: dark navy, teal/lime/gold, Cairo font, animated bars for numbers, source line on number scenes, avatar outro).
- Render stills first and look at them (check RTL text, overlaps), then send a silent preview if useful.

## Step 4 — voice + music (after the owner sends the recording)
- Detect pauses with ffmpeg `silencedetect` to find segment starts; map scene anchors with `OLD_ANCHORS` / `SCENE_BOUNDS` env vars (see the script's `warp`).
- Music: `python3 tools/make_music.py music.wav <duration>` (original synthesized track, no copyright).
- Voice chain: highpass 80, lowpass 12k, afftdn, compressor, loudnorm I=-16; music ducked under voice with sidechaincompress; alimiter.
- Send the final video for approval.

## Step 5 — publish (only after the owner says "انشر")
- Commit the mp4 to `videos/YYYY-MM-DD-slug.mp4` and push to `main`.
- Schedule with Metricool (brand blogId 7350660, timezone Asia/Baghdad), default 7:00 PM, providers instagram (REEL) + youtube (short, SCIENCE_TECHNOLOGY, not made for kids).
  Media URL: `https://raw.githubusercontent.com/mitoscienceiq/mito-science-media/<commit-sha>/videos/<file>.mp4`. (When TikTok is re-enabled later, it needs `tiktokData.title`.)
- Also put the audience question in the caption.
- TikTok: account is restricted after a spam flag (Oct 2026). Do NOT schedule TikTok via Metricool and never operate the TikTok account from a browser. Send the owner the final mp4 + caption to upload manually from the TikTok iPhone app once the restriction is lifted.
- Append the topic to `published.md`.

## Step 6 — learn from results
- Before proposing new studies, pull Metricool analytics for the previous posts (Instagram reels: views IGRE23, reach IGRE11, avg watch time IGRE24, view rate IGRE28, likes/comments/saves/shares; YouTube published-in-range: YTVP06/08/09/11/12 — YouTube data lags 24–48 h).
- Give the owner a 3-line summary and adjust hooks/length accordingly.
