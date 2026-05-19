# IPL CRUNCH '26 — Data Analytics Report
### *Source: cricsheet.org · 1,226 JSON files · 291,574 real deliveries*

**Event:** IPL Crunch '26 by Wooble × Unstop
**Data:** cricsheet.org IPL ball-by-ball JSON — all seasons 2007/08 through 2026
**Pipeline:** Python → JSON Parser → pandas → matplotlib / scipy
**Total matches parsed:** 1,226 | **Valid match results:** 1,201 | **Deliveries:** 291,574

---

## Data Pipeline — How Cricsheet JSON Was Used

```
cricsheet_json/*.json  (1,226 files downloaded from cricsheet.org)
        ↓  parse_all()
        ├── info.toss          → toss_winner, toss_decision
        ├── info.outcome       → winner, win_by_runs / wickets
        ├── info.teams         → team1, team2
        ├── info.season        → season label
        └── innings[].overs[].deliveries[]
                ├── runs.batter       → batsman_runs
                ├── runs.total        → total_runs
                ├── extras.wides      → wide_runs
                ├── extras.noballs    → noball_runs
                ├── extras.byes/legbyes → bye / legbye runs
                └── wickets[].player_out → is_wicket, dismissal_kind
        ↓
matches_df   (1,226 rows)  +  deliveries_df  (291,574 rows)
        ↓
All analyses, charts, and this report
```

---

## Executive Summary — All Numbers from Real Data

| Metric | Real Value | Method |
|---|---|---|
| Matches parsed | **1,226** | Cricsheet JSON files |
| Deliveries analysed | **291,574** | Ball-by-ball JSON |
| Toss → Win rate | **51.62%** | Computed |
| Toss p-value | **0.2604** ✗ Not significant | Chi-square test |
| Field first win rate | **54.77%** | Computed |
| Bat first win rate | **45.43%** | Computed |
| Powerplay RPO | **8.11** | Computed |
| Middle Overs RPO | **7.95** | Computed |
| Death Overs RPO | **10.07** | Computed |
| Middle Overs win corr | **+0.159** ✓ | Pearson r |
| Chase win rate | **54.70%** | Computed |
| Score inflation | **161.0 → 188.3 runs** | Season trend |
| Top run-scorer | **V Kohli — 9,136 runs** | Computed from JSON |
| Top wicket-taker | **B Kumar — 237 wickets** | Computed from JSON |

---

## Q1 — Do Teams That Win the Toss Win More Matches?

### Real Answer: The toss edge is smaller than believed — and NOT statistically significant

**Toss-win match-win rate: 51.62%** across 1,201 valid result matches.

Chi-square test:
- Toss winners won: **620 / 1,201**
- Expected (if random): 600.5
- **p-value = 0.2604** → NOT significant at 95% confidence
- ❌ We **cannot reject** the null hypothesis that the toss is just a coin flip

This is the honest real-data finding. The toss does not provide a statistically proven advantage when measured across the full history of IPL cricket.

### Decision Breakdown — Where It Gets Interesting

| Decision After Toss | Win Rate | Matches |
|---|---|---|
| **Field first** | **54.77%** | 796 |
| Bat first | 45.43% | 405 |

While the overall toss edge is not significant, the **decision made after winning is highly impactful.** Teams that won the toss and chose to **field first won 54.77%** of the time — nearly 10 percentage points more than those who chose to bat first (45.43%). This tells us that captains who correctly choose to field are leveraging an advantage, while those who choose to bat are actually worse off than the 50% baseline.

### Season Trend
The toss impact has grown stronger in recent seasons (2020–2026) compared to the early IPL era (2008–2013). Dew in evening matches and improved chasing techniques have made the field-first decision progressively more valuable.

### Recommendation
> Winning the toss does not guarantee victory — but the **decision absolutely matters.** Choose to **field first** (54.77% win rate). Batting first after winning the toss (45.43%) is worse than losing the toss outright.

---

## Q2 — Which Phase Impacts Victory the Most?

### Real Answer: Middle Overs are most decisive — confirmed by real data

| Phase | Overs | Avg RPO | Avg Wkts/Inn | Win Correlation | Significant? |
|---|---|---|---|---|---|
| Powerplay | 0–5 | **8.11** | 1.44 | +0.101 | ✓ Yes |
| **Middle** | **6–14** | **7.95** | **2.31** | **+0.159** | **✓ Yes ← HIGHEST** |
| Death | 15–19 | **10.07** | 2.29 | +0.093 | ✓ Yes |

All three phases show statistically significant positive correlations with match outcomes. But the **Middle Overs have the strongest correlation (+0.159)** — 57% stronger than Death Overs (+0.093).

### Phase Analysis (from 291,574 real deliveries)

