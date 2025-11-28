# 🚀 Advanced Email Automation System (Gmail, Drive, & Gemini AI)

## Email to PDF Archiving with Smart AI Summaries

This project provides a comprehensive, automated solution for archiving important emails from **Gmail** as **PDF files** in **Google Drive**.  
At the same time, it generates **intelligent summaries using Gemini AI** and logs the entire process to a **Google Spreadsheet** in real time.

---

## 💡 Key Features

- ✅ **Automated Monitoring**  
  Periodically scans the Gmail inbox (triggered by **Google Apps Script**) to find new, unread emails based on a configurable search query.

- 📧 **Email to PDF Conversion**  
  Uses an external web service (e.g., hosted on **Render**) to convert raw email content (`.eml` format) into a clean, archivable **PDF**.

- ☁️ **Drive Archiving**  
  Saves the converted PDF files into a specified **Google Drive** folder.

- 🧠 **Smart AI Summarization**  
  Extracts clean plain text from the email and sends it to the **Gemini API** to generate a concise, unformatted summary.

- 📈 **Centralized Logging**  
  Logs all email details (**Timestamp, Subject, Sender, Message ID**), a **clickable PDF link**, and the **AI summary** into a **Google Spreadsheet**.

---

## ⚙️ Program Workflow

The system runs through the following steps after being triggered by Google Apps Script (GAS):

1. **GAS Trigger**  
   Google Apps Script is automatically triggered to start the email search process.

2. **New Email Search**  
   GAS executes a Gmail query to identify new, unread emails.

3. **Raw Content Extraction**  
   Raw email content is extracted in `.eml` format.

4. **PDF Conversion (Render Service)**  
   The `.eml` content is sent to an external EML-to-PDF conversion API.

5. **Archive Storage**  
   The resulting PDF is uploaded and saved to the designated Google Drive folder.

6. **Text Extraction for AI**  
   Clean plain text is retrieved from the email.

7. **AI Summarization (Gemini API)**  
   The email text is sent to Gemini API to generate a summary.

8. **Spreadsheet Logging**  
   All final data (Subject, PDF Link, AI Summary, timestamps, etc.) is logged in Google Sheets.

9. **Mark as Complete**  
   The original email is marked as **read** in Gmail.

---

## 🛠️ Google Apps Script Setup Guide

The client logic is contained in the file:


---

### Step 1: Create a New GAS Project

1. Go to **Google Drive**
2. Click **New → More → Google Apps Script**
3. A new project editor window will open
4. Rename the default file `Code.gs` to:


---

### Step 2: Copy the Script Content

1. Open the file `Google Apps Script/GMAIL2PDF.txt` from this repository
2. Copy the **entire content**
3. Paste it into `GMAIL2PDF.gs`, replacing any existing code

---

### Step 3: Configure the Script (Mandatory)

Inside `GMAIL2PDF.gs`, locate the **ESSENTIAL CONFIGURATION** section and update the following variables:

| Constant | Description | Example Value (Replace This) |
|--------|------------|-------------------------------|
| `GEMINI_API_KEY` | Your Google AI API key | `AIzaSy...` |
| `SHEETS_LINK` | Full URL to target Google Spreadsheet | `https://docs.google.com/spreadsheets/...` |
| `DRIVE_FOLDER_LINK` | Full URL to target Google Drive folder | `https://drive.google.com/drive/folders/...` |
| `RENDER_SERVER_BASE_URL` | Base URL of EML-to-PDF service | `https://gmail2pdf.onrender.com` |
| `EMAIL_SEARCH_QUERY` | Gmail search query | `in:inbox is:unread newer_than:1d` |

> ⚠️ **Important**  
> Make sure to use **full, shareable URLs**, not just raw IDs.

---

### Step 4: Set the Time-Driven Trigger

1. In the GAS editor, click the **⏰ Triggers (Alarm Clock)** icon on the left sidebar
2. Click **+ Add Trigger**
3. Configure the trigger:
   - **Function to run:** `saveRecentEmlToDrive`
   - **Event source:** Time-driven
   - **Time-based trigger:** Select your preferred interval (e.g., Hour timer)
4. Click **Save**
5. Grant all required permissions for Gmail, Drive, Sheets, and external APIs

---

✅ **Setup Complete!**  
Your email automation system will now continuously archive emails, generate AI summaries, and log everything automatically.
