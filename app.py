import os
import email
from email import policy
import pdfkit

# SET PATH wkhtmltopdf
WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

def eml_to_pdf(eml_path, pdf_path):
    with open(eml_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    sender = msg.get('From', '')
    receiver = msg.get('To', '')
    subject = msg.get('Subject', '')
    date = msg.get('Date', '')

    body = "<p>(No content)</p>"

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                body = part.get_content()
                break
            elif part.get_content_type() == "text/plain":
                body = "<pre>" + part.get_content() + "</pre>"
    else:
        body = msg.get_content()

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial; }}
            .header {{
                border-bottom: 1px solid #aaa;
                margin-bottom: 20px;
            }}
            .header p {{ margin: 4px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <p><b>From:</b> {sender}</p>
            <p><b>To:</b> {receiver}</p>
            <p><b>Subject:</b> {subject}</p>
            <p><b>Date:</b> {date}</p>
        </div>
        <div>{body}</div>
    </body>
    </html>
    """

    pdfkit.from_string(html, pdf_path, configuration=config)
    print(f"✅ PDF dibuat: {pdf_path}")


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    eml_to_pdf("coba.eml", "output/contoh.pdf")
