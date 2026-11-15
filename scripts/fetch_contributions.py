
#!/usr/bin/env python3

import json
import os
import urllib.request
from datetime import date, timedelta
from pathlib import Path

USERNAME = "bevinkatti"
TOKEN = os.environ.get("GITHUB_TOKEN")

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "contributions.json"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def fetch():
    if not TOKEN:
        raise RuntimeError("GITHUB_TOKEN is missing")

    today = date.today()
    start = today - timedelta(days=364)

    payload = {
        "query": QUERY,
        "variables": {"login": USERNAME}
    }

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "GitHub-Profile-Cards"
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read())

    if "errors" in result:
        raise RuntimeError(result["errors"])

    user = result["data"]["user"]
    calendar = user["contributionsCollection"]["contributionCalendar"]

    days = [
        {
            "date": day["date"],
            "count": day["contributionCount"]
        }
        for week in calendar["weeks"]
        for day in week["contributionDays"]
        if start.isoformat() <= day["date"] <= today.isoformat()
    ]

    active_days = sum(day["count"] > 0 for day in days)
    busiest = max(days, key=lambda d: d["count"], default=None)

    streak = 0
    for day in reversed(days):
        if day["count"] > 0:
            streak += 1
        else:
            break

    monthly = {}

    for day in days:
        month = day["date"][:7]
        monthly[month] = monthly.get(month, 0) + day["count"]

    months = [
        {"month": month, "count": count}
        for month, count in sorted(monthly.items())[-12:]
    ]

    output = {
        "months": months,
        "streak": streak,
        "active_days": active_days,
        "busiest_day": busiest["date"] if busiest else "—",
        "total_contributions": calendar["totalContributions"],
        "daily": days
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print("Contribution data updated successfully.")


if __name__ == "__main__":
    fetch()
