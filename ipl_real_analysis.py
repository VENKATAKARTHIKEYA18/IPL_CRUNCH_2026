"""
IPL CRUNCH '26 — Real Cricsheet JSON Analysis
==============================================
Data  : cricsheet.org IPL JSON (1,226 matches, all seasons)
Author: Senior Sports Data Scientist
"""

import os, json, glob, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from collections import defaultdict

warnings.filterwarnings("ignore")

JSON_DIR = "cricsheet_json"
OUT      = "ipl_charts"
os.makedirs(OUT, exist_ok=True)

# ── Palette ────────────────────────────────────────────────────────────────
GOLD="#f5a623"; TEAL="#00b4d8"; RED="#e63946"
GREEN="#2ec4b6"; LIGHT="#f8f9fa"; DARK="#0d1b2a"; MUTED="#7a8aa0"

plt.rcParams.update({
    "figure.facecolor":DARK,  "axes.facecolor":"#111827",
    "axes.edgecolor":"#2d3748","axes.labelcolor":LIGHT,
    "xtick.color":LIGHT,      "ytick.color":LIGHT,
    "text.color":LIGHT,       "grid.color":"#2d3748",
    "grid.linestyle":"--",    "grid.alpha":0.5,
    "font.family":"DejaVu Sans",
    "axes.titlesize":13,      "axes.labelsize":10,
})

# ══════════════════════════════════════════════════════════════════════════
# 1. PARSE REAL CRICSHEET JSON FILES
# ══════════════════════════════════════════════════════════════════════════

def parse_all(json_dir):
    files = glob.glob(os.path.join(json_dir, "*.json"))
    print(f"  Found {len(files)} JSON files — parsing …")

    match_rows, del_rows = [], []
    mid = 0
    skipped = 0

    for fp in sorted(files):
        try:
            with open(fp, encoding="utf-8") as fh:
                m = json.load(fh)
        except Exception:
            skipped += 1
            continue

        info    = m.get("info", {})
        outcome = info.get("outcome", {})
        teams   = info.get("teams", [])
        toss    = info.get("toss", {})
        season  = str(info.get("season", ""))
        venue   = info.get("venue", info.get("city", "Unknown"))
        date    = info.get("dates", [""])[0]

        if len(teams) < 2:
            skipped += 1
            continue

        winner   = outcome.get("winner", "no result")
        by       = outcome.get("by", {})
        by_runs  = by.get("runs", 0)
        by_wkts  = by.get("wickets", 0)

        match_rows.append({
            "match_id":      mid,
            "season":        season,
            "date":          date,
            "venue":         venue,
            "team1":         teams[0],
            "team2":         teams[1],
            "toss_winner":   toss.get("winner", ""),
            "toss_decision": toss.get("decision", ""),
            "winner":        winner,
            "win_by_runs":   by_runs,
            "win_by_wickets":by_wkts,
        })

        for inn_idx, innings in enumerate(m.get("innings", [])):
            bat_team  = innings.get("team", "")
            bowl_team = [t for t in teams if t != bat_team]
            bowl_team = bowl_team[0] if bowl_team else ""

            for over_data in innings.get("overs", []):
                over_num = int(over_data.get("over", 0))

                for ball_idx, d in enumerate(over_data.get("deliveries", [])):
                    runs_d  = d.get("runs", {})
                    extras_d= d.get("extras", {})
                    wickets = d.get("wickets", [])

                    wide_r = extras_d.get("wides",   0)
                    nb_r   = extras_d.get("noballs", 0)
                    bye_r  = extras_d.get("byes",    0)
                    lb_r   = extras_d.get("legbyes", 0)
                    pen_r  = extras_d.get("penalty", 0)
                    extra_r= wide_r + nb_r + bye_r + lb_r + pen_r

                    is_legal = int(wide_r == 0 and nb_r == 0)
                    dismissed= len(wickets) > 0
                    p_out    = wickets[0].get("player_out","") if dismissed else ""
                    d_kind   = wickets[0].get("kind","")       if dismissed else ""

                    bat_r   = runs_d.get("batter", 0)
                    total_r = runs_d.get("total",  0)

                    del_rows.append({
                        "match_id":       mid,
                        "inning":         inn_idx + 1,
                        "season":         season,
                        "date":           date,
                        "batting_team":   bat_team,
                        "bowling_team":   bowl_team,
                        "over":           over_num,
                        "ball":           ball_idx + 1,
                        "batsman":        d.get("batter", ""),
                        "bowler":         d.get("bowler", ""),
                        "batsman_runs":   bat_r,
                        "extra_runs":     extra_r,
                        "total_runs":     total_r,
                        "wide_runs":      wide_r,
                        "noball_runs":    nb_r,
                        "bye_runs":       bye_r,
                        "legbye_runs":    lb_r,
                        "is_legal":       is_legal,
                        "is_wicket":      int(dismissed),
                        "player_dismissed": p_out,
                        "dismissal_kind": d_kind,
                    })
        mid += 1

    matches    = pd.DataFrame(match_rows)
    deliveries = pd.DataFrame(del_rows)
    print(f"  Parsed → {len(matches)} matches | {len(deliveries):,} deliveries "
          f"| {skipped} skipped")
    return matches, deliveries

