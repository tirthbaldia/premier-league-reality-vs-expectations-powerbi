import csv
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path("/Users/tirthbaldia/Desktop/PowerBI")
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

OUT.mkdir(parents=True, exist_ok=True)

# Canonical team name mapping across sources
CANONICAL = {
    # OpenFootball / StatsBomb / SPI variations
    "afc bournemouth": "AFC Bournemouth",
    "arsenal": "Arsenal",
    "arsenal fc": "Arsenal",
    "aston villa": "Aston Villa",
    "chelsea": "Chelsea",
    "chelsea fc": "Chelsea",
    "crystal palace": "Crystal Palace",
    "everton": "Everton",
    "everton fc": "Everton",
    "leicester city": "Leicester City",
    "liverpool": "Liverpool",
    "liverpool fc": "Liverpool",
    "manchester city": "Manchester City",
    "manchester united": "Manchester United",
    "newcastle": "Newcastle United",
    "newcastle united": "Newcastle United",
    "norwich city": "Norwich City",
    "southampton": "Southampton",
    "southampton fc": "Southampton",
    "stoke city": "Stoke City",
    "sunderland": "Sunderland",
    "sunderland afc": "Sunderland",
    "swansea city": "Swansea City",
    "tottenham hotspur": "Tottenham Hotspur",
    "watford": "Watford",
    "watford fc": "Watford",
    "west bromwich albion": "West Bromwich Albion",
    "west ham united": "West Ham United",
    "brighton and hove albion": "Brighton and Hove Albion",
    "hull city": "Hull City",
    "huddersfield town": "Huddersfield Town",
    "middlesbrough": "Middlesbrough",
    "burnley": "Burnley",
}

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def canonical(name: str) -> str:
    key = re.sub(r"\s+", " ", name.strip().lower())
    return CANONICAL.get(key, name.strip())


def season_label(dt: datetime) -> str:
    year = dt.year
    if dt.month >= 7:
        start = year
    else:
        start = year - 1
    end = (start + 1) % 100
    return f"{start}/{end:02d}"


# 1) SPI Premier League (league_id=2411)
spi_in = RAW / "fivethirtyeight" / "spi_matches.csv"
spi_match_out = OUT / "spi_pl_matches.csv"
spi_team_out = OUT / "spi_pl_team_match.csv"

