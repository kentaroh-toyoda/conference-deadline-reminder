"""
Conference data parser module.
Parses YAML files containing AI and security conference deadlines.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml
from zoneinfo import ZoneInfo


class Conference:
    """Represents a conference with its deadlines and metadata."""

    def __init__(self, data: Dict[str, Any], source: str):
        self.source = source  # 'ai' or 'security'

        # Handle different field names between AI and security conferences
        self.name = data.get('title') or data.get('name', 'Unknown')
        self.year = data.get('year')
        self.full_name = data.get('full_name', self.name)
        self.link = data.get('link', '')

        # Location info
        self.city = data.get('city', '')
        self.country = data.get('country', '')
        self.place = data.get('place', f"{self.city}, {self.country}".strip(', '))

        # Conference dates
        self.date_str = data.get('date', '')
        self.start_date = self._parse_date(data.get('start'))
        self.end_date = self._parse_date(data.get('end'))

        # Additional metadata
        self.tags = data.get('tags', [])
        self.hindex = data.get('hindex')
        self.comment = data.get('comment', '')

        # Parse deadlines
        self.deadlines = self._parse_deadlines(data)

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            return None

    def _parse_deadlines(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse deadline information from conference data."""
        deadlines = []

        # Check for multiple deadlines format (AI conferences)
        if 'deadlines' in data and isinstance(data['deadlines'], list):
            for dl in data['deadlines']:
                deadline_info = {
                    'type': dl.get('type', 'submission'),
                    'date_str': dl.get('date', ''),
                    'timezone': dl.get('timezone', data.get('timezone', 'UTC-12')),
                }
                deadline_info['datetime'] = self._parse_deadline_datetime(
                    deadline_info['date_str'],
                    deadline_info['timezone']
                )
                if deadline_info['datetime']:
                    deadlines.append(deadline_info)

        # Check for single deadline format
        elif 'deadline' in data:
            deadline_value = data['deadline']
            timezone = data.get('timezone', 'UTC-12')

            # Handle list of deadlines (security conferences)
            if isinstance(deadline_value, list):
                for i, dl_str in enumerate(deadline_value):
                    deadline_info = {
                        'type': f'deadline_{i+1}' if len(deadline_value) > 1 else 'submission',
                        'date_str': dl_str,
                        'timezone': timezone,
                    }
                    deadline_info['datetime'] = self._parse_deadline_datetime(dl_str, timezone)
                    if deadline_info['datetime']:
                        deadlines.append(deadline_info)

            # Handle single deadline string
            elif isinstance(deadline_value, str):
                deadline_info = {
                    'type': 'submission',
                    'date_str': deadline_value,
                    'timezone': timezone,
                }
                deadline_info['datetime'] = self._parse_deadline_datetime(deadline_value, timezone)
                if deadline_info['datetime']:
                    deadlines.append(deadline_info)

        return deadlines

    def _parse_deadline_datetime(self, date_str: str, timezone_str: str) -> Optional[datetime]:
        """Parse deadline string with timezone to datetime object."""
        if not date_str:
            return None

        try:
            # Handle different date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                # If no format matched, return None
                return None

            # Parse timezone
            tz = self._parse_timezone(timezone_str)
            if tz:
                dt = dt.replace(tzinfo=tz)

            return dt
        except (ValueError, TypeError):
            return None

    def _parse_timezone(self, tz_str: str) -> Optional[ZoneInfo]:
        """Parse timezone string to ZoneInfo object."""
        if not tz_str:
            return ZoneInfo('UTC')

        # Handle common timezone formats
        tz_str = tz_str.strip()

        # AoE (Anywhere on Earth) = UTC-12
        if tz_str.upper() == 'AOE':
            return ZoneInfo('Etc/GMT+12')

        # Handle UTC offset format (UTC-12, UTC+2, etc.)
        if tz_str.upper().startswith('UTC'):
            offset_str = tz_str[3:]
            if offset_str:
                try:
                    offset = int(offset_str)
                    # GMT zones are inverted: GMT+12 = UTC-12
                    return ZoneInfo(f'Etc/GMT{-offset:+d}')
                except ValueError:
                    pass

        # Try as IANA timezone name
        try:
            return ZoneInfo(tz_str)
        except Exception:
            return ZoneInfo('UTC')

    def get_upcoming_deadlines(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get deadlines within the next N days."""
        now = datetime.now(ZoneInfo('UTC'))
        upcoming = []

        for deadline in self.deadlines:
            if deadline['datetime']:
                # Convert to UTC for comparison
                dl_utc = deadline['datetime'].astimezone(ZoneInfo('UTC'))
                days_until = (dl_utc - now).days

                if 0 <= days_until <= days:
                    upcoming.append({
                        **deadline,
                        'days_until': days_until,
                    })

        return upcoming

    def __repr__(self):
        return f"<Conference {self.name} {self.year}>"


class ConferenceParser:
    """Parser for conference YAML files."""

    def __init__(self, ai_file: str, security_file: str):
        self.ai_file = Path(ai_file)
        self.security_file = Path(security_file)

    def parse_all(self) -> List[Conference]:
        """Parse all conference files and return list of Conference objects."""
        conferences = []

        # Parse AI conferences
        if self.ai_file.exists():
            conferences.extend(self._parse_file(self.ai_file, 'ai'))

        # Parse security conferences
        if self.security_file.exists():
            conferences.extend(self._parse_file(self.security_file, 'security'))

        return conferences

    def _parse_file(self, file_path: Path, source: str) -> List[Conference]:
        """Parse a single YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not data:
                return []

            # Handle both list and dict formats
            if isinstance(data, list):
                conferences = [Conference(item, source) for item in data]
            elif isinstance(data, dict):
                conferences = [Conference(data, source)]
            else:
                conferences = []

            return conferences
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []


if __name__ == '__main__':
    # Test the parser
    parser = ConferenceParser(
        'data/ai-conferences.yml',
        'data/security-conferences.yml'
    )
    conferences = parser.parse_all()

    print(f"Loaded {len(conferences)} conferences")
    for conf in conferences[:3]:
        print(f"\n{conf.full_name} ({conf.year})")
        print(f"  Location: {conf.place}")
        print(f"  Deadlines: {len(conf.deadlines)}")
        for dl in conf.deadlines:
            if dl['datetime']:
                print(f"    - {dl['type']}: {dl['datetime']} ({dl['timezone']})")