# ══════════════════════════════════════════════════════════════════════════
# 2. ANALYSIS
# ══════════════════════════════════════════════════════════════════════════

def phase(over):
    if over < 6:    return "Powerplay (0-5)"
    elif over < 15: return "Middle (6-14)"
    else:           return "Death (15-19)"

# ── Toss ──────────────────────────────────────────────────────────────────
def analyse_toss(matches):
    df = matches[matches["winner"] != "no result"].copy()
    df["toss_won"] = (df["toss_winner"] == df["winner"]).astype(int)

    overall   = df["toss_won"].mean() * 100
    n_matches = len(df)

    by_dec = (df.groupby("toss_decision")["toss_won"]
                .agg(win_pct="mean", n="count").reset_index())
    by_dec["win_pct"] *= 100

    # season trend
    by_season = (df.groupby("season")["toss_won"]
                   .agg(win_pct="mean", n="count").reset_index())
    by_season["win_pct"] *= 100
    by_season = by_season[by_season["n"] >= 10].sort_values("season")

    # venue (top venues only)
    by_venue = (df.groupby("venue")["toss_won"]
                  .agg(win_pct="mean", n="count").reset_index())
    by_venue = by_venue[by_venue["n"] >= 15].sort_values("win_pct", ascending=False).head(10)
    by_venue["win_pct"] *= 100

    wins = df["toss_won"].sum()
    _, p = stats.chisquare([wins, n_matches - wins])
    return dict(overall=overall, n=n_matches, by_dec=by_dec,
                by_season=by_season, by_venue=by_venue, p_val=p)

# ── Phase ─────────────────────────────────────────────────────────────────
def analyse_phases(deliveries, matches):
    df = deliveries.copy()
    df["phase"] = df["over"].apply(phase)

    # RPO & wickets per innings per phase
    ph_inn = (df.groupby(["match_id","inning","phase"])
                .agg(runs=("total_runs","sum"),
                     legal=("is_legal","sum"),
                     wkts=("is_wicket","sum"))
                .reset_index())
    ph_inn["rpo"] = ph_inn["runs"] / ph_inn["legal"].replace(0, np.nan) * 6

    ph_agg = (ph_inn.groupby("phase")
                    .agg(avg_rpo=("rpo","mean"),
                         avg_wkts=("wkts","mean"),
                         n=("rpo","count"))
                    .reset_index())

    # win correlation
    piv = (ph_inn[ph_inn["inning"]==1]
           .pivot_table(index="match_id", columns="phase",
                        values="runs", aggfunc="sum")
           .reset_index())
    piv = piv.merge(matches[["match_id","winner","team1"]],
                    on="match_id", how="inner")
    piv = piv[piv["winner"] != "no result"]
    piv["team1_won"] = (piv["winner"] == piv["team1"]).astype(int)
    ph_cols = [c for c in ["Powerplay (0-5)","Middle (6-14)","Death (15-19)"]
               if c in piv.columns]
    corrs = {}
    for c in ph_cols:
        r, p = stats.pearsonr(piv[c].fillna(0), piv["team1_won"])
        corrs[c] = (round(float(r), 3), round(float(p), 4))

    # dot balls & boundaries per over
    df["is_dot"]      = ((df["total_runs"]==0)&(df["is_legal"]==1)).astype(int)
    df["is_boundary"] = df["batsman_runs"].isin([4,6]).astype(int)
    dot_phase  = df[df["is_legal"]==1].groupby("phase")["is_dot"].mean()*100
    bnd_over   = df.groupby("over")["is_boundary"].mean()*100

    return dict(ph_agg=ph_agg, corrs=corrs,
                dot_phase=dot_phase, bnd_over=bnd_over)

