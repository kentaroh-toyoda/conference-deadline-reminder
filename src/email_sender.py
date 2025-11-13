"""
Email sender module using Resend API.
Sends formatted conference deadline reminders.
"""

import os
from typing import List, Dict, Any
from pathlib import Path
from jinja2 import Template
import resend


class EmailSender:
    """Sends conference deadline reminder emails using Resend."""

    def __init__(self, api_key: str, from_email: str, from_name: str = "Conference Deadline Bot"):
        """
        Initialize email sender.

        Args:
            api_key: Resend API key
            from_email: Sender email address (must be verified domain in Resend)
            from_name: Sender name to display
        """
        self.api_key = api_key
        self.from_email = from_email
        self.from_name = from_name
        resend.api_key = api_key

    def send_deadline_reminder(
        self,
        to_email: str,
        upcoming_deadlines: List[Dict[str, Any]],
        template_path: str = 'templates/email_template.html'
    ) -> Dict[str, Any]:
        """
        Send email with upcoming conference deadlines.

        Args:
            to_email: Recipient email address
            upcoming_deadlines: List of upcoming deadline dictionaries
            template_path: Path to HTML email template

        Returns:
            Response from Resend API
        """
        if not upcoming_deadlines:
            print("No upcoming deadlines to send.")
            return {'status': 'skipped', 'reason': 'no_deadlines'}

        # Load and render HTML template
        html_content = self._render_template(template_path, upcoming_deadlines)

        # Generate plain text version
        text_content = self._generate_text_content(upcoming_deadlines)

        # Prepare email
        subject = f"📅 Conference Deadlines - {len(upcoming_deadlines)} upcoming"

        try:
            # Send email using Resend
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content,
            }

            response = resend.Emails.send(params)
            print(f"Email sent successfully to {to_email}")
            print(f"Response: {response}")
            return response

        except Exception as e:
            print(f"Error sending email: {e}")
            return {'status': 'error', 'error': str(e)}

    def _render_template(self, template_path: str, upcoming_deadlines: List[Dict[str, Any]]) -> str:
        """Render HTML email template with conference data."""
        template_file = Path(template_path)

        if not template_file.exists():
            # Fallback to simple HTML if template not found
            return self._generate_simple_html(upcoming_deadlines)

        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()

        template = Template(template_content)

        # Format deadlines for template
        formatted_conferences = []
        for item in upcoming_deadlines:
            conf = item['conference']
            deadlines = []

            for dl in item['deadlines']:
                dl_formatted = {
                    'type': dl['type'],
                    'datetime_formatted': dl['datetime'].strftime('%Y-%m-%d %H:%M %Z'),
                    'days_until': dl['days_until'],
                }
                deadlines.append(dl_formatted)

            formatted_conferences.append({
                'conference': conf,
                'deadlines': deadlines,
            })

        # Render template
        html = template.render(
            conferences=formatted_conferences,
            summary_count=len(upcoming_deadlines),
        )

        return html

    def _generate_simple_html(self, upcoming_deadlines: List[Dict[str, Any]]) -> str:
        """Generate simple HTML email if template is not available."""
        html_parts = [
            '<html><body>',
            '<h1>Conference Deadline Reminder</h1>',
            f'<p>You have {len(upcoming_deadlines)} conferences with upcoming deadlines:</p>',
        ]

        for item in upcoming_deadlines:
            conf = item['conference']
            html_parts.append(f'<h2>{conf.full_name} ({conf.year})</h2>')
            html_parts.append(f'<p><strong>Location:</strong> {conf.place}</p>')
            html_parts.append(f'<p><strong>Conference:</strong> {conf.date_str}</p>')
            html_parts.append(f'<p><strong>Link:</strong> <a href="{conf.link}">{conf.link}</a></p>')

            html_parts.append('<ul>')
            for dl in item['deadlines']:
                dt_str = dl['datetime'].strftime('%Y-%m-%d %H:%M %Z')
                days = dl['days_until']
                days_str = f"in {days} day{'s' if days != 1 else ''}" if days > 0 else "TODAY"
                html_parts.append(f'<li><strong>{dl["type"]}:</strong> {dt_str} ({days_str})</li>')
            html_parts.append('</ul>')

        html_parts.append('</body></html>')
        return '\n'.join(html_parts)

    def _generate_text_content(self, upcoming_deadlines: List[Dict[str, Any]]) -> str:
        """Generate plain text email content."""
        text_parts = [
            'CONFERENCE DEADLINE REMINDER',
            '=' * 50,
            f'\nYou have {len(upcoming_deadlines)} conferences with upcoming deadlines:\n',
        ]

        for item in upcoming_deadlines:
            conf = item['conference']
            text_parts.append(f'\n{conf.full_name} ({conf.year})')
            text_parts.append(f'Location: {conf.place}')
            text_parts.append(f'Conference: {conf.date_str}')
            text_parts.append(f'Link: {conf.link}')

            if conf.tags:
                text_parts.append(f'Tags: {", ".join(str(t) for t in conf.tags)}')

            text_parts.append('\nUpcoming Deadlines:')
            for dl in item['deadlines']:
                dt_str = dl['datetime'].strftime('%Y-%m-%d %H:%M %Z')
                days = dl['days_until']
                days_str = f"in {days} day{'s' if days != 1 else ''}" if days > 0 else "TODAY"
                dl_type = dl['type'].replace('_', ' ').title()
                text_parts.append(f'  - {dl_type}: {dt_str} ({days_str})')

            if conf.comment:
                text_parts.append(f'Note: {conf.comment}')

            text_parts.append('')

        text_parts.append('\n' + '=' * 50)
        text_parts.append('This is an automated reminder sent every Monday.')
        text_parts.append('Data sources: Hugging Face AI Deadlines, Security Deadlines')

        return '\n'.join(text_parts)


if __name__ == '__main__':
    # Test email sender (requires environment variables)
    from parser import ConferenceParser
    from deadline_checker import DeadlineChecker

    # Check for required environment variables
    api_key = os.getenv('RESEND_API_KEY')
    from_email = os.getenv('FROM_EMAIL')
    to_email = os.getenv('TO_EMAIL')

    if not all([api_key, from_email, to_email]):
        print("Missing required environment variables:")
        print("  RESEND_API_KEY - Your Resend API key")
        print("  FROM_EMAIL - Sender email (verified domain)")
        print("  TO_EMAIL - Recipient email")
        exit(1)

    # Parse conferences and check deadlines
    parser = ConferenceParser(
        'data/ai-conferences.yml',
        'data/security-conferences.yml'
    )
    conferences = parser.parse_all()

    checker = DeadlineChecker(conferences)
    upcoming = checker.get_upcoming_deadlines(days=90)

    # Send email
    sender = EmailSender(api_key, from_email)
    result = sender.send_deadline_reminder(to_email, upcoming)

    print(f"\nResult: {result}")
