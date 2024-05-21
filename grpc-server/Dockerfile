# grpc-server/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# サーバーのソースコードをコピー
COPY . .

CMD ["python", "server.py"]