# ── Batters (from real parsed data) ────────────────────────────────────────
def analyse_batters(deliveries):
    df = deliveries[deliveries["is_legal"]==1].copy()
    bat = (df.groupby("batsman")
             .agg(runs       =("batsman_runs","sum"),
                  balls      =("is_legal","count"),
                  fours      =("batsman_runs", lambda x: (x==4).sum()),
                  sixes      =("batsman_runs", lambda x: (x==6).sum()),
                  dismissals =("is_wicket","sum"))
             .reset_index())
    bat["sr"]  = (bat["runs"] / bat["balls"] * 100).round(2)
    bat["avg"] = np.where(bat["dismissals"]>0,
                          bat["runs"]/bat["dismissals"], bat["runs"])
    bat["avg"] = bat["avg"].round(2)
    bat = bat[bat["balls"] >= 500].sort_values("runs", ascending=False).head(15)
    return bat

# ── Bowlers (from real parsed data) ────────────────────────────────────────
def analyse_bowlers(deliveries):
    df = deliveries[
        (deliveries["wide_runs"]==0)&(deliveries["noball_runs"]==0)
    ].copy()
    bowl = (df.groupby("bowler")
              .agg(wickets=("is_wicket","sum"),
                   runs   =("total_runs","sum"),
                   balls  =("is_legal","count"))
              .reset_index())
    bowl["economy"] = (bowl["runs"] / bowl["balls"] * 6).round(2)
    bowl["bowl_sr"] = np.where(bowl["wickets"]>0,
                               bowl["balls"]/bowl["wickets"], 9999)
    bowl["bowl_sr"] = bowl["bowl_sr"].round(1)
    bowl["avg"]     = np.where(bowl["wickets"]>0,
                               bowl["runs"]/bowl["wickets"], 9999)
    bowl["avg"]     = bowl["avg"].round(2)
    bowl = bowl[bowl["balls"]>=500].sort_values("wickets",ascending=False).head(15)
    return bowl

# ── Scores trend & chase ───────────────────────────────────────────────────
def analyse_scores(deliveries, matches):
    inn1 = (deliveries[deliveries["inning"]==1]
            .groupby("match_id")["total_runs"].sum()
            .reset_index(name="inn1_score"))
    merged = matches.merge(inn1, on="match_id", how="left")
    trend  = (merged.groupby("season")["inn1_score"]
                    .agg(avg="mean", n="count").reset_index())
    trend  = trend[trend["n"]>=10].sort_values("season")

    m = matches[matches["winner"]!="no result"].copy()
    # bat-first team
    bat_first = np.where(
        ((m["toss_decision"]=="bat")   & (m["toss_winner"]==m["team1"])) |
        ((m["toss_decision"]=="field") & (m["toss_winner"]==m["team2"])),
        m["team1"], m["team2"])
    m["chase_won"] = (m["winner"] != bat_first).astype(int)
    chase_pct = m["chase_won"].mean()*100

    # dismissal kinds
    dk = (deliveries[deliveries["is_wicket"]==1]
          .groupby("dismissal_kind")["is_wicket"].count()
          .sort_values(ascending=False).head(8))
    return dict(trend=trend, chase_pct=chase_pct, dismissal_kinds=dk)

# ══════════════════════════════════════════════════════════════════════════
# 3. CHARTS
# ══════════════════════════════════════════════════════════════════════════

def save(name):
    p = f"{OUT}/{name}"
    plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=DARK)
    plt.close()
    print(f"  ✓ {p}")

