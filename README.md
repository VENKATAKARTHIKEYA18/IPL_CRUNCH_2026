# 🏏 IPL CRUNCH '26 — Ball-by-Ball Data Analytics

<div align="center">

![IPL Crunch](https://img.shields.io/badge/IPL%20Crunch-'26-orange?style=for-the-badge&logo=cricket)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Data](https://img.shields.io/badge/Data-Cricsheet.org-green?style=for-the-badge)
![Matches](https://img.shields.io/badge/Matches-1%2C226-red?style=for-the-badge)
![Deliveries](https://img.shields.io/badge/Deliveries-291%2C574-purple?style=for-the-badge)

**Submitted for IPL Crunch '26 by Wooble × Unstop**

*Complete ball-by-ball IPL data analytics — 1,226 real Cricsheet JSON files · 19 seasons · 2007/08 → 2026*

</div>

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Dataset](#-dataset)
- [Key Findings](#-key-findings)
- [Repository Structure](#-repository-structure)
- [How to Run](#-how-to-run)
- [Analysis Questions](#-analysis-questions)
- [Charts & Visualizations](#-charts--visualizations)
- [Tech Stack](#-tech-stack)
- [Results Summary](#-results-summary)

---

## 🎯 Project Overview

This project is a complete data analytics submission for **IPL Crunch '26** — an online data analytics challenge by Wooble where participants analyze real IPL match datasets to uncover patterns, answer high-impact cricket questions, and present insights through charts, analysis, and storytelling.

> *"Everyone has IPL opinions. Very few can back them with data."*

This submission backs every finding with **real ball-by-ball data** parsed directly from **cricsheet.org JSON files** — no synthetic data, no estimates, no hardcoded numbers.

### Questions Answered
1. 🪙 Do teams that win the toss actually win more matches?
2. ⚡ Which phase impacts victory the most — Powerplay, Middle, or Death Overs?
3. 🏅 Who are the top batters and bowlers across all seasons?
4. 🔍 What hidden patterns or surprises can you discover from the data?

---

## 📦 Dataset

| Property | Value |
|---|---|
| **Source** | [cricsheet.org/downloads](https://cricsheet.org/downloads/) — IPL JSON |
| **Format** | Ball-by-ball JSON (one file per match) |
| **Files** | 1,226 JSON files |
| **Seasons** | 2007/08 → 2026 (19 seasons) |
| **Matches parsed** | 1,226 |
| **Valid results** | 1,201 (25 abandoned/no-result excluded) |
| **Deliveries** | 291,574 ball-by-ball records |

### Getting the Data

```bash
# 1. Go to cricsheet.org/downloads
# 2. Download "IPL matches (JSON)" zip
# 3. Extract into this folder:
mkdir cricsheet_json
unzip ipl_json.zip -d cricsheet_json/
```

---

## 🔑 Key Findings

### Q1 — Toss vs Win
> The toss is statistically a coin flip — but the **decision after it** is everything.

| Metric | Value |
|---|---|
| Overall toss win rate | 51.62% |
| p-value (chi-square) | 0.2604 ❌ Not significant |
| **Field first win rate** | **54.77%** ✅ |
| Bat first win rate | 45.43% ❌ Below baseline |
| Decision gap | **9.34 percentage points** |

### Q2 — Phase Impact
> Middle Overs (6–14) are the most decisive phase — not the Death Overs.

| Phase | Overs | RPO | Wkts/Inn | Win Correlation |
|---|---|---|---|---|
| Powerplay | 0–5 | 8.11 | 1.44 | +0.101 ✓ |
| **Middle** | **6–14** | **7.95** | **2.31** | **+0.159 ✓ ← HIGHEST** |
| Death | 15–19 | 10.07 | 2.29 | +0.093 ✓ |

### Q3 — Top Performers

**Top Run-Scorers (Computed from real data)**

| Rank | Batter | Runs | SR | Avg |
|---|---|---|---|---|
| 🥇 | V Kohli | **9,136** | 134.4 | 38.1 |
| 🥈 | RG Sharma | 7,246 | 132.9 | 28.9 |
| 🥉 | S Dhawan | 6,736 | 127.0 | 34.9 |
| 4 | DA Warner | 6,537 | 139.7 | 39.9 |
| 5 | KL Rahul | 5,702 | 139.0 | 44.9 |

**Top Wicket-Takers (Computed from real data)**

| Rank | Bowler | Wickets | Economy | Bowl SR |
|---|---|---|---|---|
| 🥇 | B Kumar | **237** | 7.57 | 19.0 |
| 🥈 | YS Chahal | 234 | 7.91 | 17.0 |
| 🥉 | SP Narine | 225 | **6.79** | 20.4 |
| 4 | JJ Bumrah | 207 | 7.18 | 17.4 |
| 5 | DJ Bravo | 206 | 8.15 | **15.1** |

### Q4 — Hidden Patterns

| Pattern | Finding |
|---|---|
| 🏃 Chase win rate | **54.70%** — Chasing is statistically better |
| 📈 Score inflation | 161 → 188 runs (+27.3 over 19 seasons) |
| 🔴 Dot ball % | Powerplay **46.3%** · Middle 31.8% · Death 28.4% |
| 💡 Key surprise | Toss is a coin flip (p=0.26) but field-first wins **54.77%** |

---

## 📁 Repository Structure

```
ipl-crunch-26/
│
├── 📄 README.md                          ← This file
├── 🐍 ipl_real_analysis.py              ← Main analysis script (Cricsheet parser)
├── 📊 IPL_Crunch_26_Report_REAL.md      ← Full written report
├── 🌐 IPL_Crunch_26_PitchDeck_REAL.html ← Interactive 10-slide pitch deck
│
├── 📂 cricsheet_json/                   ← Place Cricsheet JSON files here
│   ├── 1082591.json
│   ├── 1082592.json
│   └── ... (1,226 files total)
│
└── 📂 ipl_charts/                       ← Generated charts (auto-created)
    ├── 00_dashboard.png
    ├── 01_toss_analysis.png
    ├── 02_phase_analysis.png
    ├── 03_top_batters.png
    ├── 04_top_bowlers.png
    └── 05_hidden_patterns.png
```

---

## 🚀 How to Run

### Prerequisites

```bash
pip install pandas matplotlib seaborn scipy numpy
```

### Steps

```bash
# 1. Clone this repository
git clone https://github.com/yourusername/ipl-crunch-26.git
cd ipl-crunch-26

# 2. Download Cricsheet IPL JSON data
#    → Go to https://cricsheet.org/downloads/
#    → Click "IPL matches (JSON)" and download the zip
#    → Extract into cricsheet_json/ folder

# 3. Run the analysis
python ipl_real_analysis.py

# 4. View outputs
#    → Charts saved to ipl_charts/
#    → Open IPL_Crunch_26_PitchDeck_REAL.html in browser
```

### Expected Output

```
══════════════════════════════════════════════════════════
  IPL CRUNCH '26 — Cricsheet Real Data Pipeline
══════════════════════════════════════════════════════════

  Found 1,226 JSON files — parsing …
  Parsed → 1,226 matches | 291,574 deliveries | 0 skipped

[1/6] Toss analysis …         ✓ ipl_charts/01_toss_analysis.png
[2/6] Phase analysis …        ✓ ipl_charts/02_phase_analysis.png
[3/6] Batter analysis …       ✓ ipl_charts/03_top_batters.png
[4/6] Bowler analysis …       ✓ ipl_charts/04_top_bowlers.png
[5/6] Hidden patterns …       ✓ ipl_charts/05_hidden_patterns.png
[6/6] Executive dashboard …   ✓ ipl_charts/00_dashboard.png
```

---

## 📊 Analysis Questions

### Q1 — Toss Analysis
- Parses `info.toss.winner` and `info.outcome.winner` from every JSON file
- Chi-square goodness-of-fit test to check statistical significance
- Broken down by: decision (bat/field), season trend, venue

### Q2 — Phase Analysis
- Classifies every delivery by over number (0-indexed, Cricsheet format)
- `Powerplay` = overs 0–5 · `Middle` = 6–14 · `Death` = 15–19
- Computes RPO, wickets per innings, dot-ball %, win correlation (Pearson r)

### Q3 — Top Performers
- Aggregates `batsman_runs` per batter across all legal deliveries
- Minimum 500 balls faced (batters) / 500 balls bowled (bowlers)
- Computes: runs, SR, avg, 4s, 6s (batting) · wickets, economy, SR, avg (bowling)

### Q4 — Hidden Patterns
- Season-wise 1st innings score trend (scoring inflation)
- Chase vs defend win rate
- Boundary % per over (all 20 overs)
- Dismissal type distribution

---

## 📈 Charts & Visualizations

| Chart | What It Shows |
|---|---|
| `00_dashboard.png` | Executive summary — all KPIs in one view |
| `01_toss_analysis.png` | Toss win rate donut · bat/field bar · season trend |
| `02_phase_analysis.png` | RPO · wickets · win correlation by phase |
| `03_top_batters.png` | Career runs bar chart · SR vs Average scatter |
| `04_top_bowlers.png` | Career wickets bar chart · Economy vs SR scatter |
| `05_hidden_patterns.png` | Dot ball % · boundary/over · score trend · dismissals |

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.10+** | Core language |
| **pandas** | Data parsing and aggregation |
| **matplotlib** | All chart generation |
| **seaborn** | Chart styling |
| **scipy** | Statistical tests (chi-square, Pearson r) |
| **numpy** | Numerical computations |
| **json / glob** | Cricsheet JSON file loading |

---

## 📊 Results Summary

```
═══════════════════════════════════════════════════════════════════
  IPL CRUNCH '26 — REAL DATA RESULTS  (cricsheet.org)
═══════════════════════════════════════════════════════════════════

📌 Q1 TOSS  (1,201 matches)
   Win rate  : 51.62%   p=0.2604  ✗ NOT significant
   bat       : 45.43%   (n=405)
   field     : 54.77%   (n=796)  ← Always field first

📌 Q2 PHASE
   Powerplay  (0-5)   RPO=8.11  Wkts=1.44  Corr=+0.101 ✓
   Middle     (6-14)  RPO=7.95  Wkts=2.31  Corr=+0.159 ✓ ← DECISIVE
   Death      (15-19) RPO=10.07 Wkts=2.29  Corr=+0.093 ✓

📌 Q3 TOP BATTERS
   V Kohli          9,136 runs  SR=134.4  Avg=38.1
   RG Sharma        7,246 runs  SR=132.9  Avg=28.9
   S Dhawan         6,736 runs  SR=127.0  Avg=34.9
   DA Warner        6,537 runs  SR=139.7  Avg=39.9
   KL Rahul         5,702 runs  SR=139.0  Avg=44.9

📌 Q3 TOP BOWLERS
   B Kumar           237 wkts  Eco=7.57  SR=19.0
   YS Chahal         234 wkts  Eco=7.91  SR=17.0
   SP Narine         225 wkts  Eco=6.79  SR=20.4
   JJ Bumrah         207 wkts  Eco=7.18  SR=17.4
   DJ Bravo          206 wkts  Eco=8.15  SR=15.1

📌 Q4 HIDDEN PATTERNS
   Chase win rate     : 54.70%
   Score inflation    : 161.0 → 188.3 runs (+27.3 over 19 seasons)
   Dot % Powerplay    : 46.3%
   Dot % Middle       : 31.8%
   Dot % Death        : 28.4%

🔑 KEY SURPRISE INSIGHT
   The toss itself is a coin flip (p=0.26).
   But field first wins 54.77% vs bat first at only 45.43%.
   A 9.34% gap from one decision after the flip.
═══════════════════════════════════════════════════════════════════
```

---

## 📜 Submission Details

| Field | Details |
|---|---|
| **Event** | IPL Crunch '26 |
| **Platform** | Wooble × Unstop |
| **Data Source** | [cricsheet.org](https://cricsheet.org/downloads/) |
| **Files submitted** | Code · Report · Pitch Deck · 6 Charts |
| **One Key Insight** | The toss is a coin flip (p=0.26) — but choosing to field after winning it creates a 9.34% win-rate gap (54.77% vs 45.43%) |

---

<div align="center">

**Made with 🏏 and real ball-by-ball data**

*Data: cricsheet.org · Event: IPL Crunch '26 · Wooble × Unstop · May 2026*

</div>
