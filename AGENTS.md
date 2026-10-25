# AGENTS.md

## Communication Preferences
- Keep all user-facing output extremely concise, including progress updates.
- Prefer short bullet points and compact comparison tables or quick charts.
- Give the conclusion first; expand only when explicitly requested or necessary.

## Golden Goal
Turn a user-provided character image into testable walking, running, jumping,
or dancing videos.

## Decision Rule
The Golden Goal takes precedence over historical roadmaps, model choices, and
motion-source choices. Mixamo, Wan-Animate, and RTMPose are optional tools, not
product requirements.

## Current Increment
Prove a Mac-only vertical slice first:

`character image + action prompt -> MLX image-to-video -> playable MP4`

Then improve movement quality and add optional exact driver-video control.

## Working Rules
- Work incrementally and verify each vertical slice with a playable artifact.
- Preserve useful experiments and the existing CUDA Wan integration.
- Keep large models, user assets, generated outputs, and virtual environments ignored.
- Keep production code under `src/dancing_angels_ai/`.
- Do not treat roadmap completion as product completion.
- Use the user's `assets/woman-1.png` for new character tests. Preserve `man.png` and its past results only as historical evidence.
- Before new Step 3 generations, read `docs/internal/woman-1-handoff.md`: portrait framing and transparency need preparation. Do not assume vector-brush origin improves video quality.

## Roadmap Updates
- When updating a roadmap, move the superseded image into `roadmaps-ideas/archive/`.
- Add sequential letter suffixes within each roadmap version: `v5A`, `v5B`, `v5C`, and so on.
- Keep `roadmaps-ideas/roadmap/` visual and minimal: only the current roadmap image. Keep the current website reference at `roadmaps-ideas/golden-image-v4.png`.
- Store design comparison sheets and exploratory artwork in `design/concepts/`.
- Store technical status, evidence, and planning notes in `docs/internal/`; keep superseded notes in `docs/internal/archive/`.
- Update related internal status and evidence files whenever the roadmap changes. Do not add Markdown notes or technical reports to the user-facing roadmap folder.