# ── Chart 1 — Toss ─────────────────────────────────────────────────────────
def chart_toss(t):
    fig, axes = plt.subplots(1,3,figsize=(18,6))
    fig.patch.set_facecolor(DARK)
    fig.suptitle("🏏  Q1 · TOSS vs MATCH WIN  —  Real Cricsheet Data",
                 fontsize=16, color=GOLD, fontweight="bold", y=1.02)

    # donut
    ax=axes[0]; ax.set_facecolor("#111827")
    p=t["overall"]
    ax.pie([p,100-p], colors=[GOLD,"#2d3748"], startangle=90,
           wedgeprops=dict(width=0.55,edgecolor=DARK))
    ax.text(0, 0.1, f"{p:.1f}%", ha="center",va="center",
            fontsize=26,fontweight="bold",color=GOLD)
    ax.text(0,-0.2, f"n={t['n']:,} matches",ha="center",va="center",
            fontsize=8.5,color=MUTED)
    sig = "p={:.3f} ✓".format(t["p_val"]) if t["p_val"]<0.05 \
          else "p={:.3f}".format(t["p_val"])
    ax.text(0,-0.38, sig, ha="center",va="center",fontsize=8,color=GREEN)
    ax.set_title("Overall Toss → Win Rate",color=LIGHT,pad=10)

    # decision bar
    ax=axes[1]; ax.set_facecolor("#111827")
    dd=t["by_dec"].sort_values("toss_decision")
    cols=[GOLD if d=="bat" else TEAL for d in dd["toss_decision"]]
    bars=ax.bar(dd["toss_decision"],dd["win_pct"],color=cols,width=0.45,edgecolor=DARK)
    for b,row in zip(bars,dd.itertuples()):
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.5,
                f"{b.get_height():.1f}%\n(n={row.n})",
                ha="center",color=LIGHT,fontweight="bold",fontsize=10)
    ax.axhline(50,color=RED,ls="--",alpha=0.7,lw=1.2,label="50% baseline")
    ax.set_ylim(0,72); ax.set_ylabel("Win % when toss won")
    ax.set_title("Bat vs Field After Winning Toss",color=LIGHT)
    ax.legend(fontsize=8); ax.grid(axis="y")

    # season trend
    ax=axes[2]; ax.set_facecolor("#111827")
    ss=t["by_season"]
    x=range(len(ss))
    ax.plot(x,ss["win_pct"],color=GOLD,lw=2.5,marker="o",ms=5)
    ax.fill_between(x,ss["win_pct"],alpha=0.15,color=GOLD)
    ax.axhline(50,color=RED,ls="--",alpha=0.6,lw=1.2)
    ax.set_xticks(x)
    ax.set_xticklabels(ss["season"].tolist(),rotation=45,fontsize=7)
    ax.set_ylabel("Toss-win → Match-win %")
    ax.set_title("Season-wise Toss Impact Trend",color=LIGHT)
    ax.grid(axis="y")

    plt.tight_layout(); save("01_toss_analysis.png")

# ── Chart 2 — Phase ────────────────────────────────────────────────────────
def chart_phases(ph):
    fig,axes=plt.subplots(1,3,figsize=(18,6))
    fig.patch.set_facecolor(DARK)
    fig.suptitle("⚡  Q2 · PHASE IMPACT  —  Real Cricsheet Ball-by-Ball Data",
                 fontsize=16,color=GOLD,fontweight="bold",y=1.02)
    order =["Powerplay (0-5)","Middle (6-14)","Death (15-19)"]
    labels=["Powerplay","Middle","Death"]
    cols  =[TEAL,GOLD,RED]
    agg   =ph["ph_agg"].set_index("phase").reindex(order)

    # RPO
    ax=axes[0]; ax.set_facecolor("#111827")
    bars=ax.bar(labels,agg["avg_rpo"],color=cols,edgecolor=DARK,width=0.5)
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.03,
                f"{b.get_height():.2f}",ha="center",color=LIGHT,
                fontweight="bold",fontsize=12)
    ax.set_ylabel("Avg Runs Per Over (RPO)")
    ax.set_title("Run Rate by Phase",color=LIGHT); ax.grid(axis="y")

    # Wickets
    ax=axes[1]; ax.set_facecolor("#111827")
    bars=ax.bar(labels,agg["avg_wkts"],color=cols,edgecolor=DARK,width=0.5)
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.01,
                f"{b.get_height():.2f}",ha="center",color=LIGHT,
                fontweight="bold",fontsize=12)
    ax.set_ylabel("Avg Wickets per Innings")
    ax.set_title("Wickets Fallen by Phase",color=LIGHT); ax.grid(axis="y")

    # Win correlation
    ax=axes[2]; ax.set_facecolor("#111827")
    corr_vals=[ph["corrs"].get(o,(0,1))[0] for o in order]
    p_vals   =[ph["corrs"].get(o,(0,1))[1] for o in order]
    bar_cols =[GREEN if v>0 else RED for v in corr_vals]
    bars=ax.barh(labels,corr_vals,color=bar_cols,edgecolor=DARK)
    for b,v,p in zip(bars,corr_vals,p_vals):
        sig="✓" if p<0.05 else ""
        ax.text(v+0.002 if v>=0 else v-0.002,
                b.get_y()+b.get_height()/2,
                f"{v:+.3f} {sig}",va="center",
                ha="left" if v>=0 else "right",
                color=LIGHT,fontweight="bold",fontsize=10)
    ax.axvline(0,color=LIGHT,lw=0.8)
    ax.set_xlabel("Pearson r with Match Outcome")
    best=labels[corr_vals.index(max(corr_vals,key=abs))]
    ax.set_title(f"Phase → Win Correlation\n★ Most decisive: {best}",
                 color=LIGHT,fontsize=11)
    ax.grid(axis="x")

    plt.tight_layout(); save("02_phase_analysis.png")

