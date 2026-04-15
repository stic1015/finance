# Finance Handoff

## Purpose

- This file is the rolling handoff for `D:\Codex\Finance`.
- It captures the current operational truth only.
- Historical reasoning and session-by-session detail belong in separate archive files under `docs/context`.

## Current Goals And Priority

1. Finish the interrupted refactor as one release unit without reopening scope.
2. Keep homepage, strategy lab, and stock research on clean text paths (no mojibake).
3. Keep opportunities and strategy metadata interfaces stable for frontend consumption.

## Confirmed Technical And Process Constraints

- `docs/context` is the long-term home for Finance context documents.
- `finance-handoff.md` is the main rolling handoff document.
- Session archive files preserve context fidelity and should not be rewritten into a running changelog.
- The publish-sync mechanism must not rely on Git hooks.
- The publish-sync mechanism must not rely on GitHub Actions writing back into the repository.
- The preferred design is a single official publish entrypoint that updates handoff state as part of the release flow.
- The repository may require extra care around Git metadata handling because the workspace has previously used separated git metadata paths.

## Unfinished Work And Recommended Order

1. Complete GitHub push and verify Vercel production deployment for the current refactor batch.
2. Run post-deploy smoke checks for:
   - `/api/markets/opportunities`
   - strategy lab new strategy templates
   - stock research interval switching (`1d/1h/30m/15m`)
3. Keep tracking live data quality for opportunity scoring inputs (snapshot/candle/news).

## Release Sync Requirements

After every successful publish or repository push flow, update this file with at least:

- Completed This Release: concise summary of what shipped
- Remaining Work: the active unresolved items
- Recommended Next Step: the best immediate follow-up action
- Latest Release Marker: timestamp, tag, commit, or other chosen release marker

## Update Rules

- Keep this file short and current.
- Do not copy full chat transcripts here.
- Do not duplicate long historical reasoning that already exists in a session archive document.
- If a release did not materially change project state, keep the update minimal instead of writing filler.

## Current Snapshot

- Completed This Release: Released opportunity board API and UI, added four institutional strategies, and consolidated clean strategy metadata.
- Remaining Work: Run production smoke checks for opportunities endpoint and strategy/research pages after deployment.
- Recommended Next Step: Verify /api/markets/opportunities on production and validate action/reason rendering on homepage.
- Latest Release Marker: $ReleaseMarker
