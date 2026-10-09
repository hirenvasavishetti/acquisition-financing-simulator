# Benchmark context and permitted-use review

Review date: 14 September 2026. Historical information cutoff: 15 May 2025.
These source references do not override any model configuration or clear the
company evidence gate. The synthetic benchmark curve remains an explicit choice.

For five-year fixed borrowing, the Federal Reserve Board's five-year Treasury
constant-maturity observation for 14 May 2025 is **4.17%**, distributed in
[FRED's DGS5 table](https://fred.stlouisfed.org/data/DGS5).
Use the prior day for announcement-time context; do not silently insert the
announcement day's later closing yield. This is a Treasury context rate, not a
corporate executable quote or a forward curve. The Board permits distribution of
its own data with attribution under its [disclaimer](https://www.federalreserve.gov/disclaimer.htm).
Source: Board of Governors of the Federal Reserve System, H.15, via FRED.

For overnight floating borrowing, consult the New York Fed's
[SOFR source](https://www.newyorkfed.org/markets/reference-rates/sofr) and
[FRED series table](https://fred.stlouisfed.org/data/SOFR). Observation date and
publication date differ: next-business-day publication means a 15 May observation
is not an announcement-day input. A current historical table is not an original
vintage archive. No SOFR numerical observation is redistributed in this package;
publication requires the reference-rate notices specified in the New York Fed's
[Terms of Use](https://www.newyorkfed.org/privacy/termsofuse.html).

BBB OAS observations are excluded because redistribution authorization was not
established. OAS is contextual, not an issuer borrowing quote. Rating, maturity,
currency, security and instrument differences matter; never add contextual OAS on
top of an issuer spread already representing the full assumed spread. The model
keeps benchmark, issuer spread and upfront/refinancing fees separate. Fixed-rate
new-debt configuration uses a matched-tenor fixed benchmark; floating configuration
uses a stated benchmark path and period reset convention.