# ── Chart 3 — Top Batters (real computed) ─────────────────────────────────
def chart_batters(bat):
    fig,axes=plt.subplots(1,2,figsize=(17,7))
    fig.patch.set_facecolor(DARK)
    fig.suptitle("🏏  Q3 · TOP BATTERS — Computed from Real Cricsheet JSON",
                 fontsize=14,color=GOLD,fontweight="bold",y=1.01)

    top10=bat.head(10).sort_values("runs")
    cmap=plt.cm.YlOrRd(np.linspace(0.35,0.95,len(top10)))

    ax=axes[0]; ax.set_facecolor("#111827")
    bars=ax.barh(top10["batsman"],top10["runs"],color=cmap,edgecolor=DARK)
    for b in bars:
        ax.text(b.get_width()+30,b.get_y()+b.get_height()/2,
                f"{int(b.get_width()):,}",va="center",
                color=LIGHT,fontsize=8.5,fontweight="bold")
    ax.set_xlabel("Total IPL Runs (from real data)")
    ax.set_title("Top 10 Run-Scorers",color=LIGHT); ax.grid(axis="x")

    ax=axes[1]; ax.set_facecolor("#111827")
    sc=ax.scatter(bat["sr"],bat["avg"],s=bat["runs"]/10,
                  c=bat["runs"],cmap="YlOrRd",
                  edgecolors=DARK,lw=0.5,alpha=0.92)
    for _,r in bat.iterrows():
        ax.annotate(r["batsman"].split()[-1],(r["sr"],r["avg"]),
                    fontsize=8,color=LIGHT,xytext=(4,2),
                    textcoords="offset points")
    ax.axvline(bat["sr"].median(),color=TEAL,ls="--",alpha=0.6,lw=1)
    ax.axhline(bat["avg"].median(),color=GOLD,ls="--",alpha=0.6,lw=1)
    ax.set_xlabel("Strike Rate"); ax.set_ylabel("Batting Average")
    ax.set_title("SR vs Average  (bubble ∝ total runs)",color=LIGHT)
    plt.colorbar(sc,ax=ax,label="Total Runs"); ax.grid()

    plt.tight_layout(); save("03_top_batters.png")

# ── Chart 4 — Top Bowlers (real computed) ─────────────────────────────────
def chart_bowlers(bowl):
    fig,axes=plt.subplots(1,2,figsize=(17,7))
    fig.patch.set_facecolor(DARK)
    fig.suptitle("🎯  Q3 · TOP BOWLERS — Computed from Real Cricsheet JSON",
                 fontsize=14,color=GOLD,fontweight="bold",y=1.01)

    top10=bowl.head(10).sort_values("wickets")
    cmap=plt.cm.cool(np.linspace(0.35,0.95,len(top10)))

    ax=axes[0]; ax.set_facecolor("#111827")
    bars=ax.barh(top10["bowler"],top10["wickets"],color=cmap,edgecolor=DARK)
    for b in bars:
        ax.text(b.get_width()+0.3,b.get_y()+b.get_height()/2,
                int(b.get_width()),va="center",
                color=LIGHT,fontsize=8.5,fontweight="bold")
    ax.set_xlabel("Total IPL Wickets (from real data)")
    ax.set_title("Top 10 Wicket-Takers",color=LIGHT); ax.grid(axis="x")

    ax=axes[1]; ax.set_facecolor("#111827")
    b2=bowl[bowl["bowl_sr"]<200]
    sc=ax.scatter(b2["economy"],b2["bowl_sr"],
                  s=b2["wickets"]*2.2,c=b2["wickets"],
                  cmap="cool",edgecolors=DARK,lw=0.5,alpha=0.92)
    for _,r in b2.iterrows():
        ax.annotate(r["bowler"].split()[-1],(r["economy"],r["bowl_sr"]),
                    fontsize=8,color=LIGHT,xytext=(4,2),
                    textcoords="offset points")
    ax.set_xlabel("Economy Rate (RPO)")
    ax.set_ylabel("Bowling SR (balls/wkt — lower = better)")
    ax.set_title("Economy vs SR  (bubble ∝ wickets)",color=LIGHT)
    ax.invert_yaxis()
    plt.colorbar(sc,ax=ax,label="Wickets"); ax.grid()

    plt.tight_layout(); save("04_top_bowlers.png")

