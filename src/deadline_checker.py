"""
Deadline checker module.
Filters conferences with upcoming deadlines.
"""

from datetime import datetime
from typing import List, Dict, Any
from zoneinfo import ZoneInfo

from parser import Conference, ConferenceParser


class DeadlineChecker:
    """Checks for upcoming conference deadlines."""

    def __init__(self, conferences: List[Conference]):
        self.conferences = conferences

    def get_upcoming_deadlines(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get all conferences with deadlines in the next N days.

        Args:
            days: Number of days to look ahead (default: 30)

        Returns:
            List of dictionaries containing conference and deadline information
        """
        upcoming = []

        for conf in self.conferences:
            conf_deadlines = conf.get_upcoming_deadlines(days)

            if conf_deadlines:
                upcoming.append({
                    'conference': conf,
                    'deadlines': conf_deadlines,
                })

        # Sort by nearest deadline
        upcoming.sort(key=lambda x: min(dl['days_until'] for dl in x['deadlines']))

        return upcoming

    def format_deadline_summary(self, upcoming: List[Dict[str, Any]]) -> str:
        """
        Format upcoming deadlines as a text summary.

        Args:
            upcoming: List of upcoming deadline dictionaries

        Returns:
            Formatted text summary
        """
        if not upcoming:
            return "No upcoming deadlines in the next 180 days."

        summary = []
        summary.append(f"Found {len(upcoming)} conferences with upcoming deadlines:\n")

        for item in upcoming:
            conf = item['conference']
            deadlines = item['deadlines']

            summary.append(f"\n{conf.full_name} ({conf.year})")
            summary.append(f"  Location: {conf.place}")
            summary.append(f"  Conference: {conf.date_str}")
            summary.append(f"  Link: {conf.link}")

            if conf.tags:
                summary.append(f"  Tags: {', '.join(str(t) for t in conf.tags)}")

            summary.append("  Deadlines:")
            for dl in deadlines:
                dt = dl['datetime']
                days = dl['days_until']
                dl_type = dl['type'].replace('_', ' ').title()

                # Format deadline in local timezone
                local_tz = ZoneInfo('UTC')  # Can be configured per user
                dt_local = dt.astimezone(local_tz)

                days_str = f"in {days} day{'s' if days != 1 else ''}" if days > 0 else "TODAY"
                summary.append(f"    - {dl_type}: {dt_local.strftime('%Y-%m-%d %H:%M %Z')} ({days_str})")

            if conf.comment:
                summary.append(f"  Note: {conf.comment}")

        return '\n'.join(summary)


if __name__ == '__main__':
    # Test the deadline checker
    parser = ConferenceParser(
        'data/ai-conferences.yml',
        'data/security-conferences.yml'
    )
    conferences = parser.parse_all()

    checker = DeadlineChecker(conferences)
    upcoming = checker.get_upcoming_deadlines(days=90)

    print(checker.format_deadline_summary(upcoming))