with spi_in.open(newline="", encoding="utf-8") as f:
    with spi_match_out.open("w", newline="", encoding="utf-8") as out_m, \
            spi_team_out.open("w", newline="", encoding="utf-8") as out_t:
        reader = csv.DictReader(f)

        match_fields = [
            "date", "season", "team1", "team2",
            "spi1", "spi2", "prob1", "prob2", "probtie",
            "proj_score1", "proj_score2",
            "score1", "score2",
            "xg1", "xg2", "nsxg1", "nsxg2",
            "adj_score1", "adj_score2",
            "expected_points1", "expected_points2",
            "actual_points1", "actual_points2",
        ]
        team_fields = [
            "date", "season", "team", "opponent", "is_home",
            "spi", "proj_score", "actual_goals", "xg",
            "expected_points", "actual_points",
        ]

        mw = csv.DictWriter(out_m, fieldnames=match_fields)
        tw = csv.DictWriter(out_t, fieldnames=team_fields)
        mw.writeheader()
        tw.writeheader()

        for row in reader:
            if row.get("league_id") != "2411":
                continue

            dt = datetime.strptime(row["date"], "%Y-%m-%d")
            season = season_label(dt)
            team1 = canonical(row["team1"])
            team2 = canonical(row["team2"])

            prob1 = float(row["prob1"]) if row["prob1"] else 0.0
            prob2 = float(row["prob2"]) if row["prob2"] else 0.0
            probtie = float(row["probtie"]) if row["probtie"] else 0.0
            expected_points1 = 3 * prob1 + 1 * probtie
            expected_points2 = 3 * prob2 + 1 * probtie

            def to_int(x):
                return int(x) if x not in (None, "") else None

            score1 = to_int(row.get("score1"))
            score2 = to_int(row.get("score2"))

            def points(s1, s2):
                if s1 is None or s2 is None:
                    return None
                if s1 > s2:
                    return 3
                if s1 < s2:
                    return 0
                return 1

            actual_points1 = points(score1, score2)
            actual_points2 = points(score2, score1)

            mw.writerow({
                "date": row["date"],
                "season": season,
                "team1": team1,
                "team2": team2,
                "spi1": row["spi1"],
                "spi2": row["spi2"],
                "prob1": row["prob1"],
                "prob2": row["prob2"],
                "probtie": row["probtie"],
                "proj_score1": row["proj_score1"],
                "proj_score2": row["proj_score2"],
                "score1": score1 if score1 is not None else "",
                "score2": score2 if score2 is not None else "",
                "xg1": row["xg1"],
                "xg2": row["xg2"],
                "nsxg1": row["nsxg1"],
                "nsxg2": row["nsxg2"],
                "adj_score1": row["adj_score1"],
                "adj_score2": row["adj_score2"],
                "expected_points1": f"{expected_points1:.4f}",
                "expected_points2": f"{expected_points2:.4f}",
                "actual_points1": "" if actual_points1 is None else actual_points1,
                "actual_points2": "" if actual_points2 is None else actual_points2,
            })

            tw.writerow({
                "date": row["date"],
                "season": season,
                "team": team1,
                "opponent": team2,
                "is_home": 1,
                "spi": row["spi1"],
                "proj_score": row["proj_score1"],
                "actual_goals": "" if score1 is None else score1,
                "xg": row["xg1"],
                "expected_points": f"{expected_points1:.4f}",
                "actual_points": "" if actual_points1 is None else actual_points1,
            })
            tw.writerow({
                "date": row["date"],
                "season": season,
                "team": team2,
                "opponent": team1,
                "is_home": 0,
                "spi": row["spi2"],
                "proj_score": row["proj_score2"],
                "actual_goals": "" if score2 is None else score2,
                "xg": row["xg2"],
                "expected_points": f"{expected_points2:.4f}",
                "actual_points": "" if actual_points2 is None else actual_points2,
            })


# 2) StatsBomb Premier League 2015/16 (competition_id=2, season_id=27)
sm_in = RAW / "statsbomb" / "matches_2_27.json"
sm_match_out = OUT / "statsbomb_pl2015_matches.csv"
sm_team_out = OUT / "statsbomb_pl2015_team_match.csv"

with sm_in.open(encoding="utf-8") as f:
    matches = json.load(f)

# Build match map for team/opponent lookup
match_team_map = {}

with sm_match_out.open("w", newline="", encoding="utf-8") as out_m:
    mw = csv.DictWriter(out_m, fieldnames=[
        "match_id", "match_date", "kick_off", "season",
        "home_team", "away_team", "home_score", "away_score",
        "stadium", "referee",
    ])
    mw.writeheader()

    for m in matches:
        match_id = m["match_id"]
        match_date = m["match_date"]
        kick_off = m.get("kick_off", "")
        dt = datetime.strptime(match_date, "%Y-%m-%d")
        season = season_label(dt)
        home_team = canonical(m["home_team"]["home_team_name"])
        away_team = canonical(m["away_team"]["away_team_name"])
        home_score = m["home_score"]
        away_score = m["away_score"]
        stadium = m.get("stadium", {}).get("name", "") if m.get("stadium") else ""
        referee = m.get("referee", {}).get("name", "") if m.get("referee") else ""

        match_team_map[match_id] = {
            "home": home_team,
            "away": away_team,
        }

        mw.writerow({
            "match_id": match_id,
            "match_date": match_date,
            "kick_off": kick_off,
            "season": season,
            "home_team": home_team,
            "away_team": away_team,
            "home_score": home_score,
            "away_score": away_score,
            "stadium": stadium,
            "referee": referee,
        })


