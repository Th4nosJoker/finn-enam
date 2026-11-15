#!/usr/bin/env python3
"""Select source pages for a portable research cache, retaining page citations.

This is a documented retrieval cache, not a replacement for the archived PDFs.
Full text remains in data/processed/documents.json and cached raw extraction.
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"

GROUPS = [
    (r"consolidated\s+(?:statement[s]?\s+of\s+)?(?:profit|income)|consolidated\s+financial\s+results", 6),
    (r"consolidated\s+balance\s+sheet|consolidated\s+statement\s+of\s+financial\s+position", 4),
    (r"consolidated\s+(?:statement[s]?\s+of\s+)?cash\s*flow", 5),
    (r"segment\s+(?:information|revenue|results|reporting)|business\s+segments", 5),
    (r"management.{0,15}discussion|operating\s+(?:review|performance)|business\s+(?:overview|model)", 5),
    (r"borrowings|working\s+capital|capital\s+expenditure|debt\s+equity", 5),
    (r"cash\s+conversion|cash\s+generated\s+from|free\s+cash\s+flow|cash\s+from\s+operations", 4),
    (r"outlook|guidance|growth\s+strategy|chairman.{0,10}(?:message|letter)", 4),
]


def select_pages(doc):
    pages = doc.get("pages", [])
    if doc["type"] == "transcript":
        return pages
    limit = 48 if doc["type"] == "annual_report" else 32
    if len(pages) <= limit:
        return pages
    chosen = {p["page"] for p in pages[:4]}
    for pattern, quota in GROUPS:
        scored = []
        for page in pages:
            text = re.sub(r"\s+", " ", page["text"]).lower()
            count = len(re.findall(pattern, text))
            if not count:
                continue
            # Contents pages mention many sections but contain little evidence.
            content_penalty = .2 if "contents" in text[:200] or "table of contents" in text[:500] else 1
            financial_context = 1 + min(len(re.findall(r"\b\d[\d,.]*\b", text)), 150) / 150
            scored.append((count * content_penalty * financial_context, page["page"]))
        for _, number in sorted(scored, reverse=True)[:quota]:
            chosen.add(number)
            # The following page often contains the continuation of a statement.
            chosen.add(number + 1)
    ranked = []
    for page in pages:
        text = re.sub(r"\s+", " ", page["text"]).lower()
        score = sum(len(re.findall(pat, text)) for pat, _ in GROUPS)
        ranked.append((score, page["page"]))
    if len(chosen) > limit:
        chosen = set(n for _, n in sorted((s, n) for s, n in ranked if n in chosen)[-limit:])
    else:
        for _, number in sorted(ranked, reverse=True):
            chosen.add(number)
            if len(chosen) >= limit:
                break
    return [p for p in pages if p["page"] in chosen]


def main():
    docs = json.loads((OUT / "documents.json").read_text())
    deduplicated = {}
    for doc in docs:
        if doc.get("extractionStatus") == "text":
            deduplicated[doc["id"]] = doc
    compact = []
    for doc in deduplicated.values():
        pages = select_pages(doc)
        compact.append({**doc, "pages": pages, "cachedPageCount": len(pages),
                        "coverageNote": "Complete text" if len(pages) == len(doc["pages"]) else f"Selected evidence pages ({len(pages)} of {len(doc['pages'])} text pages); original PDF linked"})
    target = OUT / "documents-compact.json"
    target.write_text(json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
    manifest = {"documentCount": len(compact), "fullTextPageCount": sum(len(d["pages"]) for d in deduplicated.values()),
                "cachedPageCount": sum(len(d["pages"]) for d in compact),
                "coverage": {f"{symbol}/{kind}": count for (symbol, kind), count in Counter((d["symbol"], d["type"]) for d in compact).items()},
                "fullCorpusBytes": (OUT / "documents.json").stat().st_size, "portableCorpusBytes": target.stat().st_size,
                "selectionPolicy": "Full transcripts; up to48 annual-report and32 result pages selected for financial statements, segments, business, debt, cash, outlook. Full source documents remain available.",
                "sourceFiles": ["companies.json", "prices.json", "announcements.json", "universe.json", "documents.json", "documents-compact.json", "source-checks.json"]}
    (OUT / "corpus-manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
