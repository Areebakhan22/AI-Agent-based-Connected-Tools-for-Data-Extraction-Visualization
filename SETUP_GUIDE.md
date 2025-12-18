# Google Cloud Setup Guide

This guide will walk you through setting up Google Cloud credentials to enable Google Slides generation.

## Step-by-Step Instructions

### Step 1: Create a Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project**
   - Click on the project dropdown at the top (next to "Google Cloud")
   - Click "New Project"
   - Enter a project name (e.g., "SysML-to-Slides")
   - Click "Create"
   - Wait for the project to be created (may take a few seconds)

### Step 2: Enable Google Slides API

1. **Navigate to APIs & Services**
   - In the left sidebar, click "APIs & Services" > "Library"
   - Or go directly to: https://console.cloud.google.com/apis/library

2. **Search for Google Slides API**
   - In the search bar, type "Google Slides API"
   - Click on "Google Slides API" from the results

3. **Enable the API**
   - Click the "Enable" button
   - Wait for the API to be enabled (usually instant)

### Step 3: Create OAuth 2.0 Credentials

1. **Go to Credentials Page**
   - In the left sidebar, click "APIs & Services" > "Credentials"
   - Or go directly to: https://console.cloud.google.com/apis/credentials

2. **Configure OAuth Consent Screen** (First time only)
   - Click "OAuth consent screen" tab (or button if prompted)
   - Select "External" user type (unless you have a Google Workspace)
   - Click "Create"
   - Fill in the required fields:
     - **App name**: "SysML to Slides Converter" (or any name)
     - **User support email**: Your email address
     - **Developer contact information**: Your email address
   - Click "Save and Continue"
   - On "Scopes" page, click "Save and Continue" (no need to add scopes)
   - On "Test users" page, click "Save and Continue" (optional)
   - On "Summary" page, click "Back to Dashboard"

3. **Create OAuth 2.0 Client ID**
   - Go back to "Credentials" tab
   - Click "+ Create Credentials" button
   - Select "OAuth client ID"
   - If prompted about OAuth consent screen, click "Configure Consent Screen" and follow step 2 above
   - **Application type**: Select "Desktop app"
   - **Name**: Enter "SysML Slides Client" (or any name)
   - Click "Create"

4. **Download Credentials**
   - A popup will appear with your Client ID and Client Secret
   - Click "Download JSON" button
   - **Important**: Save the file as `credentials.json` in your project directory:
     ```
     /home/ghazia/sysml-to-slides/credentials.json
     ```
   - Click "OK" to close the popup

### Step 4: Verify Setup

1. **Check File Location**
   - Make sure `credentials.json` is in the project root directory
   - The file should contain JSON with keys like "client_id", "client_secret", etc.

2. **Test the Setup**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Run the script
   python main.py OpsCon.sysml
   ```

3. **First Run Authentication**
   - On first run, a browser window will open
   - Sign in with your Google account
   - Click "Allow" to grant permissions
   - The script will save a `token.json` file for future use
   - You won't need to authenticate again unless the token expires

## Troubleshooting

### "credentials.json not found"
- Make sure the file is named exactly `credentials.json` (case-sensitive)
- Check that it's in the project root directory (same folder as `main.py`)
- Verify the file contains valid JSON

### "Access blocked: This app's request is invalid"
- Make sure you've completed the OAuth consent screen setup
- If using "External" user type, you may need to add your email as a test user
- Wait a few minutes after creating credentials for them to propagate

### "The OAuth client was not found"
- Double-check that you downloaded the correct credentials file
- Make sure you selected "Desktop app" as the application type
- Try creating new credentials if the issue persists

### Browser doesn't open for authentication
- Make sure you're running the script from a terminal (not in background)
- Check that your system has a default browser configured
- You can manually copy the URL from the terminal if needed

## Security Notes

- **Never commit `credentials.json` or `token.json` to version control**
- These files are already in `.gitignore` for your protection
- Keep your credentials secure and don't share them
- If credentials are compromised, revoke them in Google Cloud Console and create new ones

## Next Steps After Setup

Once credentials are set up, you can:
1. Run `python main.py OpsCon.sysml` to generate slides
2. The script will create a new Google Slides presentation
3. You'll get a URL to view the presentation
4. The presentation will contain:
   - Rectangle shapes for each part/actor
   - Arrow connectors showing relationships

## Quick Reference

**Project Directory**: `/home/ghazia/sysml-to-slides/`

**Required Files**:
- `credentials.json` - Google OAuth credentials (you create this)
- `token.json` - Auto-generated after first authentication

**Command to Run**:
```bash
source venv/bin/activate
python main.py OpsCon.sysml
```

