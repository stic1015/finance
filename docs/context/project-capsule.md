# Project Capsule

## Active Runtime Chain

- Frontend entry: `frontend/src/main.ts`
- Frontend shell: `frontend/src/AppShell.vue`
- Active overview page target: replace with clean i18n-driven page
- Active stock research page target: replace with clean i18n-driven page
- Active strategy lab target: replace with clean i18n-driven page

## Product Scope

- Primary supported markets in the frontend: `HK`, `SH`, `SZ`
- `US` remains backend-compatible but is not part of the primary frontend research flow
- Backend remains local-only
- Frontend remains deployed on Vercel

## Current Backend Truth

- Market overview supports partial degradation by market
- HK and A-share symbols can be live
- US may downgrade independently to fixture when permissions are missing
- Strategy definitions currently include basic + institutional templates

## Current Frontend Risks

- Active page files contain corrupted copy
- Old and new page implementations coexist
- No formal i18n baseline exists yet
- Reminder and compare workflows are not implemented

## Current Priorities

1. Rebuild clean active pages
2. Add i18n foundation with `zh-CN` and `en-US`
3. Rebuild homepage as an opportunity discovery surface
4. Upgrade stock research conclusions
5. Upgrade strategy lab with richer result panels
6. Add local watchlist and alert workflows
