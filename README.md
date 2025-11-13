# Conference Deadline Notification Agent

Automated email reminder system for AI and security conference deadlines. Runs weekly via GitHub Actions and sends digest emails with upcoming deadlines.

## Features

- 📅 **Comprehensive Coverage**: Tracks major AI/ML and security conferences
- 📧 **Weekly Email Digests**: Automated reminders every Monday at 6 AM UTC
- 🤖 **GitHub Actions**: Serverless execution, no infrastructure needed
- 🎨 **Beautiful HTML Emails**: Professional, responsive email templates
- ⏰ **Smart Filtering**: Shows deadlines in the next 30 days
- 🌍 **Timezone Support**: Handles multiple timezone formats (AoE, UTC offsets, etc.)

## Data Sources

Conference data is sourced from community-maintained repositories:

- **AI Conferences**: [Hugging Face AI Deadlines](https://github.com/huggingface/ai-deadlines)
- **Security Conferences**: [Security Deadlines](https://github.com/sec-deadlines/sec-deadlines.github.io)

## Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd conference-deadline-notification-agent
```

### 2. Get Resend API Key

1. Sign up at [Resend](https://resend.com)
2. Verify your sending domain (or use Resend's test domain for testing)
3. Create an API key from the [API Keys page](https://resend.com/api-keys)

### 3. Configure GitHub Secrets

Go to your repository's **Settings → Secrets and variables → Actions** and add:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `RESEND_API_KEY` | Your Resend API key | `re_xxx...` |
| `FROM_EMAIL` | Sender email (verified domain) | `bot@yourdomain.com` |
| `TO_EMAIL` | Recipient email address | `you@email.com` |
| `FROM_NAME` | Sender display name (optional) | `Conference Bot` |

### 4. Test Locally (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export RESEND_API_KEY="your-api-key"
export FROM_EMAIL="bot@yourdomain.com"
export TO_EMAIL="you@email.com"
export FROM_NAME="Conference Bot"

# Run the script
python src/main.py
```

### 5. Enable GitHub Actions

The workflow runs automatically every Monday at 6 AM UTC. You can also trigger it manually:

1. Go to **Actions** tab in your GitHub repository
2. Select **Weekly Conference Deadline Reminder**
3. Click **Run workflow**

## Project Structure

```
conference-deadline-notification-agent/
├── .github/workflows/
│   └── weekly-reminder.yml        # GitHub Actions workflow (Monday 6 AM)
├── data/
│   ├── ai-conferences.yml         # AI conference data
│   └── security-conferences.yml   # Security conference data
├── src/
│   ├── parser.py                  # YAML parser with timezone support
│   ├── deadline_checker.py        # Filters upcoming deadlines
│   ├── email_sender.py            # Resend API integration
│   └── main.py                    # Entry point
├── templates/
│   └── email_template.html        # HTML email template
├── config.yaml                    # Configuration reference
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Customization

### Change Schedule

Edit `.github/workflows/weekly-reminder.yml`:

```yaml
schedule:
  # Every Monday at 6 AM UTC
  - cron: '0 6 * * 1'

  # Examples:
  # Every day at 9 AM UTC: '0 9 * * *'
  # Every Friday at 5 PM UTC: '0 17 * * 5'
```

### Change Deadline Window

Modify the `DAYS_AHEAD` environment variable in the workflow file:

```yaml
env:
  DAYS_AHEAD: 30  # Change to 60, 90, etc.
```

### Update Conference Data

Conference data files should be updated periodically. You can:

1. **Manual Update**: Download latest YAML files from source repositories
2. **Automated Update**: Add a scheduled job to pull from upstream repos
3. **Add Custom Conferences**: Edit `data/ai-conferences.yml` or `data/security-conferences.yml`

#### Adding a Conference

Add to `data/ai-conferences.yml` or `data/security-conferences.yml`:

```yaml
- title: MyConf
  year: 2025
  id: myconf25
  full_name: My Conference on AI
  link: https://myconf.org
  deadline: '2025-06-01 23:59:59'
  timezone: UTC-12
  city: Tokyo
  country: Japan
  date: September 15-18, 2025
  start: '2025-09-15'
  end: '2025-09-18'
  tags:
    - machine-learning
```

### Customize Email Template

Edit `templates/email_template.html` to change the look and feel of reminder emails.

## Maintenance

### Updating Conference Data

To keep conference data fresh:

```bash
# Option 1: Manual download from source repos
# Visit: https://github.com/huggingface/ai-deadlines
# Visit: https://github.com/sec-deadlines/sec-deadlines.github.io

# Option 2: Use git submodules (advanced)
git submodule add https://github.com/huggingface/ai-deadlines data/external/ai-deadlines
git submodule add https://github.com/sec-deadlines/sec-deadlines.github.io data/external/sec-deadlines
```

### Monitoring

Check GitHub Actions runs:
- Go to **Actions** tab
- View workflow execution logs
- Check for errors in email sending

## Troubleshooting

### Email Not Sending

1. **Check API Key**: Verify `RESEND_API_KEY` is correct
2. **Verify Domain**: Ensure `FROM_EMAIL` domain is verified in Resend
3. **Check Logs**: View GitHub Actions workflow logs for errors
4. **Rate Limits**: Resend free tier has sending limits

### No Deadlines Found

- Conference deadlines may have passed
- Try increasing `DAYS_AHEAD` value
- Check if conference data is up to date

### Timezone Issues

- All deadlines are converted to UTC for comparison
- Display format can be customized in `deadline_checker.py`
- Supported formats: AoE, UTC offsets (UTC-12), IANA timezones

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

- Conference data from [Hugging Face](https://github.com/huggingface/ai-deadlines) and [sec-deadlines](https://github.com/sec-deadlines/sec-deadlines.github.io)
- Email sending powered by [Resend](https://resend.com)

## Support

For issues or questions:
- Open a GitHub issue
- Check existing issues for solutions
- Review GitHub Actions logs for debugging

---

**Note**: Remember to keep your conference data files updated regularly for accurate deadline information!
