# mtg-irs — project notes for Claude

## Conventions
- **All graphics are produced in English** (titles, labels, legends, annotations,
  footnotes, colour-bar text). This applies even though we talk in Turkish.
- Conversation with the project owner is in Turkish.
- Times on graphics: TRT (UTC+3), stated on the card.
- Every graphic credits its data source, e.g. "Data: EUMETSAT MTG-S1 IRS (L1, LAC4)".
- Anything made from synthetic data carries a "DRAFT · SYNTHETIC DATA" badge and watermark.

## Data facts (checked 2026-11-17)
- IRS in the EUMETSAT Data Store is Level 1 only:
  `EO:EUM:DAT:0737` (300 principal components, ~0.55 GB per product) and
  `EO:EUM:DAT:0741` (full spectral soundings, 1953 channels, ~4.7 GB per product).
  No IRS Level 2 collection yet.
- LAC4 (Europe) is scanned every 30 min, filename tag `Q4`. Each product is split
  into ~76 chunk files that can be downloaded individually.
- Search/browse works anonymously; download needs auth.
- Auth: eumdac 4.x uses OAuth2 with User Portal username/password from
  `EUMDAC_USER` / `EUMDAC_PW`. Legacy consumer key/secret still works via `--v1`.