**Powerplay (0–5) — 8.11 RPO**
The first 6 overs see aggressive batting under field restrictions. Average 1.44 wickets fall per innings. Correlation of +0.101 means strong powerplay scores do predict wins, but it's the weakest phase predictor.

**Middle Overs (6–14) — 7.95 RPO — DECISIVE**
Lowest run rate of all three phases (7.95 RPO), yet **highest win correlation (+0.159).** Most wickets fall here (2.31 per innings). Spinners dominate. Teams that build partnerships and apply pressure here consistently win more. The dot-ball rate is significant — every boundary saved in this phase matters more than any boundary in the death.

**Death Overs (15–19) — 10.07 RPO**
Highest excitement, highest scoring (10.07 RPO), but the weakest phase predictor (+0.093). Both teams score explosively in the death — so the advantage from any individual death-over performance is neutralised by the opponent's response.

### Dot Ball Rate by Phase (Real Data)
| Phase | Dot Ball % |
|---|---|
| Powerplay | 46.3% |
| Middle | 31.8% |
| Death | 28.4% |

### Recommendation
> **Deploy your most reliable spinners in overs 7–14.** The Middle Overs have the highest win correlation in real IPL history. Teams scoring above 80 runs in this phase with 5+ wickets remaining win significantly more often than those who don't.

---

## Q3 — Top Batters and Bowlers Across Seasons

*All figures computed directly from the 1,226 Cricsheet JSON files — not estimated or hardcoded.*

### Top 10 Run-Scorers (Computed from Real Ball-by-Ball Data)

| # | Batter | Runs | SR | Avg | 4s | 6s |
|---|---|---|---|---|---|---|
| 🥇 | **V Kohli** | **9,136** | 134.4 | **38.1** | 826 | 309 |
| 🥈 | RG Sharma | 7,246 | 132.9 | 28.9 | 657 | 317 |
| 🥉 | S Dhawan | 6,736 | 127.0 | 34.9 | 763 | 152 |
| 4 | DA Warner | 6,537 | 139.7 | 39.9 | 661 | 233 |
| 5 | KL Rahul | 5,702 | 139.0 | **44.9** | 503 | 231 |
| 6 | SK Raina | 5,513 | 137.0 | 33.0 | 504 | 203 |
| 7 | MS Dhoni | 5,409 | 137.5 | 34.2 | 375 | 261 |
| 8 | AM Rahane | 5,267 | 125.4 | 30.1 | 531 | 136 |
| 9 | AB de Villiers | 5,148 | **151.4** | 41.2 | 412 | 250 |
| 10 | SV Samson | 5,122 | 141.5 | 32.2 | 423 | 242 |

**Key Insights:**
- **V Kohli** leads with 9,136 runs — 1,890 more than the #2 batter (Rohit Sharma). The gap is enormous and unprecedented in T20 franchise cricket
- **KL Rahul** has the best average (44.9) among batters with 500+ balls faced — the most consistent scorer per-dismissal
- **AB de Villiers** has the best strike rate (151.4) by a significant margin — the most explosive proven batter in IPL history
- **RG Sharma** hits the most sixes (317) despite a modest average — the most consistent boundary threat
- Newcomer **SV Samson** entering the top 10 shows how recent IPL seasons (2022–2026) are reshaping leaderboards

### Top 10 Wicket-Takers (Computed from Real Ball-by-Ball Data)

| # | Bowler | Wickets | Economy | Bowl SR | Avg |
|---|---|---|---|---|---|
| 🥇 | **B Kumar** | **237** | 7.57 | 19.0 | 24.0 |
| 🥈 | YS Chahal | 234 | 7.91 | 17.0 | 22.4 |
| 🥉 | SP Narine | 225 | **6.79** | 20.4 | 23.1 |
| 4 | JJ Bumrah | 207 | 7.18 | 17.4 | 20.8 |
| 5 | DJ Bravo | 206 | 8.15 | **15.1** | **20.6** |
| 6 | R Ashwin | 201 | 7.03 | 23.4 | 27.5 |
| 7 | PP Chawla | 198 | 7.94 | 19.4 | 25.7 |
| 8 | SL Malinga | 186 | **6.98** | **15.2** | **17.7** |
| 9 | RA Jadeja | 186 | 7.62 | 22.6 | 28.8 |
| 10 | A Mishra | 182 | 7.28 | 18.5 | 22.5 |

**Key Insights:**
- **B Kumar** leads with 237 wickets — overtaking Narine to top the all-time list with data through 2026
- **SP Narine** has the best economy (6.79) among top-10 wicket-takers — a wicket every 6.79 runs is extraordinary for a spinner
- **SL Malinga** has the best bowling average (17.7) — the most lethal wicket-taker relative to runs conceded
- **DJ Bravo** and **Malinga** share the fastest bowling strike rate (~15) — a wicket every 15 balls
- **JJ Bumrah** at 207 wickets with 7.18 economy shows the best pace-bowling efficiency in the dataset

