**Public data ingestion**

Run `python scripts/ingest_sources.py --documents`, then `python scripts/compact_corpus.py` from the FINN directory. Python's standard library handles HTTP/HTML; PDF parsing uses `pypdfium2` when available, with `pypdf` as a fallback. The Codex bundled Python runtime already supplies both. `--refresh` bypasses raw caches.

This initial snapshot is explicitly bounded to 15 November 2026. The portfolio announcement window is 15 October–15 November 2026; research results history begins 1 October 2025. Daily-price history is requested with Yahoo's six-month range and contains observations through the last completed trading day, 13 November 2026. A later snapshot should update the explicit exchange date bounds or use the application's live refresh adapters.

`data/processed/companies.json` contains the 18-company mock portfolio. `universe.json` is the NSE equity-symbol master, with company names, ISINs and series. Company identity is checked against that source rather than guessed from a name.

`prices.json` contains 127 observations per company. These are Yahoo's daily close and volume, not intraday prices. Preserve source dates and the stated adjustment basis; changes in corporate actions can need additional handling before interpreting an anomaly.

`announcements.json` preserves all 271 fetched portfolio filings in the snapshot window. `announcements-history.json` supplies the longer filing history for the four research examples. Both retain original attachment URLs and exchange timestamps; document classification, event grouping and materiality are application concerns.

`discovered-documents.json` contains primary-document links discovered on Screener. Screener's AI summaries and derived financial tables are deliberately excluded. Annual reports, transcripts and results are company disclosures hosted by BSE/NSE. The corpus has three distinct annual-report years, seven distinct transcript months, and five quarterly result filings for each of TCS, Infosys, Titan and Polycab. Publication dates remain null when discovery does not supply one; a report's fiscal year is not presented as its publication date.

`documents.json` contains every extracted text page, with the original 1-based PDF page number. Raw PDFs and extraction caches live in ignored `data/raw/`. The portable `documents-compact.json` retains full transcripts and a documented selection of annual-report/result pages. `corpus-manifest.json` records the counts and selection policy. Page-selected coverage is visibly labelled so that it is not mistaken for a full-document search index.

Checks performed: all 18 portfolio symbols occur in the 2,635-symbol NSE master; all 18 have 127 positive-price observations; no duplicate company/date observations; no duplicate filing IDs; every document has source provenance, a content hash and nonempty extracted pages; every research example has 3 annuals, 7 transcripts and 5 results. These checks verify ingestion integrity, not the correctness of later model-extracted financial facts.

Source access findings: Yahoo chart, NSE announcements, NSE symbol CSV, Screener discovery and exchange-hosted PDFs all worked. The BSE announcement API and Infosys HTML pages returned 403 in the first check; the pipeline uses accessible NSE and exchange-PDF alternatives. Yahoo returned 429 with a browser-specific User-Agent but worked with a simple `Mozilla/5.0` User-Agent. Cache/error reporting must remain honest if source access later changes.
