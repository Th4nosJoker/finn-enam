# FINN

FINN turns portfolio filings and company primary disclosures into a mobile investment-research workflow. Built for the ENAM AI Engineer challenge, November 2026.

## Run locally

Requires Node 24+, pnpm 11, and Python 3 with pypdf or pypdfium2 for refreshing the source corpus.

```sh
pnpm install
pnpm build
pnpm dev
```

Open `http://localhost:8787`. The local server uses durable SQLite under `.local/`; the hosted Worker uses Cloudflare D1. Local `.env` / `.env.local` and all raw PDFs are ignored by Git. Connect Gemini using the local-only page at `http://localhost:8787/__setup`; it saves the key to ignored local settings without printing it. Model names are overridable through `GEMINI_MODEL` and `GEMINI_REASONING_MODEL`. The example file documents all supported environment names. Hosted provider credentials are AES-GCM encrypted in private D1; the connection fingerprint is held as a native hosting secret and never returned by the app. `scripts/connect-provider.mjs` transfers the key directly from local settings to the authenticated private Site, without including it in chat or command arguments.

## Data and architecture

- React mobile interface: Today, Research, Alerts, Portfolio & Rules.
- JavaScript Worker service: company resolution, document discovery and parsing, evidence retrieval, research, on-demand questions, rules and alert generation.
- Python ingestion utilities: reproducible public-source downloads and PDF page extraction; full source corpus in `data/processed/documents.json`, portable evidence selection in `documents-compact.json`.
- Actual NSE directory; 18 mock portfolio names; six months of Yahoo daily prices; NSE exchange filings; company-issued annual reports, quarterly results and call transcripts discovered through Screener.
- All research passages retain original document URL and PDF page. Screener financial tables, broker research, news, and model memory are not research evidence.
- Cheap deterministic first-pass triage; one shared company analysis powers eight research views; source and analysis caches reduce duplicate work. The provider gateway supports Gemini Interactions and OpenAI Responses, with JSON outputs and `store:false`. Gemini is the selected live provider after OpenAI returned an exhausted-credit error. Live Q&A, financial and management extraction, and hosted eight-view ASIANPAINT research passed on the user's confirmed Free-tier project; evidence is tracked in `docs/acceptance.md`. Quotations are checked against the ingested page text.
- Period and currency/basis metadata accompany numerical facts. Ordinary code handles price/volume thresholds and comparable financial changes. Unsupported data is marked unavailable.

The initial data snapshot was ingested on 15 November 2026. The latest completed trading session is 13 November. The default 24-hour digest is honestly empty on Sunday; choose seven or thirty days to inspect recent filings.

## Source refresh

```sh
python3 scripts/ingest_sources.py
python3 scripts/compact_corpus.py
python3 scripts/ingest_management.py
python3 scripts/check_sources.py
pnpm build
```

Check each script's `--help` for options. The live API also refreshes prices and exchange announcements, and discovers/ingests primary PDFs for unseen NSE symbols. Source rejection, extraction failure and missing documents appear as explicit states, with cached evidence preserved. Newly discovered PDF extraction has a 40 MB / 1,000-page safety bound and reports scanned PDFs as requiring OCR.

## Monitoring

The local service runs a five-minute background refresh. The web workspace requests a throttled automatic check each minute while open. A Worker `scheduled` handler is included for unattended execution; an hourly hosted schedule is now linked and enabled. The initial authenticated updater/readback check passed with no source errors. The first scheduled occurrence was not yet observed at handoff; closed-app cadence is hourly because the hosting task service enforces that limit. Rules and detected-alert identities persist; repeated checks do not duplicate identical alerts.

## Checks

```sh
pnpm test
pnpm build
pnpm check
node scripts/audit-features.mjs
```

Meaningful checks cover financial comparison bases, volume lookbacks, alert boundaries, filing deduplication/grouping, citation validity and retrieval coverage. Browser review covers phone layouts and key interactions. Source-ingestion integrity is recorded in `data/processed/ingestion-checks.json`; it is not proof that generated financial analysis is correct.

## Scope and delivery status

See `docs/acceptance.md` for the current feature checklist and verification status. No feature is complete merely because it has a UI tab. The prototype is intended to show research judgment and source transparency; it does not place trades.

Submission source: https://github.com/Th4nosJoker/finn-enam. The native hosting source repository is separate. Actual build-conversation exports are packaged separately; they are excluded from the public source. The mock-data demo is published for evaluator access. Public visitors share the connected Gemini Free-tier quota; prepared dossiers and filing examples remain available if live quota is exhausted. No submission email has been sent.
