# go-batch/Dockerfile
FROM golang:1.16-alpine

WORKDIR /app

# Go依存関係のダウンロード
COPY go.mod go.sum ./
RUN go mod download

# ソースコードをコピー
COPY . .

# アプリケーションのビルド
RUN go build -o /main main.go

CMD ["/main"]
