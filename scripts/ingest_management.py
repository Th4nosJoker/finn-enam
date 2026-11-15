#!/usr/bin/env python3
"""Cache source-backed management-change examples from the portfolio filings."""
import json
import re
from ingest_sources import OUT, extract_document, write


def main():
    announcements = json.loads((OUT / "announcements.json").read_text())
    selected = [a for a in announcements if (
        a["symbol"] == "HDFCBANK" and a["publishedAt"][:10] in ["2026-11-13", "2026-11-06", "2026-10-27"]
        and re.search("change|general", a["headline"], re.I)
    ) or (a["symbol"] == "NTPC" and a["publishedAt"][:10] == "2026-10-23" and a["headline"] == "Appointment")]
    documents = [extract_document({"symbol": a["symbol"], "title": f"{a['symbol']} {a['headline']} {a['publishedAt'][:10]}",
                                   "type": "management_change", "period": a["publishedAt"][:10], "publishedAt": a["publishedAt"],
                                   "url": a["attachmentUrl"], "announcementId": a["id"]}) for a in selected]
    write("management-documents.json", documents)
    print(f"Management sources: {len(documents)} documents, {sum(len(d['pages']) for d in documents)} source pages")


if __name__ == "__main__":
    main()
