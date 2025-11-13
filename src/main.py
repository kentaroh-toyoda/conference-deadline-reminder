#!/usr/bin/env python3
"""
Main script for conference deadline notification system.
Checks for upcoming deadlines and sends email reminders.
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from parser import ConferenceParser
from deadline_checker import DeadlineChecker
from email_sender import EmailSender


def load_config():
    """Load configuration from environment variables."""
    config = {
        'resend_api_key': os.getenv('RESEND_API_KEY'),
        'from_email': os.getenv('FROM_EMAIL'),
        'to_email': os.getenv('TO_EMAIL'),
        'from_name': os.getenv('FROM_NAME', 'Conference Deadline Bot'),
        'days_ahead': int(os.getenv('DAYS_AHEAD', '30')),
    }

    # Validate required config
    required = ['resend_api_key', 'from_email', 'to_email']
    missing = [key for key in required if not config[key]]

    if missing:
        print("Error: Missing required environment variables:")
        for key in missing:
            env_var = key.upper()
            print(f"  {env_var}")
        print("\nPlease set these environment variables and try again.")
        sys.exit(1)

    return config


def main():
    """Main entry point."""
    print("Conference Deadline Notification System")
    print("=" * 50)

    # Load configuration
    config = load_config()
    print(f"✓ Configuration loaded")
    print(f"  Checking deadlines for next {config['days_ahead']} days")
    print(f"  Sending to: {config['to_email']}")

    # Determine paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    ai_file = project_root / 'data' / 'ai-conferences.yml'
    security_file = project_root / 'data' / 'security-conferences.yml'
    template_path = project_root / 'templates' / 'email_template.html'

    # Check if data files exist
    if not ai_file.exists():
        print(f"Warning: AI conference file not found: {ai_file}")
    if not security_file.exists():
        print(f"Warning: Security conference file not found: {security_file}")

    if not ai_file.exists() and not security_file.exists():
        print("Error: No conference data files found!")
        sys.exit(1)

    # Parse conference data
    print(f"\n📚 Parsing conference data...")
    parser = ConferenceParser(str(ai_file), str(security_file))
    conferences = parser.parse_all()
    print(f"✓ Loaded {len(conferences)} conferences")

    # Check for upcoming deadlines
    print(f"\n🔍 Checking for upcoming deadlines...")
    checker = DeadlineChecker(conferences)
    upcoming = checker.get_upcoming_deadlines(days=config['days_ahead'])

    if not upcoming:
        print(f"✓ No deadlines found in the next {config['days_ahead']} days")
        print("No email will be sent.")
        return

    print(f"✓ Found {len(upcoming)} conferences with upcoming deadlines")

    # Print summary
    print(f"\n📋 Summary:")
    for item in upcoming[:5]:  # Show first 5
        conf = item['conference']
        min_days = min(dl['days_until'] for dl in item['deadlines'])
        print(f"  • {conf.name} {conf.year} - nearest deadline in {min_days} day(s)")

    if len(upcoming) > 5:
        print(f"  ... and {len(upcoming) - 5} more")

    # Send email
    print(f"\n📧 Sending email notification...")
    sender = EmailSender(
        config['resend_api_key'],
        config['from_email'],
        config['from_name']
    )

    result = sender.send_deadline_reminder(
        config['to_email'],
        upcoming,
        str(template_path)
    )

    if result.get('status') == 'error':
        print(f"✗ Failed to send email: {result.get('error')}")
        sys.exit(1)
    else:
        print(f"✓ Email sent successfully!")
        if result.get('id'):
            print(f"  Message ID: {result['id']}")

    print("\n" + "=" * 50)
    print("✓ Done!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
