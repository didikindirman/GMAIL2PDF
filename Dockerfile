# Gunakan image Python 3.11 versi slim untuk ukuran yang lebih kecil
FROM python:3.11-slim

# Langkah Kritis: Instalasi dependensi sistem dan wkhtmltopdf
# wkhtmltopdf membutuhkan beberapa library rendering (libxrender1, libfontconfig1, dll.)
# untuk dapat bekerja di lingkungan tanpa GUI (headless environment) seperti container.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    libxrender1 \
    libjpeg-turbo8 \
    libfontconfig1 \
    libxtst6 \
    # Bersihkan file cache APT untuk mengurangi ukuran akhir image container
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Atur direktori kerja utama di dalam container
WORKDIR /app

# Salin file requirements.txt dan install semua dependensi Python
# Langkah ini dieksekusi terpisah untuk memanfaatkan caching Docker layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode aplikasi inti Python (app.py)
COPY app.py .

# Tetapkan variabel lingkungan PORT. Ini adalah standar yang digunakan
# oleh Render, Heroku, dan platform PaaS modern lainnya.
ENV PORT 8080

# Perintah yang akan dijalankan saat container dimulai.
# Menggunakan Gunicorn sebagai web server produksi yang stabil untuk melayani aplikasi Flask.
# --bind 0.0.0.0:$PORT memastikan server mendengarkan di semua interface pada port yang ditentukan.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 app:app