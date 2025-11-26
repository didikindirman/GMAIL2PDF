# Gunakan image Python 3.11 versi slim untuk ukuran yang lebih kecil
FROM python:3.11-slim

# Tentukan versi wkhtmltopdf yang akan diunduh secara manual.
# Kami menggunakan versi Bullseye (Debian 11) karena cocok dengan base image Python 3.11 slim.
ENV WKHTMLTOPDF_VERSION 0.12.6-1
# Tambahkan ini untuk memastikan APT tidak menanyakan pertanyaan selama instalasi
ENV DEBIAN_FRONTEND noninteractive

# Langkah Kritis: Instalasi wkhtmltopdf secara manual
# Perintah digabungkan untuk efisiensi Docker layer:
# 1. Update APT dan instal wget, dan dependensi rendering dasar (fontconfig, libxtst6, dll.).
# 2. Download paket wkhtmltopdf (.deb) langsung dari GitHub.
# 3. Instal paket .deb menggunakan dpkg. Jika dependensi hilang (yang biasanya terjadi),
#    'apt-get install -f -y' akan dijalankan untuk menginstal semua dependensi runtime yang hilang.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        fontconfig \
        libxrender1 \
        libxtst6 \
        xfonts-base && \
    wget https://github.com/wkhtmltopdf/packaging/releases/download/${WKHTMLTOPDF_VERSION}/wkhtmltox_${WKHTMLTOPDF_VERSION}.bullseye_amd64.deb -O /tmp/wkhtmltox.deb && \
    dpkg -i /tmp/wkhtmltox.deb || apt-get install -f -y && \
    rm /tmp/wkhtmltox.deb && \
    # Bersihkan file cache APT
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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