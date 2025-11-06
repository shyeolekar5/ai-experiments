# Gmail Draft Automation via Zapier

This project demonstrates automating email draft creation using Google Sheets and Gmail with Zapier. Every time a new row is added to a spreadsheet, a draft email is automatically generated in Gmail.

## Features
- Pulls data dynamically from Google Sheets (Name, Email, Notes, etc.)
- Creates professional Gmail drafts ready for review
- Supports HTML templates with embedded links
- Fully configurable via Zapier

## Demo
Add a row to the spreadsheet `example_spreadsheet.csv`:

| Name | Email | Notes |
|------|-------|-------|
| John Doe | john.doe@example.com | Follow-up on report |

After the Zap runs, a draft email is created in Gmail for the row.

## Getting Started

1. Open [Zapier](https://zapier.com) and click **Create a Zap**.
2. **Trigger**: Google Sheets → New Spreadsheet Row → Connect your Google account → Select your spreadsheet.
3. **Action**: Gmail → Create Draft → Connect Gmail → Map fields (`To`, `Subject`, `Body`) to spreadsheet columns.
4. Optionally, use `template_email.html` as your email body.
5. Test the Zap and activate it.

## Files
- `example_spreadsheet.csv` → Sample data for testing
- `template_email.html` → HTML email template
- `zap_config_instructions.md` → Step-by-step setup guide 
- `screenshots/` → screenshots of the Zap setup
