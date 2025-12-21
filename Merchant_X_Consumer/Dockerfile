# 使用官方 Python image
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 避免 Python 產生 .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安裝必要套件
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean

# 將 requirements.txt 複製到容器
COPY requirements.txt /app/

# 安裝依賴
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 複製整個專案到容器內
COPY . /app/

# 對外開放 port 8000
EXPOSE 8000

# 啟動命令（讓 docker-compose 控制）
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
