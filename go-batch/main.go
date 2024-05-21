package main

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"time"

	pb "go-batch/path/to/your/proto"

	_ "github.com/lib/pq"
	"google.golang.org/grpc"
)

const (
	address = "localhost:50051"
	connStr = "user=username dbname=mydb sslmode=disable" // Replace with actual connection string
)

func saveToDB(newsItems []*pb.NewsItem, db *sql.DB) {
	for _, item := range newsItems {
		_, err := db.Exec("INSERT INTO posts (title, url, status) VALUES ($1, $2, $3)", item.Text, item.Url, 0)
		if err != nil {
			log.Printf("Failed to insert news item: %v", err)
		}
	}
}

func main() {
	conn, err := grpc.Dial(address, grpc.WithInsecure(), grpc.WithBlock())
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()
	client := pb.NewNewsServiceClient(conn)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	ticker := time.NewTicker(1 * time.Minute)
	for ; true; <-ticker.C {
		ctx, cancel := context.WithTimeout(context.Background(), time.Second)
		defer cancel()
		r, err := client.FetchNews(ctx, &pb.NewsRequest{})
		if err != nil {
			log.Fatalf("could not fetch news: %v", err)
		}
		saveToDB(r.NewsItems, db)
		fmt.Printf("Fetched and saved %d news items.\n", len(r.NewsItems))
	}
}
