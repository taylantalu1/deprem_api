# Python 3.9 imajını kullan
FROM python:3.9-slim

# Çalışma dizini belirle
WORKDIR /app

# Gereksinimleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Flask uygulamasını başlat
CMD ["python", "app.py"]
