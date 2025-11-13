#!/bin/bash

# Local test script for conference deadline notification system
# Usage: ./test_local.sh

echo "Conference Deadline Notification System - Local Test"
echo "===================================================="
echo ""

# Check if environment variables are set
if [ -z "$RESEND_API_KEY" ]; then
    echo "⚠️  Warning: RESEND_API_KEY not set"
    echo "   Set it with: export RESEND_API_KEY='your-key'"
fi

if [ -z "$FROM_EMAIL" ]; then
    echo "⚠️  Warning: FROM_EMAIL not set"
    echo "   Set it with: export FROM_EMAIL='bot@yourdomain.com'"
fi

if [ -z "$TO_EMAIL" ]; then
    echo "⚠️  Warning: TO_EMAIL not set"
    echo "   Set it with: export TO_EMAIL='you@email.com'"
fi

echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""

# Run the script
echo "Running deadline checker..."
python3 src/main.py

echo ""
echo "Done!"
