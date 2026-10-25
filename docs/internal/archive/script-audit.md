# Script Audit

Roadmap V3 Step 1: audit existing project before refactoring.

## Verdict Key

- **Keep**: useful prototype evidence; preserve.
- **Fix**: useful, but needs cleanup before v2.
- **Legacy**: old backend/path; preserve as reference only.
- **Delete later**: likely removable after confirming no unique value.

## Scripts And Runtime Files

| File | Roadmap Role | Verdict | Why | Next Action |
|---|---|---|---|---|
| `experiments/pose/test_skeleton.py` | Steps 1-2: pose detection / pose map | Keep | Verified locally; produces overlay + pose condition image. | Refactor pose detection into `src/angels_ai/pose/`. |
| `experiments/pose/test_walk_cycle.py` | Old Step 3: basic procedural walk | Legacy | Superseded by `test_walk_cycle_v2.py`. | Keep until v2 procedural fallback exists. |
| `experiments/pose/test_walk_cycle_v2.py` | Step 3.5: better procedural motion | Keep | Verified locally; useful fallback/test motion. | Refactor as optional procedural `MotionSource`. |
| `experiments/pose/test_motion_video.py` | V3 Steps 3-4: Mixamo/Blender MP4 -> pose motion | Keep | Verified prototype refactored into `angels_ai.pose.RTMPoseVideoPreprocessor`. | Preserve as reference. |
| `experiments/legacy_sdxl/test_sdxl_controlnet_one.py` | Old Step 4: single SDXL frame | Legacy | Old backend; useful only as generation-history evidence. | Preserved; do not extend. |
| `experiments/legacy_sdxl/test_sdxl_controlnet_sequence.py` | Old Step 5: SDXL frame sequence | Legacy | Old backend replaced by Wan-Animate target. | Preserved; do not extend. |
| `experiments/archive/test_openpose_condition.py` | Old OpenPose conditioning attempt | Delete later | Marked unnecessary and contains a syntax error. | Delete after confirming no unique notes are needed. |
| `experiments/archive/tmp.py` | None | Delete later | Empty scratch file. | Delete later. |
| `experiments/current_commands.txt` | Command notes | Keep | Historical commands now point to the preserved experiment paths. | Keep with experiment documentation. |
| `experiments/legacy_sdxl/app/pose/pose_engine.py` | Old app integration | Legacy | Outdated; eager SDXL load, missing `ImageDraw` import, not aligned with V3. | Rebuild around v2 modules later. |
| `experiments/legacy_sdxl/app/diffusion/sd_engine.py` | Old SDXL backend | Legacy | SDXL + ControlNet is no longer preferred backend. | Preserved as backend reference. |
| `experiments/legacy_sdxl/main.py` | Old chat entrypoint | Legacy | Tied to outdated `PoseEngine`; uses older LangChain chat path. | Replace after clean v2 pipeline exists. |

## Support File Fixes

| File / Area | Verdict | Why | Next Action |
|---|---|---|---|
| `requirements.txt` | Keep | Includes the dependencies used by current prototypes. | Split production and legacy dependencies when Wan-Animate is integrated. |
| `.gitignore` / tracked files | Fix | Assets, outputs, tests, and `.venv` appear tracked despite ignore rules. | Clean tracking later, with approval. |
| `roadmaps-ideas/` | Keep | Contains current project planning artifacts. | Keep roadmaps and idea docs here. |

## Verified During Audit

Ran from `/private/tmp` to avoid dirtying repo outputs:

| Command | Result |
|---|---|
| `python3 -m experiments.pose.test_skeleton /Users/cbombs/github/angels-ai/assets/man.png` | Passed |
| `python3 -m experiments.pose.test_walk_cycle_v2 /Users/cbombs/github/angels-ai/assets/man.png` | Passed |
| `python3 -m experiments.pose.test_motion_video /Users/cbombs/github/angels-ai/assets/walk.mp4` | Passed; wrote 42 pose frames |

## Fix Plan Step 3

Complete:

1. Preserved prototype code under `experiments/`.
2. Added installable `src/angels_ai/` package metadata.
3. Defined motion, pose, face, generation, and pipeline boundaries.
4. Kept assets and outputs ignored.

Tracked generated files remain a separate cleanup decision requiring approval.

## Roadmap V3 Step 4

Complete: `RTMPoseVideoPreprocessor` now converts a Mixamo/Blender driver MP4 into a frame-aligned pose-conditioning MP4.
