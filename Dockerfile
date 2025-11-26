# Menggunakan image dasar Python 3.11 Slim (Debian Bullseye)
FROM python:3.11-slim-bullseye

# Mengatur variabel lingkungan
ENV DEBIAN_FRONTEND=noninteractive
ENV PORT=8080

# Langkah 1: Instal dependensi sistem yang diperlukan oleh WeasyPrint (GTK+/Cairo/Pango)
# Dependensi ini lebih mudah diinstal daripada dependensi Qt milik wkhtmltopdf.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Dependensi Core WeasyPrint (Cairo, Pango, GDK-Pixbuf)
        libxml2-dev \
        libxslt1-dev \
        libffi-dev \
        libcairo2 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        # Utilitas Umum
        wget \
        fontconfig \
        xfonts-base \
        # Bersihkan cache APT
        && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Atur direktori kerja
WORKDIR /app

# Salin dan instal dependensi Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode aplikasi
COPY app.py .

# Ekspos port aplikasi
EXPOSE 8080

# Perintah yang akan dijalankan saat container dimulai (Menggunakan Gunicorn untuk aplikasi Flask/Web)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "app:app"]