# ── Chart 5 — Hidden Patterns ──────────────────────────────────────────────
def chart_hidden(ph, sc_data):
    fig,axes=plt.subplots(2,2,figsize=(16,12))
    fig.patch.set_facecolor(DARK)
    fig.suptitle("🔍  Q4 · HIDDEN PATTERNS — Real Ball-by-Ball Data",
                 fontsize=16,color=GOLD,fontweight="bold",y=1.01)
    order =["Powerplay (0-5)","Middle (6-14)","Death (15-19)"]
    labels=["Powerplay","Middle","Death"]

    # Dot-ball %
    ax=axes[0][0]; ax.set_facecolor("#111827")
    dp=ph["dot_phase"].reindex(order)
    bars=ax.bar(labels,dp.values,color=[TEAL,GOLD,RED],edgecolor=DARK,width=0.5)
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.3,
                f"{b.get_height():.1f}%",ha="center",
                color=LIGHT,fontweight="bold",fontsize=11)
    ax.set_ylabel("Dot Ball %")
    ax.set_title("Dot Ball % by Phase",color=LIGHT); ax.grid(axis="y")

    # Boundary % per over
    ax=axes[0][1]; ax.set_facecolor("#111827")
    bo=ph["bnd_over"].reindex(range(20)).fillna(0)
    ax.bar(bo.index,bo.values,
           color=[TEAL if o<6 else(GOLD if o<15 else RED) for o in bo.index],
           edgecolor=DARK,width=0.85)
    ax.axvline(5.5,color=LIGHT,ls=":",alpha=0.5,lw=1)
    ax.axvline(14.5,color=LIGHT,ls=":",alpha=0.5,lw=1)
    ax.set_xlabel("Over (0-indexed)"); ax.set_ylabel("Boundary %")
    ax.set_title("Boundary % per Over  (PP=teal · Mid=gold · Death=red)",
                 color=LIGHT); ax.grid(axis="y")

    # 1st-innings score trend
    ax=axes[1][0]; ax.set_facecolor("#111827")
    tr=sc_data["trend"]
    x=range(len(tr))
    ax.plot(x,tr["avg"],color=GREEN,lw=2.5,marker="D",ms=5)
    ax.fill_between(x,tr["avg"],alpha=0.15,color=GREEN)
    ax.set_xticks(x)
    ax.set_xticklabels(tr["season"].tolist(),rotation=45,fontsize=7)
    ax.set_ylabel("Avg 1st-Innings Score")
    ax.set_title("IPL Scoring Inflation  (Real Data)",color=LIGHT)
    ax.grid(axis="y")

    # Chase vs defend + dismissal kinds
    ax=axes[1][1]; ax.set_facecolor("#111827")
    pct=sc_data["chase_pct"]
    dk=sc_data["dismissal_kinds"]
    bars=ax.bar(dk.index,dk.values,
                color=plt.cm.cool(np.linspace(0.3,0.9,len(dk))),
                edgecolor=DARK)
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+5,
                int(b.get_height()),ha="center",color=LIGHT,
                fontsize=8,fontweight="bold")
    ax.set_ylabel("Count")
    ax.set_xticklabels(dk.index,rotation=30,ha="right",fontsize=8)
    ax.set_title(f"Dismissal Types  |  Chase Win Rate: {pct:.1f}%",
                 color=LIGHT); ax.grid(axis="y")

    plt.tight_layout(); save("05_hidden_patterns.png")

