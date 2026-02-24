# Premier League: Reality vs Expectations

A storytelling-first Power BI project that asks one question:

**Who is truly performing well, and who is riding short-term variance?**

This dashboard combines match forecasts, event-level shot data, and fixture context to turn football performance into clear actions for analysts, coaches, and recruitment teams.

## Match Story Arc

The report is structured as a four-page narrative:

1. **Executive Summary (Why)**
   - Actual vs expected points
   - Team-level points delta
   - Monthly points-delta trend

2. **Drivers (What)**
   - Relationship between finishing (`Goals - xG`) and points delta
   - Team output table and trend view

3. **2015/16 Deep Dive (How)**
   - StatsBomb event-level breakdown
   - Shot profile, big chances, conversion, goals vs xG

4. **What-If / Action (What if)**
   - Regression-to-mean parameter
   - Projected points after regression
   - Practical decision rule for risk/opportunity

## Dashboard Preview


<img width="1512" height="982" alt="Screenshot 2026-02-23 at 11 19 06 PM" src="https://github.com/user-attachments/assets/7adab15e-bcd8-469c-ba43-077cbfc46d19" />
<img width="1512" height="982" alt="Screenshot 2026-02-23 at 11 19 13 PM" src="https://github.com/user-attachments/assets/8de5c052-6328-4bfa-a634-9c4b3aea4deb" />
<img width="1512" height="982" alt="Screenshot 2026-02-23 at 11 06 47 PM" src="https://github.com/user-attachments/assets/658226bb-c2ac-4b42-b607-1ae1fc3c6562" />
<img width="1512" height="982" alt="Screenshot 2026-02-23 at 11 19 21 PM" src="https://github.com/user-attachments/assets/7dca30b8-4ed4-43b2-ba9b-23f0b1fab54c" />


## Data Sources

This project is built from three public football datasets:

- **FiveThirtyEight SPI**: match-level forecasts, projected scores, probabilities, xG
- **StatsBomb Open Data**: event-level JSON for deep-dive shot and chance analysis
- **OpenFootball (England)**: fixture and results context for Premier League structure

### Source Links

- FiveThirtyEight SPI: [https://datahub.io/core/five-thirty-eight-datasets/datasets/soccer-spi](https://datahub.io/core/five-thirty-eight-datasets/datasets/soccer-spi)
- StatsBomb Open Data: [https://github.com/statsbomb/open-data](https://github.com/statsbomb/open-data)
- OpenFootball England: [https://github.com/openfootball/england](https://github.com/openfootball/england)

## Data Engineering and Cleaning

Data prep was handled in Python and Power BI to ensure model consistency and reliable cross-source joins.

### Key cleaning and transformation steps

- Standardized team naming across all sources (`newcastle` -> `Newcastle United`, `arsenal fc` -> `Arsenal`, etc.)
- Filtered SPI to Premier League (`league_id = 2411`)
- Built season labels from match dates (`YYYY/YY` format)
- Calculated **expected points** per match from probabilities:
  - `Expected Points = 3 * Win Probability + 1 * Draw Probability`
- Converted match-level tables into **team-match grain** for robust slicing and aggregation
- Parsed StatsBomb events for Premier League 2015/16 and aggregated:
  - shots
  - goals
  - xG
  - big chances (`xG >= 0.30`)
- Built `dim_date` and `dim_team` dimensions for semantic model relationships

## Core Metrics

- **SPI Expected Points**
- **SPI Actual Points**
- **SPI Points Delta**
- **SPI Points Delta per Match**
- **SPI Goals minus xG**
- **SB Goals minus xG**
- **SB Shot Conversion**
- **Projected Points (After Regression)**

## Repository Structure

```text
.
|-- Assignment_3.pbix
|-- README.md
|-- data/
|   |-- raw/
|   |-- processed/
|       |-- dim_date.csv
|       |-- dim_team.csv
|       |-- spi_pl_matches.csv
|       |-- spi_pl_team_match.csv
|       |-- statsbomb_pl2015_matches.csv
|       |-- statsbomb_pl2015_team_match.csv
|       |-- openfootball_pl2015_matches.csv
|-- scripts/
|   |-- build_dataset.py
|-- screenshots/
|   |-- 01-executive-summary.png
|   |-- 02-drivers-what.png
|   |-- 03-deep-dive-how.png
|   |-- 04-what-if-action.png
```

## How to Reproduce

1. Download the raw files into `data/raw/`
2. Run the build script:

```bash
python3 scripts/build_dataset.py
```

3. Open `Assignment_3.pbix`
4. Refresh the model in Power BI Desktop

## What To Upload In This Repository

At minimum, upload:

- `README.md`
- `Assignment_3.pbix`
- `scripts/build_dataset.py`
- `data/processed/*.csv`
- `screenshots/*.png`

Strongly recommended additions:

- `docs/data-dictionary.md` (column definitions for each table)
- `docs/dax-measures.md` (all DAX formulas used)
- `docs/story-script.md` (your narration script for the video)
- `presentation/video-link.txt` (YouTube/Drive link to final walkthrough)
- `.gitignore` (exclude cache and temp files)

Optional but useful:

- `requirements.txt` (if you later add Python dependencies)
- `LICENSE` (for your repo code)
- `ATTRIBUTION.md` (dataset credits and usage terms)

## Attribution and Usage Notes

- StatsBomb open data requires attribution when used in public work.
- Respect each source's licensing and usage terms.
- This repository is for educational and analytical use.

---

If you use this project as a base, keep the storytelling sequence:

**Why -> What -> How -> What if -> Action.**

That structure is what makes the dashboard decision-ready.
