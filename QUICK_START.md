# Quick Start Checklist

Follow these steps in order to get the SysML to Slides converter running:

## ✅ Setup Checklist

- [ ] **Step 1**: Virtual environment created and activated
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- [ ] **Step 2**: Dependencies installed
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Step 3**: Google Cloud Project created
  - Visit: https://console.cloud.google.com/
  - Create new project

- [ ] **Step 4**: Google Slides API enabled
  - APIs & Services > Library
  - Search "Google Slides API" > Enable

- [ ] **Step 5**: OAuth Consent Screen configured
  - APIs & Services > OAuth consent screen
  - Fill required fields > Save

- [ ] **Step 6**: OAuth 2.0 Credentials created
  - APIs & Services > Credentials
  - Create Credentials > OAuth client ID
  - Application type: Desktop app
  - Download JSON file

- [ ] **Step 7**: Credentials file placed in project
  - Rename downloaded file to `credentials.json`
  - Place in: `/home/ghazia/sysml-to-slides/credentials.json`

- [ ] **Step 8**: Test the setup
  ```bash
  source venv/bin/activate
  python main.py OpsCon.sysml
  ```

## 🚀 Running the Converter

Once setup is complete:

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run with your SysML file
python main.py OpsCon.sysml

# Or with a different file
python main.py path/to/your/file.sysml
```

## 📚 Need More Help?

- **Detailed Setup Guide**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Full Documentation**: See [README.md](README.md)
- **Troubleshooting**: Check the Troubleshooting section in README.md

## ⚡ Quick Test (Without Google Slides)

To test just the parsing (without Google Slides API):

```bash
source venv/bin/activate
python -c "from sysml_parser import parse_sysml_file; import json; print(json.dumps(parse_sysml_file('OpsCon.sysml'), indent=2))"
```

This will show you the extracted parts and connections without requiring Google credentials.