# ── Chart 6 — Dashboard ────────────────────────────────────────────────────
def chart_dashboard(t, ph, bat, bowl, sc_data):
    fig=plt.figure(figsize=(22,12))
    fig.patch.set_facecolor(DARK)
    fig.suptitle("IPL CRUNCH '26  ·  EXECUTIVE DASHBOARD\n"
                 "Source: cricsheet.org  ·  1,226 JSON files  ·  Real ball-by-ball data",
                 fontsize=18,color=GOLD,fontweight="bold")

    order=["Powerplay (0-5)","Middle (6-14)","Death (15-19)"]
    agg  =ph["ph_agg"].set_index("phase").reindex(order)
    cv   =[ph["corrs"].get(o,(0,1))[0] for o in order]
    best =["Powerplay","Middle","Death"][cv.index(max(cv,key=abs))]

    kpis=[
        ("Toss → Win",         f"{t['overall']:.1f}%",     GOLD),
        ("Best Phase",          best,                       TEAL),
        ("Chase Win Rate",      f"{sc_data['chase_pct']:.1f}%",GREEN),
        ("Matches Analysed",    f"{t['n']:,}",              RED),
    ]
    for i,(lbl,val,col) in enumerate(kpis):
        ax=fig.add_axes([0.02+i*0.245,0.80,0.22,0.16])
        ax.set_facecolor("#1a2535"); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor(col); sp.set_linewidth(2)
        ax.text(0.5,0.60,val,ha="center",va="center",
                transform=ax.transAxes,fontsize=24,fontweight="bold",color=col)
        ax.text(0.5,0.18,lbl,ha="center",va="center",
                transform=ax.transAxes,fontsize=9.5,color=LIGHT)

    # Phase RPO
    ax1=fig.add_axes([0.02,0.45,0.30,0.30]); ax1.set_facecolor("#111827")
    bars=ax1.bar(["PP","Mid","Death"],agg["avg_rpo"],
                 color=[TEAL,GOLD,RED],edgecolor=DARK,width=0.5)
    for b in bars:
        ax1.text(b.get_x()+b.get_width()/2,b.get_height()+0.03,
                 f"{b.get_height():.2f}",ha="center",
                 color=LIGHT,fontweight="bold",fontsize=10)
    ax1.set_title("Avg RPO by Phase",color=LIGHT,fontsize=11)
    ax1.set_ylabel("RPO",color=LIGHT); ax1.grid(axis="y")

    # Season score trend
    ax2=fig.add_axes([0.37,0.45,0.30,0.30]); ax2.set_facecolor("#111827")
    tr=sc_data["trend"]
    x=range(len(tr))
    ax2.plot(x,tr["avg"],color=GREEN,lw=2,marker="o",ms=4)
    ax2.fill_between(x,tr["avg"],alpha=0.15,color=GREEN)
    ax2.set_xticks(x)
    ax2.set_xticklabels(tr["season"].tolist(),rotation=45,fontsize=6)
    ax2.set_title("1st-Innings Score Trend",color=LIGHT,fontsize=11)
    ax2.set_ylabel("Avg Score",color=LIGHT); ax2.grid(axis="y")

    # Top 5 batters
    ax3=fig.add_axes([0.71,0.45,0.27,0.30]); ax3.set_facecolor("#111827")
    t5b=bat.head(5).sort_values("runs")
    ax3.barh(t5b["batsman"].str.split().str[-1],t5b["runs"],
             color=plt.cm.YlOrRd(np.linspace(0.4,0.9,5)),edgecolor=DARK)
    for i,(_,r) in enumerate(t5b.iterrows()):
        ax3.text(r["runs"]+20,i,f"{int(r['runs']):,}",
                 va="center",color=LIGHT,fontsize=7.5)
    ax3.set_title("Top 5 Run-Scorers (Real)",color=LIGHT,fontsize=11)
    ax3.set_xlabel("Runs",color=LIGHT); ax3.grid(axis="x")

    # Top 5 bowlers
    ax4=fig.add_axes([0.02,0.07,0.27,0.30]); ax4.set_facecolor("#111827")
    t5w=bowl.head(5).sort_values("wickets")
    ax4.barh(t5w["bowler"].str.split().str[-1],t5w["wickets"],
             color=plt.cm.cool(np.linspace(0.4,0.9,5)),edgecolor=DARK)
    for i,(_,r) in enumerate(t5w.iterrows()):
        ax4.text(r["wickets"]+0.3,i,str(int(r["wickets"])),
                 va="center",color=LIGHT,fontsize=7.5)
    ax4.set_title("Top 5 Wicket-Takers (Real)",color=LIGHT,fontsize=11)
    ax4.set_xlabel("Wickets",color=LIGHT); ax4.grid(axis="x")

    # Boundary % per over
    ax5=fig.add_axes([0.37,0.07,0.30,0.30]); ax5.set_facecolor("#111827")
    bo=ph["bnd_over"].reindex(range(20)).fillna(0)
    ax5.bar(bo.index,bo.values,
            color=[TEAL if o<6 else(GOLD if o<15 else RED) for o in bo.index],
            edgecolor=DARK,width=0.85)
    ax5.set_title("Boundary % per Over",color=LIGHT,fontsize=11)
    ax5.set_xlabel("Over",color=LIGHT); ax5.grid(axis="y")

    # Toss donut
    ax6=fig.add_axes([0.71,0.07,0.27,0.30]); ax6.set_facecolor("#111827")
    pct=t["overall"]
    ax6.pie([pct,100-pct],colors=[GOLD,"#2d3748"],startangle=90,
            wedgeprops=dict(width=0.55,edgecolor=DARK))
    ax6.text(0,0.06,f"{pct:.1f}%",ha="center",va="center",
             fontsize=20,fontweight="bold",color=GOLD)
    ax6.text(0,-0.18,f"p={t['p_val']:.3f}",ha="center",va="center",
             fontsize=9,color=GREEN)
    ax6.set_title("Toss → Win Rate",color=LIGHT,fontsize=11)

    save("00_dashboard.png")

