**Independent primary-source reconciliation**

These checks use company filings and call transcripts from the actual corpus. Values are manually reconciled to the cited PDF tables; indicated latest-quarter pages were also visually checked.

**Polycab: complete four-metric enrichment**

Use actual results event `106818441`; related company earnings presentation `106818494` and company press release `106818462`.

The company presentation (document `17e3080f5a6db2349fc2`, PDF page 15) reports the following consolidated figures in **INR million**, rounded to the nearest million:

| Metric | Q2FY27, Sep2026 | Q1FY27, Jun2026 | Q2FY26, Sep2025 |
|---|---:|---:|---:|
| Revenue | 98,989 | 82,097 | 64,772 |
| EBITDA | 14,225 | 11,362 | 10,207 |
| PBT | 13,062 | 10,582 | 9,210 |
| Total PAT | 9,900 | 7,967 | 6,930 |

PDF page 19 explicitly defines EBITDA as excluding other income. Page15 therefore supplies a complete reported four-metric example without substituting operating profit. The company press release (`d25a4250f7cdea65dce6`, PDF pages 2–3) independently reports current EBITDA and its YoY/QoQ growth. Both complete source documents are in `supplemental-documents.json`.

The actual financial-results statement (`ba0b8cd298e46095964f`, PDF page 4) preserves higher precision. Operational EBITDA can also be reconciled as PBT + finance cost + depreciation/amortisation − other income: **14,224.98 / 11,361.99 / 10,207.49 million**, which rounds to the reported EBITDA. Preserve this as a derivation, separately from the reported rounded amounts.

Total PAT is 9,899.97 /7,966.54 /6,929.59 million; PAT attributable to owners is 9,773.74 /7,843.37 /6,854.56 million. These are distinct bases.

**Infosys: financial checks and pitfalls**

Latest filing `4d2e7774ca8a2887b366`, PDF page 6 (IFRS INR fact sheet) and page 18 (Ind-AS statement): consolidated revenues 49,244 /48,211 /44,490 crore and PBT 11,063 /11,028 /10,229 crore for Sep2026 /Jun2026 /Sep2025. Owner-attributable net profit is 7,823 /7,769 /7,364 crore; total profit for the period is 7,838 /7,775 /7,375 crore. Do not mix these PAT bases.

The fact-sheet table order is current/year-ago/YoY/previous/QoQ. The consolidated financial-results statement instead orders current/previous/year-ago/half-year/year. USD and INR tables also coexist. Operating profit 10,330 crore is **not reported EBITDA**. There is no EBITDA label in this 195-page results filing.

**Guidance chronology**

- On 14Jan2026, Infosys guided FY26 CC revenue growth of 3%–3.5% (`07929340a0affc4b83a5`, PDF page 4). On 23Apr2026 it reported FY26 CC growth 3.1%, explicitly within that upgraded January band (`9245fc9faa070d829354`, page28). This is a legitimate **annual** met comparison.
- On 23Apr2026, FY27 guidance was 1.5%–3.5% CC growth; on23Jul2026 it became 1.5%–3%; on23Oct2026 it became 1%–2%. These are sourced annual-guidance revisions. FY27 is incomplete, so its delivery verdict is pending. A quarterly CC growth rate is not the annual outcome.
- Polycab's Project Spring FMEG target is 8%–10% EBITDA margin by FY30. Management explicitly says the guidance is for FY30 (`3c39debac5dedfdf9df0`, PDF page9). A current quarterly EBIT margin cannot establish delivery of that future EBITDA target.

The JSON supplies source IDs, exact short quotes, actual PDF page numbers, dates, precise values, computed changes, ready enrichment objects and supporting evidence pages. It validates a small reference set; the rest of the app's generated facts still require reconciliation.
