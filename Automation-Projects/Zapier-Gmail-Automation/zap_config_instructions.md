# Zap Setup Instructions

## Step 1: Create a Zap
- Log in to Zapier.com → Click **Create a Zap**

## Step 2: Trigger
- App: Google Sheets
- Event: New Spreadsheet Row
- Connect your Google account
- Select the spreadsheet (`example_spreadsheet.csv`)
- Click **Refresh & Find New Records** to verify

## Step 3: Action
- App: Gmail
- Event: Create Draft
- Connect your Gmail account
- Map fields:
  - **To:** Spreadsheet `Email` column
  - **Subject:** Your chosen subject line
  - **Body:** Use `template_email.html` or dynamic fields (Name, Notes)
- Enable HTML formatting if using HTML template

## Step 4: Test & Activate
- Add a row to the spreadsheet and click **Run**
- Verify a draft appears in Gmail
- Save and name your Zap