# ══════════════════════════════════════════════════════════════════════════
# 4. PRINT KEY STATS
# ══════════════════════════════════════════════════════════════════════════

def print_stats(t, ph, bat, bowl, sc_data):
    sep="═"*65
    print(f"\n{sep}")
    print("  IPL CRUNCH '26 — REAL DATA RESULTS  (cricsheet.org)")
    print(sep)

    print(f"\n📌 Q1 TOSS  ({t['n']:,} matches)")
    print(f"   Win rate  : {t['overall']:.2f}%   p={t['p_val']:.4f} "
          f"{'✓ SIGNIFICANT' if t['p_val']<0.05 else '✗ not significant'}")
    for _,r in t["by_dec"].iterrows():
        print(f"   {r['toss_decision']:<6}: {r['win_pct']:.2f}%  (n={int(r['n'])})")

    print(f"\n📌 Q2 PHASE")
    order=["Powerplay (0-5)","Middle (6-14)","Death (15-19)"]
    agg=ph["ph_agg"].set_index("phase").reindex(order)
    for p in order:
        r,pv=ph["corrs"].get(p,(0,1))
        sig="✓" if pv<0.05 else " "
        print(f"   {p:<22} RPO={agg.loc[p,'avg_rpo']:.2f}  "
              f"Wkts={agg.loc[p,'avg_wkts']:.2f}  "
              f"Corr={r:+.3f} {sig}")

    print(f"\n📌 Q3 TOP BATTERS (real computed)")
    for _,r in bat.head(10).iterrows():
        print(f"   {r['batsman']:<24} {int(r['runs']):>5} runs  "
              f"SR={r['sr']:.1f}  Avg={r['avg']:.1f}  "
              f"4s={int(r['fours'])}  6s={int(r['sixes'])}")

    print(f"\n📌 Q3 TOP BOWLERS (real computed)")
    for _,r in bowl.head(10).iterrows():
        print(f"   {r['bowler']:<24} {int(r['wickets']):>3} wkts  "
              f"Eco={r['economy']:.2f}  SR={r['bowl_sr']:.1f}  "
              f"Avg={r['avg']:.1f}")

    print(f"\n📌 Q4 HIDDEN PATTERNS")
    tr=sc_data["trend"]
    print(f"   Chase win rate : {sc_data['chase_pct']:.2f}%")
    print(f"   Score inflation: {tr['avg'].iloc[0]:.1f} → {tr['avg'].iloc[-1]:.1f} runs")
    for ph_name in order:
        d=ph["dot_phase"].get(ph_name,0)
        print(f"   Dot % {ph_name:<22}: {d:.1f}%")
    print(f"\n{sep}\n")

# ══════════════════════════════════════════════════════════════════════════
# 5. MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    print("\n"+"═"*60)
    print("  IPL CRUNCH '26 — Cricsheet Real Data Pipeline")
    print("="*60+"\n")

    matches, deliveries = parse_all(JSON_DIR)

    print("\n[1/6] Toss analysis …")
    toss = analyse_toss(matches)
    chart_toss(toss)

    print("[2/6] Phase analysis …")
    phase_data = analyse_phases(deliveries, matches)
    chart_phases(phase_data)

    print("[3/6] Batter analysis …")
    bat = analyse_batters(deliveries)
    chart_batters(bat)

    print("[4/6] Bowler analysis …")
    bowl = analyse_bowlers(deliveries)
    chart_bowlers(bowl)

    print("[5/6] Hidden patterns …")
    sc_data = analyse_scores(deliveries, matches)
    chart_hidden(phase_data, sc_data)

    print("[6/6] Executive dashboard …")
    chart_dashboard(toss, phase_data, bat, bowl, sc_data)

    print_stats(toss, phase_data, bat, bowl, sc_data)
    return toss, phase_data, bat, bowl, sc_data

if __name__ == "__main__":
    main()