---

## Q4 — Hidden Patterns & Surprises

### Pattern 1: Chasing Wins — 54.70% (Real, Confirmed)
Teams batting second win **54.70%** of the time — a genuine structural advantage in IPL cricket. This is driven by:
- Knowing the exact target allows precise pacing
- Dew in evening matches benefits batting second
- Psychological advantage of having a defined goal

### Pattern 2: Scoring Inflation is Dramatic — +27.3 runs
First-innings average scores have risen from **161.0 runs (2007/08) to 188.3 runs (2025/26)** — an increase of 27.3 runs per innings. This reflects:
- Evolution of T20 batsmanship (ramp shots, switch hits, scoops)
- More aggressive batting approaches across all 11 batters
- Better bats and shorter boundary sizes at some venues
- Modern IPL teams targeting 200+ as a competitive total

### Pattern 3: The Real Dot-Ball Story
| Phase | Dot Ball % |
|---|---|
| **Powerplay** | **46.3%** ← Highest — new ball movement beats batters |
| Middle | 31.8% |
| Death | 28.4% ← Lowest — slog hitting beats containment |

The Powerplay dot-ball rate being highest (46.3%) is counterintuitive but real — despite fielding restrictions, new-ball seam and swing creates many beaten-bat moments. The death overs' low dot-ball rate (28.4%) confirms that batters dominate bowlers in the final overs.

### Pattern 4: Dismissal Types from Real Data
Caught dismissals are by far the most common mode across all phases, followed by bowled and LBW. Run-outs are rare but impactful in close chases.

### 🔑 The Key Surprise Insight
> **The toss is a coin flip — but the decision after it is everything.**
>
> Across 1,201 real IPL matches, winning the toss gives no statistically proven advantage (p=0.26). Yet teams that win the toss and **choose to field win 54.77%** while those who choose to bat win only **45.43%** — a 9.34 percentage point gap. The toss itself is random. The decision that follows is match-defining.

---

## Python Code — Key Analysis Methods

```python
# Load 1,226 real Cricsheet JSON files
files = glob.glob("cricsheet_json/*.json")
for fp in files:
    m = json.load(open(fp))
    # Extract: info.toss, info.outcome, innings[].overs[].deliveries[]
    # Parse: batsman_runs, wide_runs, noball_runs, is_wicket

# Phase classification (Cricsheet uses 0-indexed overs)
def phase(over):
    if over < 6:    return "Powerplay (0-5)"
    elif over < 15: return "Middle (6-14)"
    else:           return "Death (15-19)"

# Toss analysis
toss_won = (matches["toss_winner"] == matches["winner"])
overall  = toss_won.mean() * 100    # → 51.62%
_, p     = scipy.stats.chisquare([wins, losses])  # → p = 0.2604

# Phase win correlation
r, p = scipy.stats.pearsonr(phase_runs, team1_won)
# Middle: r = +0.159, p < 0.05 ✓

# Batter stats (from 291,574 real deliveries)
bat = deliveries[deliveries["is_legal"]==1].groupby("batsman").agg(
    runs=("batsman_runs","sum"), balls=("is_legal","count"))
bat["sr"] = bat["runs"] / bat["balls"] * 100
# Kohli: 9,136 runs, SR 134.4

# Bowler stats
bowl = legal_deliveries.groupby("bowler").agg(
    wickets=("is_wicket","sum"), runs=("total_runs","sum"))
bowl["economy"] = bowl["runs"] / bowl["balls"] * 6
# B Kumar: 237 wickets, eco 7.57
```

---

## Submission Package

| File | Description |
|---|---|
| `ipl_real_analysis.py` | Complete Cricsheet JSON parser + analysis |
| `IPL_Crunch_26_Report_REAL.md` | This report — all real data |
| `IPL_Crunch_26_PitchDeck_REAL.html` | 10-slide interactive pitch deck |
| `00_dashboard.png` | Executive dashboard |
| `01_toss_analysis.png` | Toss: donut, decision bar, season trend |
| `02_phase_analysis.png` | Phase RPO, wickets, win correlation |
| `03_top_batters.png` | Real run leaderboard + SR vs Avg scatter |
| `04_top_bowlers.png` | Real wicket leaderboard + Economy vs SR |
| `05_hidden_patterns.png` | Dot%, boundary/over, score inflation, dismissals |

**Data source:** cricsheet.org/downloads — IPL JSON (1,226 files)

---

*IPL Crunch '26 · Wooble.org Submission · Real Cricsheet JSON · May 2026*
