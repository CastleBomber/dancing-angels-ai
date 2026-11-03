# Step 3 direction — three basic movements, 2026-11-02

User-requested planning change: establish **walk → run → jump** before returning
to dance or following a saved reference animation such as Mixamo. This updates
the current acceptance target prospectively; it does not regrade historical
Shuffle experiments or claim new quality evidence.

## Current evidence and prerequisite

-3A input passed for the prepared woman reference and tested upload path.
- Historical Shuffle videos remain below target (4/10 for the prepared woman).
- Q8 conversion passed; its visual quality remains untested. Both October28
  launches stopped at the recorded memory guard during text encoding.
- Resolve/measure text-encoding memory use before further local video tests.
  A simpler action prompt does not by itself remove that memory requirement.
- All three basic movements are **untested**.3B and3C are not passed.

## Three basic movements

Use the prepared `assets/woman-1.png` character, full body and feet visible,
fixed camera, stable appearance. Test each action separately and sequentially.

| Order | Action | Recognizable motion required for score2 | Status |
|---|---|---|---|
|1|Walk in place|Repeated alternating steps, coherent weight shifts and foot contact|Untested; first target|
|2|Run in place|Repeated running strides, opposed arm/leg swing and a visible flight phase|Untested; after walking|
|3|Jump in place|Clear preparation, both feet leave the ground, controlled landing|Untested; after running|

Before generation, save the exact action prompt, settings, seed, model, input
hashes, budget and action-specific acceptance criteria. Preserve existing models
and all previous experiments. New walking results cannot be treated as a
single-variable quantization comparison against the historical Shuffle prompt.
If comparing Q4/Q8, hold the selected action prompt and all other variables fixed.

Retain the five-category0–2 rubric:identity, anatomy, framing, continuity,
and **requested action**. Replace the Shuffle-specific final category only for
new basic-movement trials. Require total≥8/10, no zeros, requested-action2 for
**each** movement before3B is complete under this revised scope. Passing walking
alone is a milestone, not completion of all3B. Verify all-frame decoding and
browser playback separately from visual quality. Record limits of agent review.
3C remains repeatability across fixed seeds and different character images; one
passing clip per action does not establish robustness or arbitrary-image support.

## Later: following a reference movement

Plain-language goal: choose a saved movement and have the user's character follow
it. Mixamo is an optional source for that movement, not needed for the initial
image-plus-action tests. Later workflow:

1. Select and save the desired animation with a unique local label and preview;
   duplicate display names are insufficient to identify a motion.
2. Prepare a playable reference clip from that saved animation if needed.
3. Evaluate a compatible motion-controlled animation workflow that can accept
   the character image and reference clip, then compare motion fidelity.

The current prompt-only MLX path does not consume Mixamo animation files or
reference videos. Supporting those inputs requires later compatibility and
implementation work; no direct Mixamo integration or exact-motion capability is
claimed. Do not require Mixamo, Wan-Animate or RTMPose to meet the Golden Goal.

## Roadmap and application boundaries

V5L adds the dedicated three-movement section and later reference-animation panel.
Steps1,2,4 retain their existing completed milestones; API completion refers to
its previously verified diagnostic flow, not new walk/run/jump presets. Steps5–8
remain planned. Website action choices and API presets will be updated in later
implementation work. Current website reference remains `roadmaps-ideas/golden-image-v5.png`.

This request changes planning/status/visuals only: no new video generation, model
change, application code, API/website integration or GitHub deployment. V5K and
its image prompt are archived. Previous evidence remains intact; handoff and
status link this new direction.

Related: [Q8 evidence](roadmap-v5-step3b-q8-evidence.md),
[current status](roadmap-v5-status.md), [input handoff](woman-1-handoff.md).
