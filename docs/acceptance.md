# AI Engineer assignment: verification

Verified on 15 November 2026. This checklist distinguishes implemented behaviour, actual live tests and delivery requirements.

| Assignment feature | Evidence |
| --- | --- |
| Mobile-first working prototype | Deployed Worker + React app; phone viewport390px had page width390px. Live question, answer and original-page evidence flow passed. |
| 15–20 company portfolio | 18 diversified companies; portfolio add/remove and database readback passed. |
| 3–5 research examples | Four prepared, fully cited dossiers: INFY, TCS, TITAN, POLYCAB. A fifth, ASIANPAINT, was generated live outside the seed set. |
| EOD price/volume | 2,286 observations, 127 sessions per company; latest completed session13November. Previous20-session volume baseline excludes the evaluated session. |
| NSE/BSE filings | 271 initial exchange filings; deterministic17-category classification, priorities and routine grouping. Public exchange source ingestion passed. |
| Company fundamentals | Seed corpus:60 annual reports/transcripts/results,6,994 text pages;6 supplemental/management documents. Unseen ASIANPAINT:3 annual reports,7 transcripts,5 results ingested with no source errors. |
| Default24h / configurable digest | Phone default and7-day window verified; routine expansion and custom date backfill tested. Sunday default is honestly empty. |
| Triggered alerts | Category, materiality, price, volume and lookback settings persist; boundary, disabled-rule, deduplication, read-state and invalid-input checks passed. |
| Automatic checks | Open-session checks and linked hourly cloud schedule enabled. Authenticated writer returned18companies with zero source errors. Closed-app cadence is hourly; a scheduled occurrence was not independently observed. |
| Results Revenue/EBITDA/PBT/PAT + QoQ/YoY | Live POLYCAB extraction matched all12 current/previous/year-ago values; all12 citations validated. Code calculates changes with matching basis and units; non-positive bases are explicit. |
| Management background | Four prepared, sourced filing extractions; live HDFCBANK extraction returned Rangan's role, reappointment and professional background with a valid source. |
| All8 research views | Four prepared examples verified. Hosted ASIANPAINT live report returned8nonempty views and26cited points. |
| Four-quarter promise/delivery | All prepared reports have4rows; live ASIANPAINT has4rows. Annual guidance is not scored against a quarterly result. Unsupported matches remain not_assessable. |
| Contextual company questions | Live local and hosted INFY questions passed; phone form and source drawer passed. |
| Generalisation beyond demos | Hosted ASIANPAINT discovered/ingested15documents, then extracted and synthesised a fresh report through the same job pipeline. |
| Primary-only evidence | Prepared outputs:371citation occurrences checked. Live outputs:82citation occurrences verified independently against26pages from the deployed source API. No broker/news sources are research inputs. |
| Efficiency and failures | Document/fact/research caches; cheap extraction followed by reasoning synthesis; no duplicate fact generation in synthesis. Bounded503 retries, explicit quota/permission/truncation errors. Usage telemetry records provider-reported tokens and latency. |
| Automated checks |22unit checks passed;14offline integrated workflow checks passed. Valid Worker ESM/build passed. |
| Secrets | Local keys are ignored by Git; hosted Gemini key is encrypted in private D1, with the connection fingerprint held as a native secret. Both actual keys were checked absent from the compiled bundle. |

## Delivery

- Live demo: https://finn-enam-rohit-2026.wildcarol8.chatgpt.site (public mock-data reviewer demo).
- GitHub target: https://github.com/Th4nosJoker/finn-enam. The source is published using the official connector; private chat exports and credentials are excluded.
- Actual build conversations are supplied as a separate private export; source archives exclude chat histories, secrets and local databases.
- Covering email is prepared separately and has not been sent.

## Limits established by testing

The four seed dossiers are clearly labelled prepared source reviews. Generic live research is generated from available retrieved passages; financial fact counts can be sparse after citation validation (ASIANPAINT had5validated facts). A valid quote does not prove every interpretation. Missing or horizon-mismatched guidance is explicitly unassessed. Scanned PDFs require OCR and oversized/unavailable documents produce coverage gaps. The OpenAI attempt returned exhausted credits; Gemini is the selected live provider on the user's confirmed Free-tier project.

Detailed evidence: `docs/feature-audit.json` and `docs/live-feature-audit.json`.