# Aggregate StatsBomb events
EVENTS_DIR = RAW / "statsbomb" / "events_2_27"

with sm_team_out.open("w", newline="", encoding="utf-8") as out_t:
    tw = csv.DictWriter(out_t, fieldnames=[
        "match_id", "team", "opponent", "is_home",
        "shots", "goals", "xg", "big_chances",
    ])
    tw.writeheader()

    for event_file in sorted(EVENTS_DIR.glob("*.json")):
        match_id = int(event_file.stem)
        teams = match_team_map.get(match_id)
        if not teams:
            continue

        # Initialize
        agg = {
            teams["home"]: {"shots": 0, "goals": 0, "xg": 0.0, "big_chances": 0},
            teams["away"]: {"shots": 0, "goals": 0, "xg": 0.0, "big_chances": 0},
        }

        with event_file.open(encoding="utf-8") as f:
            events = json.load(f)

        for e in events:
            if e.get("type", {}).get("name") != "Shot":
                continue
            team = canonical(e.get("team", {}).get("name", ""))
            if team not in agg:
                # skip if unexpected
                continue
            agg[team]["shots"] += 1

            shot = e.get("shot", {})
            xg = shot.get("statsbomb_xg", 0.0) or 0.0
            agg[team]["xg"] += float(xg)
            if float(xg) >= 0.30:
                agg[team]["big_chances"] += 1

            outcome = shot.get("outcome", {}).get("name", "")
            if outcome == "Goal":
                agg[team]["goals"] += 1

        # Write home/away rows
        home = teams["home"]
        away = teams["away"]
        tw.writerow({
            "match_id": match_id,
            "team": home,
            "opponent": away,
            "is_home": 1,
            **{k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in agg[home].items()},
        })
        tw.writerow({
            "match_id": match_id,
            "team": away,
            "opponent": home,
            "is_home": 0,
            **{k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in agg[away].items()},
        })


# 3) OpenFootball Premier League 2015/16
of_in = RAW / "openfootball" / "england-master" / "2015-16" / "1-premierleague.txt"
of_out = OUT / "openfootball_pl2015_matches.csv"

matchday = None
current_date = None

with of_out.open("w", newline="", encoding="utf-8") as out_f:
    writer = csv.DictWriter(out_f, fieldnames=[
        "matchday", "date", "home_team", "away_team", "home_score", "away_score"
    ])
    writer.writeheader()

    for line in of_in.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()
        if not line or line.startswith("=") or line.startswith("#"):
            continue
        if line.startswith("Matchday"):
            matchday = line.replace("Matchday", "").strip()
            continue
        if line.startswith("[") and line.endswith("]"):
            # Example: [Sat Aug/8]
            try:
                parts = line.strip("[]").split()
                month_day = parts[1]
                month_abbr, day = month_day.split("/")
                month = MONTHS.get(month_abbr)
                day = int(day)
                # 2015/16 season boundary
                year = 2015 if month >= 8 else 2016
                current_date = datetime(year, month, day).strftime("%Y-%m-%d")
            except Exception:
                current_date = None
            continue

        # Match line: optional time, home team, score, away team
        m = re.match(r"^\s*(?:\d{1,2}\.\d{2}\s+)?(.+?)\s+(\d+)-(\d+)(?:\s+\(.+\))?\s+(.+)$", line)
        if not m:
            continue
        home = canonical(m.group(1))
        away = canonical(m.group(4))
        home_score = int(m.group(2))
        away_score = int(m.group(3))

        writer.writerow({
            "matchday": matchday,
            "date": current_date or "",
            "home_team": home,
            "away_team": away,
            "home_score": home_score,
            "away_score": away_score,
        })

print("Done. Outputs in", OUT)
