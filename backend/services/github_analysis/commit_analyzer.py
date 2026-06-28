from datetime import datetime, timezone
from typing import Any, Dict, List

from .client import GitHubClient


async def analyze_commits(client: GitHubClient, owner: str, repo: str) -> dict:
    commits = await client.get_commits(owner, repo, per_page=100)
    activity = await client.get_commit_activity(owner, repo)
    contributors = await client.get_contributors(owner, repo)

    if not commits:
        return _empty()

    total_commits = len(commits)

    first_commit_date = None
    latest_commit_date = None
    if commits:
        latest = commits[0]
        earliest = commits[-1]
        try:
            latest_commit_date = latest.get("commit", {}).get("author", {}).get("date", "")
            first_commit_date = earliest.get("commit", {}).get("author", {}).get("date", "")
        except (KeyError, IndexError):
            pass

    development_duration_days = 0
    if first_commit_date and latest_commit_date:
        try:
            first_dt = datetime.fromisoformat(first_commit_date.replace("Z", "+00:00"))
            latest_dt = datetime.fromisoformat(latest_commit_date.replace("Z", "+00:00"))
            development_duration_days = (latest_dt - first_dt).days
        except (ValueError, TypeError):
            pass

    commit_frequency = 0.0
    if development_duration_days > 0:
        commit_frequency = round(total_commits / max(development_duration_days, 1), 2)

    active_contributors = len(contributors) if contributors else 0

    recent_commits_30d = 0
    now = datetime.now(timezone.utc)
    for commit in commits:
        try:
            date_str = commit.get("commit", {}).get("author", {}).get("date", "")
            if date_str:
                commit_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                days_ago = (now - commit_dt).days
                if days_ago <= 30:
                    recent_commits_30d += 1
        except (ValueError, TypeError):
            continue

    weekly_activity = []
    for week_data in (activity or [])[-12:]:
        weekly_activity.append({
            "week": week_data.get("week", 0),
            "total": week_data.get("total", 0),
        })

    health_score = _compute_health_score(
        total_commits, development_duration_days, active_contributors,
        recent_commits_30d, commit_frequency,
    )

    return {
        "total_commits": total_commits,
        "first_commit_date": first_commit_date,
        "latest_commit_date": latest_commit_date,
        "development_duration_days": development_duration_days,
        "commit_frequency_per_day": commit_frequency,
        "active_contributors": active_contributors,
        "recent_commits_30d": recent_commits_30d,
        "health_score": health_score,
        "weekly_activity": weekly_activity,
        "is_active": recent_commits_30d > 0,
    }


def _compute_health_score(
    total_commits: int, duration_days: int, contributors: int,
    recent_commits: int, frequency: float,
) -> float:
    score = 0.0

    if total_commits > 500:
        score += 2.5
    elif total_commits > 100:
        score += 2.0
    elif total_commits > 20:
        score += 1.5
    elif total_commits > 5:
        score += 1.0
    else:
        score += 0.5

    if duration_days > 365:
        score += 2.0
    elif duration_days > 90:
        score += 1.5
    elif duration_days > 30:
        score += 1.0
    else:
        score += 0.5

    if contributors > 10:
        score += 2.0
    elif contributors > 3:
        score += 1.5
    elif contributors > 1:
        score += 1.0
    else:
        score += 0.5

    if recent_commits > 20:
        score += 2.0
    elif recent_commits > 5:
        score += 1.5
    elif recent_commits > 0:
        score += 1.0
    else:
        score += 0.0

    if frequency > 1.0:
        score += 1.5
    elif frequency > 0.3:
        score += 1.0
    elif frequency > 0.05:
        score += 0.5

    return round(min(10.0, score), 1)


def _empty() -> dict:
    return {
        "total_commits": 0,
        "first_commit_date": None,
        "latest_commit_date": None,
        "development_duration_days": 0,
        "commit_frequency_per_day": 0,
        "active_contributors": 0,
        "recent_commits_30d": 0,
        "health_score": 0,
        "weekly_activity": [],
        "is_active": False,
    }
