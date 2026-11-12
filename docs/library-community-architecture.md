# Sorin Library — community architecture (draft, 2026-11-12)

Status: **design proposal, not deployed**. Public `main` and the original Sorin beta backup must not be changed by this work.

## Product boundaries

- **Community-owned content:** emojis, stickers, sounds, graphics (including server icons, banners, role icons, welcome art). Members submit original/licensed files and retain attribution; Sorin moderates publication.
- **Sorin-curated directories:** bots and Discord servers. No community-created listings in the initial release. Store verified official URLs, review dates, source and ownership metadata; avoid suggesting that Sorin endorses third parties.
- **Library UX:** keep the small existing tiles, compact grids and search/filter controls; show a limited initial set with an explicit “Show more”. Do not add long stacked galleries.
- **Gamification:** points, creator levels and leaderboard are earned from *approved* contributions, not merely uploads. Avoid rewarding spam.

## Backend entities (initial proposal)

- `users`: id, handle (unique), email (unique, private), password_hash or external_auth_id, created_at, status.
- `assets`: id, creator_id, kind [emoji|sticker|sound|graphic], title, description, storage_key, mime_type, size_bytes, sha256, license, attribution, status [pending|approved|rejected|removed], created_at, reviewed_at, reviewed_by.
- `asset_reviews`: id, asset_id, reviewer_id, stars [1..5], created_at; unique (asset_id, reviewer_id), no self-rating.
- `moderation_events`: id, asset_id, moderator_id, decision, reason, created_at. Keep an audit trail and an appeal path.
- `point_events`: id, user_id, asset_id, reason, points, created_at, unique event key. Approval creates an idempotent award; reversal/rejection removes eligibility without double-awarding.
- `curated_listings`: id, kind [bot|server], title, official_url, category, verified_at, source_url, status.

Indexes: `assets(status,kind,created_at)`, `assets(creator_id,status)`, `asset_reviews(asset_id)`, `point_events(user_id)`, `curated_listings(kind,status)`.

## Suggested API (not yet implemented)

- `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /me`
- `GET /assets?kind=&sort=&cursor=`, `POST /assets` (authenticated; initially pending)
- `GET /me/submissions`, `POST /assets/:id/reviews` (one review per user; approved only)
- `GET /leaderboard?period=`, `GET /creators/:id`
- `GET /curated?kind=bot|server`
- Moderator only: `GET /moderation/queue`, `POST /moderation/assets/:id/decision`

Use server-side authorization for every mutation; never trust client-submitted points, role, owner or approval status.

## Points and level proposal

Start with **20 points per approved contribution** as a configurable value, not a hard-coded contract. Award once per unique approved asset. Deduplicate by hash and review suspicious near-duplicates; remove or reverse points for revoked items. Do not award points for ratings, page views or unapproved submissions. Level is derived from accumulated eligible points; publish level thresholds before launch. Rate-limit submissions and reviews. Leaderboard should allow opting out and support abuse reports.

## Security and operational gates before public launch

1. Store uploads outside executable/public application paths; random storage keys, strict MIME/signature checks, per-type size limits, image re-encoding and safe audio processing; scan uploads.
2. Secure authentication (salted password hashing, session cookie HttpOnly/Secure/SameSite, CSRF controls as appropriate), rate limiting and email verification.
3. Separate moderator/admin permissions, audit log, content takedown/reporting and copyright process.
4. Privacy policy, data retention/deletion, backup and restore test, monitoring and abuse-response process.
5. SQLite can support a local prototype; production DB/storage and deployment choices require a separate decision.

## Acceptance tests for the first integrated slice

- Anonymous upload and moderation calls are denied.
- A new upload is pending and invisible in public asset queries.
- Moderator approval publishes it and awards points **exactly once**, including repeated approval requests.
- Rejection/removal cannot be used to retain illegitimate leaderboard points.
- A user cannot rate their own asset or rate an unapproved asset; duplicate rating policy is enforced.
- Malformed, oversized or unsafe uploads are rejected; HTML text is escaped.
- Compact tile density and “Show more” work on desktop and mobile.
- Bots/servers can only be changed by authorized Sorin curators.
- Existing Builder/Templates and modal route navigation continue working.

## Integration plan

1. Audit the existing local Library V3 prototype (if its ZIP is available) against the contract above; do **not** claim its code is merged into this repository.
2. Add backend integration behind an explicit feature flag in `development`, preserving the existing standalone demo as fallback.
3. Run backend tests, JS syntax tests, manual browser smoke tests, and rollback verification.
4. Review and merge to `development` only after the integration is demonstrably safe. Public `main` requires separate user approval.
