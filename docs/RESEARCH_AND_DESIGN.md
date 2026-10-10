# Research and design decisions

## What the project should demonstrate

Banking analysis is strongest when a financing choice can be followed through a model into a decision, rather than a collection of valuation multiples. JPMorgan's [investment banking analyst programme](https://www.jpmorganchase.com/careers/explore-opportunities/programs/investment-banking-fulltime-analyst) describes financial models, reports and transaction support. This project therefore puts sources and uses, cash availability, debt service and dilution on the same analytical path. It does not claim to replicate an institution's internal process.

Goldman Sachs describes its [FICC and Equities work](https://www.goldmansachs.com/careers/our-firm/FICC-and-equities/) in terms of market insight, analytics and risk. A financing simulator alone does not demonstrate instrument price risk. The separate rates lab adds an explicit, testable connection from cash flows to price, risk and a hypothetical hedge.

| Research | Implementation decision | Boundary |
|---|---|---|
| [OCC refinancing risk guidance](https://occ.treas.gov/news-issuances/bulletins/2024/bulletin-2024-29.html) | Show cash cushions and refinancing dependence across operating and rate stress. | Analytical screens are not legal covenants or commitments. |
| [CME basis point value](https://www.cmegroup.com/education/courses/introduction-to-sofr/understanding-the-importance-of-basis-point-value) | Compute DV01 from discounted cash flows; test it against central differences. | One basis point is 0.0001; dollar risk is not a percentage. |
| [CME Treasury DV01](https://www.cmegroup.com/trading/interest-rates/calculating-the-dollar-value-of-a-basis-point.html) | Size a hypothetical hedge using DV01 rather than matching notionals. | The input is an assumed contract DV01, not a futures quote or deliverable-basket calculation. |
| [FINRA duration](https://syndication.finra.org/content/duration-what-interest-rate-hike-could-do-your-bond-portfolio) | Show exact repricing beside duration/convexity approximation. | Duration does not capture default, liquidity or optionality. |
| [New York Fed SOFR](https://www.newyorkfed.org/markets/reference-rates/sofr) | Keep benchmark assumptions explicit. | Overnight SOFR is not Term SOFR; no live market feed is implied. |

These references inform model design. They do not verify any historical company input. The company case continues to use its original 15 May 2025 information cutoff and source register.

## Interface design

The interface is a research workstation: a funding comparison, supporting schedules and a visible evidence boundary. Navigation follows the analytical workflow. Credit Risk exposes a small joint-stress matrix; Rates Lab has a distinct scope and units.

```text
Navigation | Title, timing and export
           | Analysis scope and evidence status
           | Structure / scenario selection
           | Funding comparison and schedules | Model context
```

Palette: olive #20251b, lime #d0ff62, purple #7545f5, lavender #dccbff, paper #ffffff, workspace #f4f5f8, text #25282d. The reference-led layout uses a narrow inset sidebar, separate compact funding cards, a two-column chart grid and a white Model insights rail. A purple Credit Risk shortcut sits beside coverage; it keeps the selected scenario's actual breach text. Purple trends and labelled dashed analytical thresholds retain their model values. The borrowing comparison remains a bar chart: it is not presented as a reconciled funding-composition donut.

Typography uses Segoe UI/system sans-serif and tabular numerals without external requests. Rounded cards have subtle borders; lime actions use dark text. Breaches and evidence limitations retain text labels. All ten sections, native controls, focus outlines, reduced motion and the mobile navigation drawer remain. Insights move below the content on narrower screens. Web exports remain model JSON plus a separate hypothetical bond JSON; Excel and PDF exports use the documented CLI. No calculation or evidence dependency changed for this visual redesign.

## Model scope

Joint stress changes gross margin by 0, −100 or −200 bp and the benchmark by 0, +100 or +200 bp, simultaneously, for each funding structure. It uses the canonical engine and selected timing. The grid holds base assumptions fixed; it is not compounded with the saved scenario selector. A positive minimum cash cushion is insufficient if leverage, coverage or maturity fails.

The rates lab values a hypothetical non-callable bullet bond at a coupon date. For payment frequency m, yield y and cash flow CF at period k:

`P = Σ CF[k] / (1 + y/m)^k`

Modified duration is `−P′/P`, convexity is `P″/P`, and dollar DV01 is `−P′ × 0.0001 × notional/100`. Yield is a flat benchmark plus spread. Consequently rate DV01 and spread CS01 are identical in this deliberately simple model. Their economic risks are not interchangeable. A short benchmark hedge leaves credit-spread, curve, basis and convexity exposure. Contract DV01 is hypothetical and rounding leaves residual exposure.

Maturity is limited to whole years, frequency to 1/2/4 and notional to $10bn. No accrued interest, stub periods, default recovery, options or stochastic dynamics are modelled. These are useful extensions only after their conventions and independent benchmarks are specified.

## Evidence policy remains unchanged

Verified history, conditional public projections and synthetic demonstrations remain separate. No source review is upgraded to independent human sign-off. Unsupported actual-company recommendations remain blocked, even when the standalone rates lab or an individual historical calculation is available. No private information has been obtained by this upgrade.
