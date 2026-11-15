#!/usr/bin/env python3
"""Meaningful ingestion-integrity checks; not financial-fact validation."""
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "processed"


def load(name):
    return json.loads((OUT / name).read_text())


def main():
    companies, prices, filings, docs, universe = [load(f + ".json") for f in ["companies", "prices", "announcements", "documents", "universe"]]
    symbols = {c["symbol"] for c in companies}
    assert len(companies) == len(symbols) == 18
    assert symbols <= {c["symbol"] for c in universe}
    assert {r["symbol"] for r in prices} == symbols
    assert all(r["close"] > 0 and r["volume"] >= 0 for r in prices)
    assert len({(r["symbol"], r["date"]) for r in prices}) == len(prices)
    assert min(Counter(r["symbol"] for r in prices).values()) >= 100
    assert all(r["symbol"] in symbols and r["publishedAt"] and r["attachmentUrl"] for r in filings)
    assert len({r["id"] for r in filings}) == len(filings)
    assert len({d["id"] for d in docs}) == len(docs) == 60
    for symbol in ["TCS", "INFY", "TITAN", "POLYCAB"]:
        company_docs = [d for d in docs if d["symbol"] == symbol]
        assert Counter(d["type"] for d in company_docs) == {"annual_report": 3, "transcript": 7, "results": 5}
        assert len({d["period"] for d in company_docs if d["type"] == "annual_report"}) == 3
        assert all(d["pages"] and d["sha256"] and d["url"].startswith("https:") for d in company_docs)
        assert all(len({p["page"] for p in d["pages"]}) == len(d["pages"]) for d in company_docs)
    report = {"status": "passed", "companies": len(companies), "priceObservations": len(prices), "filings": len(filings),
              "documents": len(docs), "nseUniverse": len(universe), "sourceTextPages": sum(len(d["pages"]) for d in docs),
              "firstMarketDate": min(r["date"] for r in prices), "lastMarketDate": max(r["date"] for r in prices),
              "scope": "Ingestion integrity and research corpus coverage; downstream extracted financial facts require separate reconciliation."}
    (OUT / "ingestion-checks.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
