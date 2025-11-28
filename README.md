Automated Email Processing System: PDF Archiving and AI Summarization (Gmail & Google Apps Script)

This project is an automated solution for archiving important emails from Gmail as PDF files in Google Drive, simultaneously generating smart summaries using the Gemini API, and logging the results into a Google Spreadsheet in real-time.

The system is split into two complementary parts:

Client/Trigger (GAS): The Google Apps Script hosted on Google's platform, which monitors Gmail and orchestrates the entire workflow.

Web Service (Render Deployment): An external EML-to-PDF API (e.g., hosted on Render) that performs the complex email conversion task.

🎯 Key Features

Automated Monitoring: Scans the Gmail inbox periodically (set by the GAS time-based trigger) to find new, unread emails based on a configurable search query.

Email to PDF Conversion: Uses an external API hosted on Render (e.g., gmail2pdf.onrender.com) to convert raw email content (.eml format) into clean, archivable PDF files.

Drive Archiving: Saves the converted PDF files to a specific Google Drive folder.

Smart AI Summarization: Extracts the clean, plain text from the email and sends it to the Google Gemini API to generate a concise, unformatted summary.

Centralized Logging: Logs email details (Timestamp, Subject, Sender, Message ID), the PDF link to Drive, and the AI summary result to a Google Spreadsheet.

⚙️ Program Workflow

The program runs through a structured sequence of steps after being triggered by Google Apps Script (GAS):

GAS Trigger: The Google Apps Script (GAS) is triggered automatically (e.g., every 2 hours) to start the email search process.

New Email Search: GAS executes a search query in Gmail (e.g.: in:inbox is:unread newer_than:1d) to identify newly arrived and unread emails.

Raw Content Extraction (.eml): GAS extracts the raw email content for conversion.

PDF Conversion (Render Service): The raw .eml content is sent via an HTTP POST request to the external EML-to-PDF converter API on the Render platform.

Archive Storage: The resulting PDF blob is uploaded and saved to the specified Google Drive folder.

Text Extraction for AI: The clean plain text is retrieved for processing.

AI Summarization (Gemini API): The email text is sent to the Gemini API (gemini-2.5-flash) to generate a concise text summary.

Spreadsheet Logging: The final data (Timestamp, Sender, Subject, PDF Link, AI Summary) is logged to the Google Spreadsheet.

Marking as Complete: The original email is marked as read in Gmail.

🛠️ Setup Instructions (Google Apps Script Side)

The client logic is stored in the Google Apps Script/GMAIL2PDF.txt file in this repository.

Step 1: Create the GAS Project

Go to Google Drive and click New -> More -> Google Apps Script. A new project editor window will open.

A default file named Code.gs will exist. Click the filename (usually Code.gs) in the file explorer panel on the left.

Rename this file to GMAIL2PDF.gs.

Step 2: Copy the Script Content

Open the Google Apps Script/GMAIL2PDF.txt file from this repository.

Select and copy the entire content (Ctrl+A / Cmd+A, then Ctrl+C / Cmd+C).

Paste the content into the GMAIL2PDF.gs file in your Google Apps Script editor, replacing any existing code.

Step 3: Configure the Script

In the GMAIL2PDF.gs file, locate the ESSENTIAL CONFIGURATION section near the top and replace the placeholder values with your own:

Constant

Description

Your Value Example

GEMINI_API_KEY

Your Google AI API key.

AIzaSy...

SHEETS_LINK

Full URL of your target Google Spreadsheet.

https://docs.google.com/spreadsheets/...

DRIVE_FOLDER_LINK

Full URL of your target Google Drive folder.

https://drive.google.com/drive/folders/...

RENDER_SERVER_BASE_URL

The base URL of your deployed EML-to-PDF service (e.g., on Render).

https://gmail2pdf.onrender.com

EMAIL_SEARCH_QUERY

Gmail search query to filter target emails.

'in:inbox is:unread newer_than:1d'

Step 4: Set the Time-Driven Trigger

In the GAS editor, click the Alarm Clock icon (Triggers) on the left sidebar.

Click + Add Trigger.

Configure the trigger settings:

Choose which function to run: saveRecentEmlToDrive

Choose deployment to run: Head

Select event source: Time-driven

Select type of time based trigger: Choose your desired interval (e.g., Hour timer).

Click Save. You will be prompted to grant permissions to the script to access Gmail, Drive, and external APIs. Accept these permissions.