# Gunakan image Python 3.11 versi slim untuk ukuran yang lebih kecil
FROM python:3.11-slim

# Tambahkan ini untuk memastikan APT tidak menanyakan pertanyaan selama instalasi
ENV DEBIAN_FRONTEND=noninteractive
ENV PORT=8080

# --- Konfigurasi wkhtmltopdf untuk Instalasi Manual (.deb) ---
# Tentukan TAG rilis wkhtmltopdf di GitHub. Ini adalah bagian PATH dari URL.
ENV WKHTMLTOPDF_TAG=0.12.6.1-2
# Nama file paket wkhtmltopdf yang lengkap.
ENV WKHTMLTOPDF_PACKAGE_NAME=wkhtmltox_0.12.6.1-2.bullseye_amd64.deb

# Langkah 1: Update APT dan instal utilitas dan dependensi rendering
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        dpkg \
        fontconfig \
        libxrender1 \
        libxtst6 \
        xfonts-base \
        libssl3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Langkah 2: Unduh dan Instal paket wkhtmltopdf (.deb)
RUN echo "Mengunduh paket wkhtmltopdf..." && \
    # Menggunakan bendera -O untuk menyimpan file dengan nama target di /tmp/
    wget -O /tmp/wkhtmltox.deb https://github.com/wkhtmltopdf/packaging/releases/download/${WKHTMLTOPDF_TAG}/${WKHTMLTOPDF_PACKAGE_NAME} && \
    echo "Menginstal paket wkhtmltopdf..." && \
    # Instal paket; jika gagal karena dependensi, perbaiki dengan 'apt-get install -f -y'
    dpkg -i /tmp/wkhtmltox.deb || apt-get install -f -y && \
    rm /tmp/wkhtmltox.deb

# Atur direktori kerja utama di dalam container
WORKDIR /app

# Salin file requirements.txt dan install semua dependensi Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode aplikasi inti Python (app.py)
COPY app.py .

# Perintah yang akan dijalankan saat container dimulai (Menggunakan format JSON untuk CMD)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "app:app"]