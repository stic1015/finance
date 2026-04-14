# Finance Handoff

## Purpose

- This file is the rolling handoff for `D:\Codex\Finance`.
- It captures the current operational truth only.
- Historical reasoning and session-by-session detail belong in separate archive files under `docs/context`.

## Current Goals And Priority

1. Stabilize the Finance handoff workflow so project state survives interrupted sessions cleanly.
2. Introduce a single official publish entrypoint that can own both repository push behavior and handoff refresh behavior.
3. Resume unfinished product work in this order:
   - new strategy support
   - price-change percentage fallback
   - RSS/news source expansion

## Confirmed Technical And Process Constraints

- `docs/context` is the long-term home for Finance context documents.
- `finance-handoff.md` is the main rolling handoff document.
- Session archive files preserve context fidelity and should not be rewritten into a running changelog.
- The publish-sync mechanism must not rely on Git hooks.
- The publish-sync mechanism must not rely on GitHub Actions writing back into the repository.
- The preferred design is a single official publish entrypoint that updates handoff state as part of the release flow.
- The repository may require extra care around Git metadata handling because the workspace has previously used separated git metadata paths.

## Unfinished Work And Recommended Order

1. Finish the handoff document layer so future implementation does not lose context.
2. Implement the official publish entrypoint that updates this file after a successful push.
3. Resume backend and frontend functional work for:
   - strategy expansion
   - percentage fallback behavior
   - RSS provider expansion
4. Revisit `backend/app/services/backtest/strategies.py` carefully because the prior execution pass stopped at dirty or corrupted strategy text content.

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

- Completed This Release: established the Finance handoff documentation structure and separated archive context from rolling handoff state
- Remaining Work: official publish entrypoint, strategy work, percentage fallback, RSS expansion
- Recommended Next Step: implement the official publish entrypoint before resuming interrupted feature work
- Latest Release Marker: `docs baseline created on 2026-04-14`
