import os
import email
from email import policy
import pdfkit
from flask import Flask, request, send_file, jsonify
from io import BytesIO
import time
import re

app = Flask(__name__)

# --- Configuration for wkhtmltopdf ---
# PENTING: Tentukan path biner secara eksplisit, karena wkhtmltopdf sering
# diinstal di /usr/local/bin/ setelah instalasi paket manual (.deb)
WKHTMLTOPDF_PATH = '/usr/local/bin/wkhtmltopdf' 

try:
    # pdfkit configuration menggunakan path biner yang sudah ditentukan
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    # Verifikasi bahwa biner ditemukan saat server dimulai
    if not os.path.exists(WKHTMLTOPDF_PATH):
        print(f"ERROR: wkhtmltopdf biner tidak ditemukan di {WKHTMLTOPDF_PATH}. Server mungkin akan gagal.")
        config = None
    else:
        print(f"INFO: wkhtmltopdf berhasil dikonfigurasi menggunakan path: {WKHTMLTOPDF_PATH}")
except OSError as e:
    # Log an error jika konfigurasi gagal karena alasan lain
    print(f"ERROR: Gagal mengonfigurasi pdfkit. {e}")
    config = None

# --- EML PARSING FUNCTION ---
def eml_to_html(eml_content):
    """
    Parses the raw EML content (bytes) and extracts email details and body into an HTML string 
    for proper PDF rendering. It prefers HTML body content over plain text.
    """
    f = BytesIO(eml_content)
    # Use email.policy.default for robust header and structure decoding
    msg = email.message_from_binary_file(f, policy=policy.default)

    # Extract email metadata
    sender = msg.get('From', 'N/A')
    receiver = msg.get('To', 'N/A')
    subject = msg.get('Subject', 'No Subject')
    date = msg.get('Date', 'N/A')

    body = "<p>No readable content found.</p>"
    
    # Logic to find the best body part: HTML preferred, then Plain Text
    if msg.is_multipart():
        # First attempt: find the HTML part
        for part in msg.walk():
            # Check for HTML content that is not an attached file
            if part.get_content_type() == "text/html" and part.get_filename() is None:
                try:
                    body = part.get_content()
                    break
                except:
                    pass # Continue searching or fall back

        # If no HTML found, search for Plain Text part
        if body == "<p>No readable content found.</p>":
             for part in msg.walk():
                if part.get_content_type() == "text/plain" and part.get_filename() is None:
                    try:
                        # Wrap plain text in <pre> tags to preserve line breaks
                        body = "<pre>" + part.get_content() + "</pre>"
                        break
                    except:
                        pass
    else:
        # Simple, non-multipart message
        try:
            content_type = msg.get_content_type()
            if content_type == "text/html":
                body = msg.get_content()
            elif content_type == "text/plain":
                body = "<pre>" + msg.get_content() + "</pre>"
        except Exception:
            body = "<p>Error extracting body content.</p>"

    # --- Construct the final HTML structure for wkhtmltopdf ---
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ margin: 1in; }} 
            body {{ font-family: Arial, sans-serif; line-height: 1.5; }}
            .header {{
                border-bottom: 1px solid #ddd;
                padding-bottom: 10px;
                margin-bottom: 20px;
                font-size: 10pt;
            }}
            .header p {{ margin: 4px 0; }}
            .content {{ font-size: 11pt; }}
            pre {{ 
                white-space: pre-wrap; 
                word-wrap: break-word; 
                background-color: #f4f4f4;
                padding: 10px;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <p><b>From:</b> {sender}</p>
            <p><b>To:</b> {receiver}</p>
            <p><b>Subject:</b> {subject}</p>
            <p><b>Date:</b> {date}</p>
        </div>
        <div class="content">{body}</div>
    </body>
    </html>
    """
    return html, subject
    

@app.route('/convert', methods=['POST'])
def convert_eml():
    """API endpoint to receive EML content and return a PDF file."""
    
    if not request.data:
        return jsonify({"error": "No EML content provided in the request body."}), 400
    
    # Cek konfigurasi wkhtmltopdf
    if config is None:
        return jsonify({"error": f"Server error: PDF generation is not properly set up. wkhtmltopdf not found at {WKHTMLTOPDF_PATH}."}), 500
        
    try:
        eml_bytes = request.data
        
        # 1. Convert EML content to structured HTML
        html_content, subject = eml_to_html(eml_bytes)
        
        # 2. Generate PDF bytes using pdfkit
        # The second argument (False) tells pdfkit to return the PDF data as a binary string (bytes)
        pdf_bytes = pdfkit.from_string(html_content, False, configuration=config)
        
        # 3. Create a clean and unique filename
        # Clean special characters from the subject and add a timestamp
        clean_subject = re.sub(r'[^\w\s-]', '', subject).strip()
        filename_core = clean_subject.replace(' ', '_')[:50]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_core}_{timestamp}.pdf"

        # 4. Return PDF file as a response
        # send_file requires a file-like object (BytesIO)
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        # Log the detailed error on the server side
        print(f"Conversion Error: {e}")
        # Return a standard JSON error response to the client
        return jsonify({"error": f"Internal server error during conversion: {e}"}), 500

# Health check endpoint (optional but good for PaaS monitoring)
@app.route('/', methods=['GET'])
def home():
    # Gunakan WKHTMLTOPDF_PATH untuk diagnostik
    status = "OK" if config else "ERROR (wkhtmltopdf not found)"
    return f"EML to PDF Converter API is running. Status: {status}. Path: {WKHTMLTOPDF_PATH}", 200

if __name__ == '__main__':
    # Get port from environment variable (standard for Render, Heroku, etc.)
    port = int(os.environ.get('PORT', 8080))
    print(f"Flask API running on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)