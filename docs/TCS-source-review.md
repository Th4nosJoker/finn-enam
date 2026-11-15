# TCS prepared source review

Prepared from the ingested company annual reports, quarterly results and earnings-call transcripts only. No secondary commentary or external company knowledge was used. This is a cached, AI-assisted source review rather than a claim that the deployed application generated the dossier live.

## Financial reconciliation

All monetary figures below are consolidated INR crore, except where stated.

| Metric | FY2024 | FY2025 | FY2026 | Source |
| --- | ---: | ---: | ---: | --- |
| Revenue | 240,893 | 255,324 | 267,021 | FY2025 annual report PDF p182; FY2026 annual report PDF p168 |
| Total PAT, including NCI | 46,099 | 48,797 | 49,454 | Same consolidated P&L pages |
| Cash from operations | 44,338 | 48,908 | 52,094 | FY2025 annual report PDF p185; FY2026 annual report PDF p173 |

Latest Q2 FY2027 result (document `5179bb0306b4cde2ed74`, PDF p8) compares September 2026, June 2026 and September 2025 quarters:

| Metric | Q2 FY2027 | Q1 FY2027 | Q2 FY2026 |
| --- | ---: | ---: | ---: |
| Revenue | 73,188 | 72,275 | 65,799 |
| PBT | 18,638 | 17,944 | 16,068 |
| Total PAT including NCI | 13,934 | 13,420 | 12,131 |
| PAT attributable to owners | 13,884 | 13,349 | 12,075 |

Operating margin of 24% is a management-reported operating metric, not EBITDA. The prepared dossier does not fabricate an EBITDA value.

FY2026 reported PBT includes exceptional restructuring, Labour Code and legal-claim costs. The annual report's adjusted ratios and reported statutory PAT are not interchangeable. Cash conversion in the dossier explicitly states its denominator: CFO / total PAT is approximately 105.3%; the company's reported 105.9% annual cash-conversion ratio uses PAT attributable to shareholders.

The FCF proxy is defined as CFO minus cash purchases of PPE and intangibles: FY2026 `52,094 - 3,670 - 367 = 48,057`; FY2025 `48,908 - 2,917 - 944 = 45,047`. This deliberately excludes right-of-use payments, acquired assets and business acquisitions, and is labelled a proxy rather than all cash remaining after every investment.

## Guidance and scorecard

The company explicitly says it does not provide specific revenue or earnings guidance on the October 2025, January 2026, April 2026 and July 2026 call introductions (PDF p3 in each). The last four completed reporting quarters are Q3 FY2026, Q4 FY2026, Q1 FY2027 and Q2 FY2027. Their scorecard rows show reported outcomes, but are honestly `not_assessable` against a missing numerical quarterly promise.

October 2026 call PDF p15 does state a 26–28% long-term operating-margin aspiration. It has no fixed target quarter; the current 24% operating margin cannot fairly be called a quarterly guidance miss. Qualitative investment and scale-efficiency commentary is retained as qualitative, conditional outlook.

## Validation and limits

- All 56 citations attached to the eight view points are exact, whitespace-normalised substrings of the stated original PDF pages. Financial facts, guidance entries and scorecard sources were validated by the same citation constructor.
- All referenced pages exist in the portable `documents-compact.json` corpus, including result pages and full transcripts. No additional source-page merge is required for this dossier.
- Four-quarter promise sources precede outcome sources by at least one reporting cycle. No same-quarter retrospective statement is scored as a forecast.
- The review does not reconstruct a full borrowing-maturity schedule or adjusted net debt. It retains lease liabilities and avoids an unsupported debt-free claim.
- Numerical disclosure, calculated arithmetic and bull/bear inference are separated in the prose.
