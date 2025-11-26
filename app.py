import os
import sys
import email
import io
from email import policy
from weasyprint import HTML, CSS
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

# --- CRITICAL CSS FOR PDF RENDERING ---
# This CSS attempts to make the output look like a direct print of the email body.
CSS_CONTENT = """
@page {
    size: A4;
    margin: 2cm 1cm; /* Reduced horizontal margin for more content space */
}
body {
    font-family: Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #333;
    padding: 0;
    margin: 0;
}

/* Simplified Metadata Box */
.email-metadata {
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
    margin-bottom: 10px;
    font-size: 8pt;
    text-align: left;
    color: #666;
}

.email-content {
    margin-top: 5px;
    text-align: left;
    line-height: 1.5;
}

/* --- FIXES FOR EMAIL LAYOUT (To prevent overflow and borders) --- */

/* Force all elements to respect page width (Crucial for responsive rendering) */
.email-content * {
    max-width: 100% !important; 
    height: auto !important;
    box-sizing: border-box; 
    overflow: hidden; /* Hide anything that tries to overflow its container */
}

/* Ensure images don't overflow */
.email-content img {
    max-width: 100% !important;
    height: auto !important;
    display: block; 
}

/* Remove unwanted borders from layout tables (Fixes the 'grid' issue) */
.email-content table {
    width: 100% !important; 
    border-collapse: collapse;
    border: none !important; 
}
.email-content table td, 
.email-content table th {
    /* Explicitly remove borders from cells */
    border: none !important; 
    padding: 2px; /* Reduce padding to minimize whitespace */
    text-align: left;
}

/* Fallback for plain text content */
.email-content pre {
    white-space: pre-wrap;
    word-wrap: break-word;
}
"""

# --- EML Processing Function ---

def extract_content_and_metadata(eml_bytes):
    """
    Reads binary EML data, extracts HTML/Text content, and metadata.
    The extracted content is then wrapped in a single HTML frame.
    """
    try:
        # Use io.BytesIO to read binary data and email.policy.default
        msg = email.message_from_bytes(eml_bytes, policy=policy.default)
    except Exception as e:
        print(f"ERROR: Failed to parse EML message: {e}", file=sys.stderr)
        return None

    html_content = None
    text_content = None
    
    # Extract Metadata
    subject = msg['subject'] or 'No Subject'
    from_addr = msg['from'] or 'Unknown Sender'
    to_addr = msg['to'] or 'Unknown Recipient'
    date = msg['date'] or 'Date Unknown'
    
    # Find HTML and Text parts
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdisp = part.get('Content-Disposition')
            
            if ctype == 'text/html' and not cdisp:
                html_content = part.get_content()
                break # Prioritize HTML
            elif ctype == 'text/plain' and not cdisp:
                if text_content is None:
                    text_content = part.get_content()
    else:
        # Simple email
        ctype = msg.get_content_type()
        if ctype == 'text/html':
            html_content = msg.get_content()
        elif ctype == 'text/plain':
            text_content = msg.get_content()

    # --- Content Merging for PDF ---
    # Prioritize HTML, then fallback to Plain Text
    content_body = ""
    if html_content:
        content_body = html_content
    elif text_content:
        # Wrap Plain Text in <pre> tags to preserve line breaks/spaces
        content_body = f"<pre>{text_content}</pre>"
    else:
        return None # No renderable content found

    # Wrap content and metadata in a single HTML frame
    # NOTE: The static "Konversi Email ke PDF" title (<h1>) has been removed.
    final_html = f"""
    <!doctype html>
    <html>
    <head>
        <title>Email: {subject}</title>
    </head>
    <body>
        <div class="email-metadata">
            <strong>From:</strong> {from_addr}<br>
            <strong>To:</strong> {to_addr}<br>
            <strong>Date:</strong> {date}<br>
            <strong>Subject:</strong> {subject}
        </div>
        <div class="email-content">
            {content_body}
        </div>
    </body>
    </html>
    """
    return final_html

# --- Flask Routes ---

