# Roadmap V3 Status

Current pipeline:

`character image + driver MP4 -> official Wan pose/face preprocessing -> Wan2.2-Animate -> final MP4`

| Step | Status | Evidence |
|---|---|---|
| 1. Audit existing project | Complete | `script-audit.md` |
| 2. Preserve prototype evidence | Complete | `experiments/` |
| 3. Real Mixamo/Blender motion source | Complete | `assets/walk.mp4`, 42 frames at 30 FPS |
| 4. RTMPose diagnostic extraction | Complete | `RTMPoseVideoPreprocessor` |
| 5. Wan face + pose preprocessing | Implemented; GPU acceptance pending | `WanAnimatePreprocessor` wraps the official joint preprocessing command, supports the external-data ViTPose layout, and validates all artifacts |
| 6. Generate character animation | Implemented; GPU acceptance pending | `WanAnimateBackend` wraps official Animate-14B generation and validates the MP4 |
| 7. Clean v2 architecture | Complete | `src/angels_ai/`, dependency split, focused tests, and `angels-ai doctor` readiness checks |
| 8. Product/chat actions | Later | Build after the real Wan acceptance video passes |

## Acceptance Gate

The application code and subprocess contracts are locally tested. Roadmap V3 is
not marked fully complete until a CUDA worker with the official 72.4 GB
checkpoint successfully produces `outputs/man-walking.mp4` from
`assets/man.png` and `assets/walk.mp4`, followed by visual inspection.

See `docs/wan-runtime.md` for the exact command.
