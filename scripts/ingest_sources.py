#!/usr/bin/env python3
"""Reproducible public-source ingestion for FINN. Never synthesizes financial facts.

Run with Python 3 + pypdf: python scripts/ingest_sources.py [--documents]
Raw downloads are cached by URL hash; --refresh bypasses their cache.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import html
import io
import json
import re
import time
import threading
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
for directory in (RAW, OUT):
    directory.mkdir(parents=True, exist_ok=True)
NOW = datetime.now(timezone.utc).isoformat()
CHECKS = []
FETCH_TIMES = {}
REFRESH = False
PDF_LOCK = threading.Lock()
PORTFOLIO = [
    ("RELIANCE", "Reliance Industries", "Diversified", "500325", False),
    ("TCS", "Tata Consultancy Services", "IT Services", "532540", True),
    ("INFY", "Infosys", "IT Services", "500209", True),
    ("HDFCBANK", "HDFC Bank", "Banking", "500180", False),
    ("ICICIBANK", "ICICI Bank", "Banking", "532174", False),
    ("ITC", "ITC", "Consumer Staples", "500875", False),
    ("HINDUNILVR", "Hindustan Unilever", "Consumer Staples", "500696", False),
    ("TITAN", "Titan Company", "Consumer Discretionary", "500114", True),
    ("MARUTI", "Maruti Suzuki India", "Automobiles", "532500", False),
    ("SUNPHARMA", "Sun Pharmaceutical Industries", "Pharmaceuticals", "524715", False),
    ("LT", "Larsen & Toubro", "Industrials", "500510", False),
    ("ULTRACEMCO", "UltraTech Cement", "Building Materials", "532538", False),
    ("NTPC", "NTPC", "Power", "532555", False),
    ("BHARTIARTL", "Bharti Airtel", "Telecommunications", "532454", False),
    ("POLYCAB", "Polycab India", "Electrical Equipment", "542652", True),
    ("CDSL", "Central Depository Services (India)", "Market Infrastructure", None, False),
    ("CAMS", "Computer Age Management Services", "Financial Infrastructure", "543232", False),
    ("APLAPOLLO", "APL Apollo Tubes", "Steel Products", "533758", False),
]
COMPANIES = [dict(zip(("symbol", "name", "sector", "bseCode", "research"), c)) for c in PORTFOLIO]
SYMBOLS = {c[0] for c in PORTFOLIO}


def write(name, value):
    path = OUT / name
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")))
    tmp.replace(path)


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def get(url, timeout=35):
    key = hashlib.sha256(url.encode()).hexdigest()[:24]
    path = RAW / key
    if path.exists() and not REFRESH:
        FETCH_TIMES[url] = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
        CHECKS.append({"url": url, "status": "cache_hit", "bytes": path.stat().st_size, "retrievedAt": FETCH_TIMES[url], "checkedAt": NOW})
        return path.read_bytes()
    last = None
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.bseindia.com/" if "bseindia" in url else "https://www.nseindia.com/",
                "Accept": "*/*",
            })
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read(60 * 1024 * 1024)
                path.write_bytes(data)
                FETCH_TIMES[url] = NOW
                CHECKS.append({"url": url, "status": response.status, "bytes": len(data), "checkedAt": NOW})
                return data
        except Exception as exc:
            last = exc
            if attempt == 0:
                time.sleep(.5)
    CHECKS.append({"url": url, "error": str(last), "checkedAt": NOW})
    raise last


def price_one(company):
    symbol = company["symbol"]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}.NS?range=6mo&interval=1d"
    payload = json.loads(get(url))
    chart = payload["chart"]["result"][0]
    quote = chart["indicators"]["quote"][0]
    records = []
    for i, stamp in enumerate(chart.get("timestamp", [])):
        close = quote["close"][i]
        volume = quote["volume"][i]
        if close is None or volume is None:
            continue
        records.append({"symbol": symbol, "date": datetime.fromtimestamp(stamp, timezone.utc).strftime("%Y-%m-%d"), "close": round(close, 4), "volume": volume,
                        "sourceUrl": url, "retrievedAt": FETCH_TIMES.get(url, NOW), "adjustment": "Yahoo daily close; no implicit adjusted-close substitution"})
    return records


def announce_one(company, history=False):
    symbol = company["symbol"]
    # Explicit source window; retain original exchange broadcast times.
    start = "01-10-2025" if history else "15-10-2026"
    url = "https://www.nseindia.com/api/corporate-announcements?" + urllib.parse.urlencode({"index": "equities", "symbol": symbol, "from_date": start, "to_date": "15-11-2026"})
    raw = json.loads(get(url))
    records = []
    for item in raw:
        if item.get("symbol") != symbol:
            continue
        published = item.get("sort_date") or item.get("an_dt")
        if published and re.match(r"\d{4}-\d{2}-\d{2} ", published):
            published = published.replace(" ", "T") + "+05:30"
        records.append({"id": str(item.get("seq_id") or hashlib.sha256(json.dumps(item,sort_keys=True).encode()).hexdigest()[:20]),
                        "symbol": symbol, "headline": item.get("desc", ""), "details": item.get("attchmntText", ""),
                        "publishedAt": published, "url": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
                        "attachmentUrl": item.get("attchmntFile"), "sourceUrl": url, "retrievedAt": FETCH_TIMES.get(url, NOW)})
    return records


def discover(symbol):
    source = f"https://www.screener.in/company/{symbol}/consolidated/"
    page = get(source).decode(errors="replace")
    links = []
    # Annual-report anchors are explicitly labelled; do not ingest Screener's AI summaries.
    annuals = re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>\s*(Annual Report\s+\d{4})\s*</a>', page, re.S)
    annual_years = set()
    for url, title in annuals:
        if clean(title) in annual_years:
            continue
        annual_years.add(clean(title))
        links.append({"symbol": symbol, "title": f"{symbol} {clean(title)}", "type": "annual_report", "url": html.unescape(url), "period": clean(title).replace("Annual Report ", "FY"), "publishedAt": None, "discoveryUrl": source})
        if len(annual_years) >= 3:
            break
    # Each concall list item contains its month and the raw company transcript link.
    section_start = page.find('documents concalls')
    if section_start < 0:
        section_start = page.find('Concalls')
    concalls = page[section_start:] if section_start >= 0 else ""
    found = 0
    transcript_periods = set()
    for li in re.findall(r"<li\b[^>]*>(.*?)</li>", concalls, re.S):
        transcript = re.search(r'<a\b[^>]*href="([^"]+)"[^>]*title="Raw Transcript"[^>]*>\s*Transcript\s*</a>', li, re.S)
        if not transcript:
            # Attribute order can vary.
            transcript = re.search(r'<a\b[^>]*href="([^"]+)"[^>]*>\s*Transcript\s*</a>', li, re.S)
        if not transcript:
            continue
        month = re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(20\d{2})\b", clean(li))
        if not month:
            continue
        period = month.group(0)
        if period in transcript_periods:
            continue
        transcript_periods.add(period)
        links.append({"symbol": symbol, "title": f"{symbol} Earnings-call transcript {period}", "type": "transcript", "url": html.unescape(transcript.group(1)), "period": period, "publishedAt": None, "discoveryUrl": source})
        found += 1
        if found >= 7:
            break
    return links


def pdf_url_candidates(url):
    yield url
    if "AnnPdfOpen.aspx?Pname=" in url:
        name = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("Pname", [""])[0]
        if name:
            yield "https://www.bseindia.com/xml-data/corpfiling/AttachHis/" + name
            yield "https://www.bseindia.com/xml-data/corpfiling/AttachLive/" + name


def extract_document(meta):
    key = hashlib.sha256(meta["url"].encode()).hexdigest()[:20]
    parsed = RAW / (key + ".pages.json")
    if parsed.exists() and not REFRESH:
        cached = json.loads(parsed.read_text())
        if cached.get("parserVersion") == "pdfium-v1":
            return cached
    try:
        data = None
        for url in pdf_url_candidates(meta["url"]):
            try:
                attempt = get(url, timeout=50)
                if attempt.startswith(b"%PDF"):
                    data = attempt
                    break
            except Exception:
                pass
        if data is None:
            raise ValueError("No PDF returned by source URL")
        pages = []
        try:
            import pypdfium2 as pdfium
            # PDFium provides more complete font decoding in this runtime. Its C
            # API is not thread safe, so serialise parsing while downloads overlap.
            with PDF_LOCK:
                pdf = pdfium.PdfDocument(data)
                page_count = len(pdf)
                for index in range(page_count):
                    page = pdf[index]
                    textpage = page.get_textpage()
                    text = textpage.get_text_range().strip()
                    textpage.close()
                    page.close()
                    if text:
                        pages.append({"page": index + 1, "text": text})
                pdf.close()
        except ImportError:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data), strict=False)
            page_count = len(reader.pages)
            for number, page in enumerate(reader.pages, 1):
                text = (page.extract_text() or "").strip()
                if text:
                    pages.append({"page": number, "text": text})
        result = {**meta, "id": key, "retrievedAt": NOW, "sha256": hashlib.sha256(data).hexdigest(), "pageCount": page_count, "pages": pages, "parserVersion": "pdfium-v1", "extractionStatus": "text" if pages else "needs_ocr"}
        parsed.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        print(f"document {meta['symbol']} {meta['type']} {meta['period']}: {len(pages)} text pages", flush=True)
        return result
    except Exception as exc:
        print(f"document failed {meta['symbol']} {meta['title']}: {exc}", flush=True)
        return {**meta, "id": key, "pages": [], "extractionStatus": "failed", "error": str(exc), "retrievedAt": NOW}


def run_pool(function, items, workers=6):
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(function, item): item for item in items}
        for future in concurrent.futures.as_completed(futures):
            item = futures[future]
            try:
                records.append(future.result())
            except Exception as exc:
                print("failed", str(item)[:100], str(exc), flush=True)
    return records


def main():
    global REFRESH
    parser = argparse.ArgumentParser()
    parser.add_argument("--documents", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    REFRESH = args.refresh
    write("companies.json", COMPANIES)
    try:
        url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
        rows = list(csv.DictReader(io.StringIO(get(url).decode("utf-8-sig"))))
        universe = [{"symbol": r["SYMBOL"].strip(), "name": r["NAME OF COMPANY"].strip(), "isin": r.get(" ISIN NUMBER", r.get("ISIN NUMBER", "")).strip(), "series": r.get(" SERIES", r.get("SERIES", "")).strip()} for r in rows]
        write("universe.json", universe)
        print("NSE universe", len(universe), flush=True)
    except Exception as exc:
        print("universe failed", exc, flush=True)
    prices = [record for group in run_pool(price_one, COMPANIES) for record in group]
    write("prices.json", prices)
    print("prices", len(prices), Counter(r["symbol"] for r in prices), flush=True)
    announcements = [record for group in run_pool(announce_one, COMPANIES) for record in group]
    announcements.sort(key=lambda r: r["publishedAt"] or "", reverse=True)
    write("announcements.json", announcements)
    print("announcements", len(announcements), flush=True)
    write("source-checks.json", CHECKS)
    if args.documents:
        research = [c for c in COMPANIES if c["research"]]
        discoveries = [link for links in run_pool(lambda c: discover(c["symbol"]), research, 4) for link in links]
        # Gather actual result filings across the scorecard's outcome window.
        history = [r for rs in run_pool(lambda c: announce_one(c, True), research, 4) for r in rs]
        write("announcements-history.json", history)
        for company in research:
            symbol = company["symbol"]
            candidates = [r for r in history if r["symbol"] == symbol and r.get("attachmentUrl") and
                          re.search(r"outcome of board meeting|financial results", r["headline"], re.I) and
                          re.search(r"financial results", r["headline"] + " " + r["details"], re.I) and
                          not re.search(r"intimation|newspaper|publication", r["headline"], re.I)]
            candidates.sort(key=lambda r: r["publishedAt"] or "", reverse=True)
            months = set()
            for filing in candidates:
                month = (filing.get("publishedAt") or "")[:7]
                if month in months:
                    continue
                months.add(month)
                discoveries.append({"symbol": symbol, "title": f"{symbol} {filing['headline']} {filing['publishedAt'][:10]}", "type": "results", "url": filing["attachmentUrl"], "period": filing["publishedAt"][:10], "publishedAt": filing["publishedAt"], "discoveryUrl": filing["sourceUrl"]})
                if len(months) >= 5:
                    break
        write("discovered-documents.json", discoveries)
        documents = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(extract_document, meta) for meta in discoveries]
            for future in concurrent.futures.as_completed(futures):
                documents.append(future.result())
                write("documents.json", documents)
        write("source-checks.json", CHECKS)
        print("document coverage", Counter((d["symbol"], d["type"], d["extractionStatus"]) for d in documents), flush=True)


if __name__ == "__main__":
    main()
