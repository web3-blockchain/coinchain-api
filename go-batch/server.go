package main

import (
	"context"
	"log"
	"net"

	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	"google.golang.org/grpc"

	pb "go-batch/protos/database.proto"
)

const (
	postgreSQLInfo = "host=localhost port=5432 user=username password=password dbname=yourdb sslmode=disable"
)

type server struct {
	db *sqlx.DB
}

func (s *server) CreateTables(ctx context.Context, in *pb.CreateTablesRequest) (*pb.CreateTablesResponse, error) {
	// ここでテーブル作成のSQLを実行
	_, err := s.db.Exec("CREATE TABLE IF NOT EXISTS example (id SERIAL PRIMARY KEY, name TEXT)")
	if err != nil {
		return &pb.CreateTablesResponse{Success: false, Message: err.Error()}, nil
	}
	return &pb.CreateTablesResponse{Success: true, Message: "Tables created successfully"}, nil
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	db, err := sqlx.Connect("postgres", postgreSQLInfo)
	if err != nil {
		log.Fatalf("failed to connect database: %v", err)
	}
	pb.RegisterDatabaseServiceServer(s, &server{db: db})
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