@app.route('/', methods=['GET'])
def index():
    """Displays the simple HTML upload form (Front-end is now fully in English)."""
    html_form = """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EML to PDF Converter</title>
        <!-- Load Tailwind CSS from CDN for fast, responsive styling -->
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            /* Set base font and background */
            body { 
                font-family: 'Inter', sans-serif; 
                background-color: #f0f4f8; 
            }
        </style>
    </head>
    <body class="flex items-center justify-center min-h-screen p-4">
        <div class="container w-full max-w-lg bg-white p-8 md:p-10 rounded-2xl shadow-xl border border-blue-100/50">
            <!-- Header -->
            <header class="text-center mb-8">
                <h1 class="text-4xl font-extrabold text-blue-700">
                    EML to <span class="text-green-500">PDF Converter</span>
                </h1>
                <p class="mt-2 text-gray-600 text-lg">
                    Reliable Email Conversion using WeasyPrint
                </p>
            </header>

            <!-- Upload Form -->
            <form method="post" enctype="multipart/form-data" action="/convert" class="space-y-6">
                <!-- File Input -->
                <label for="eml_file" class="block text-left text-sm font-medium text-gray-700">
                    Select EML File (.eml)
                </label>
                <input 
                    type="file" 
                    name="eml_file" 
                    id="eml_file"
                    accept=".eml" 
                    required 
                    class="block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-6 file:rounded-full file:border-0 file:text-base file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer transition duration-150 ease-in-out shadow-inner"
                >

                <!-- Convert Button -->
                <button 
                    type="submit" 
                    class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3.5 px-4 rounded-xl transition duration-200 ease-in-out shadow-lg transform hover:scale-[1.01] focus:outline-none focus:ring-4 focus:ring-green-300 focus:ring-opacity-50"
                >
                    Convert & Download PDF
                </button>
            </form>

            <!-- Footer/Instructions -->
            <footer class="mt-8 pt-6 border-t border-gray-100 text-center text-sm text-gray-500">
                <p>This application runs in Docker using Flask and WeasyPrint for reliable conversion.</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_form)

@app.route('/convert', methods=['POST'])
def convert_file():
    """Handles EML file upload and returns the PDF."""
    if 'eml_file' not in request.files:
        return "No file uploaded.", 400

    eml_file = request.files['eml_file']
    if eml_file.filename == '':
        return "No file selected.", 400
    
    # Validate extension
    if not eml_file.filename.lower().endswith('.eml'):
        return "File must be in .eml format.", 400

    try:
        eml_bytes = eml_file.read()
        
        # 1. Extract HTML Content and Metadata
        final_html = extract_content_and_metadata(eml_bytes)
        
        if not final_html:
            return "The EML file is empty or contains no renderable text part.", 400

        # 2. Convert using WeasyPrint into a buffer (memory)
        pdf_buffer = io.BytesIO()
        
        # HTML() requires a string. base_url is set to None.
        HTML(string=final_html, base_url=None).write_pdf(
            target=pdf_buffer, 
            stylesheets=[CSS(string=CSS_CONTENT)]
        )
        pdf_buffer.seek(0)

        # 3. Return PDF as response
        pdf_filename = eml_file.filename.replace('.eml', '.pdf')
        if pdf_filename == eml_file.filename:
            pdf_filename = f"converted_email_{os.path.basename(eml_file.filename).split('.')[0]}.pdf"
            
        return send_file(
            pdf_buffer,
            download_name=pdf_filename,
            mimetype='application/pdf',
            as_attachment=True
        )

    except Exception as e:
        # Print error to Docker/Gunicorn console
        print(f"ERROR DURING CONVERSION: {e}", file=sys.stderr)
        return f"""
        A server error occurred during conversion. 
        Please ensure your EML file is valid. Error: {e}
        """, 500

if __name__ == '__main__':
    # Used for local testing
    print("WARNING: Running Flask in development mode. Use Gunicorn for production.")
    app.run(debug=True, host='0.0.0.0', port=5000)