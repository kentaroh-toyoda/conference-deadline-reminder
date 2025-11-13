# Quick Start Guide

Get your conference deadline notification system running in 5 minutes!

## Prerequisites

- GitHub account
- Resend account (free tier available at https://resend.com)
- Python 3.11+ (for local testing only)

## Setup Steps

### 1. Get Resend API Key

1. Sign up at https://resend.com
2. Verify a domain (or use Resend test domain for testing)
3. Create API key at https://resend.com/api-keys
4. Copy the API key (starts with `re_`)

### 2. Configure GitHub Repository

1. Push this code to your GitHub repository

2. Go to **Settings → Secrets and variables → Actions**

3. Click **New repository secret** and add these secrets:

   | Secret Name | Value | Example |
   |-------------|-------|---------|
   | `RESEND_API_KEY` | Your Resend API key | `re_123abc...` |
   | `FROM_EMAIL` | Verified sender email | `bot@yourdomain.com` |
   | `TO_EMAIL` | Your email address | `you@example.com` |
   | `FROM_NAME` | Bot name (optional) | `Conference Bot` |

### 3. Test the Workflow

1. Go to **Actions** tab in GitHub
2. Select **Weekly Conference Deadline Reminder**
3. Click **Run workflow** → **Run workflow**
4. Wait ~30 seconds
5. Check your email!

### 4. Schedule is Automatic

The workflow runs every Monday at 6 AM UTC automatically. No further action needed!

## Local Testing (Optional)

```bash
# Set environment variables
export RESEND_API_KEY="re_your_key_here"
export FROM_EMAIL="bot@yourdomain.com"
export TO_EMAIL="you@example.com"

# Install dependencies
pip install -r requirements.txt

# Run the script
python src/main.py
```

## Customization

### Change Email Schedule

Edit `.github/workflows/weekly-reminder.yml`:

```yaml
schedule:
  - cron: '0 6 * * 1'  # Monday 6 AM UTC
```

Common schedules:
- Daily: `'0 9 * * *'` (9 AM UTC every day)
- Weekly Friday: `'0 17 * * 5'` (5 PM UTC every Friday)
- Bi-weekly: `'0 6 * * 1/2'` (every other Monday)

### Change Deadline Window

In `.github/workflows/weekly-reminder.yml`, modify:

```yaml
env:
  DAYS_AHEAD: 30  # Change to 60, 90, etc.
```

## Troubleshooting

**No email received?**
- Check GitHub Actions logs for errors
- Verify secrets are set correctly
- Confirm FROM_EMAIL domain is verified in Resend
- Check spam folder

**No deadlines found?**
- Increase DAYS_AHEAD value
- Update conference data files (may be outdated)

**Email looks broken?**
- Check email client (some clients don't support HTML)
- View email in web browser

## Next Steps

1. ✅ Test the workflow manually
2. ✅ Verify email arrives correctly
3. 📅 Wait for Monday 6 AM UTC for automatic run
4. 🔄 Update conference data periodically from source repos

## Support

- Check GitHub Actions workflow logs
- Review README.md for detailed documentation
- Open an issue for bugs or questions

---

**Pro Tip**: Add multiple email addresses to `TO_EMAIL` in GitHub Secrets:
```
email1@example.com,email2@example.com
```
Then modify `email_sender.py` to parse and send to multiple recipients!
