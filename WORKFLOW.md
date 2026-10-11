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
- 45–60 s, hook in the first 3 s, ~9 numbered segments, one idea per segment (each segment = one scene).
- Write numbers as spoken words. End with: "تابعوا ميتوكوندريا."
- Tell the owner: leave ~1 s silence between segments; on a mistake pause 3 s and redo the whole segment; record in iPhone Voice Memos (Lossless) + Enhance Recording.

## Step 3 — visuals
- Copy `tools/example_glp1_video.py` to a new file and rewrite the scenes for the new study (same style: dark navy, teal/lime/gold, Cairo font, animated bars for numbers, source line on number scenes, avatar outro).
- Render stills first and look at them (check RTL text, overlaps), then send a silent preview if useful.

## Step 4 — voice + music (after the owner sends the recording)
- Detect pauses with ffmpeg `silencedetect` to find segment starts; map scene anchors with `OLD_ANCHORS` / `SCENE_BOUNDS` env vars (see the script's `warp`).
- Music: `python3 tools/make_music.py music.wav <duration>` (original synthesized track, no copyright).
- Voice chain: highpass 80, lowpass 12k, afftdn, compressor, loudnorm I=-16; music ducked under voice with sidechaincompress; alimiter.
- Send the final video for approval.

## Step 5 — publish (only after the owner says "انشر")
- Commit the mp4 to `videos/YYYY-MM-DD-slug.mp4` and push to `main`.
- Schedule with Metricool (brand blogId 7350660, timezone Asia/Baghdad), default 7:00 PM, providers tiktok + instagram (REEL) + youtube (short, SCIENCE_TECHNOLOGY, not made for kids).
  Media URL: `https://raw.githubusercontent.com/mitoscienceiq/mito-science-media/<commit-sha>/videos/<file>.mp4`. TikTok needs `tiktokData.title`.
- Append the topic to `published.md`.
