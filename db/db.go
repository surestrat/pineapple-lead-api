package db

import (
	"context"
	"fmt"
	"log"
	"sync"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/surestrat/pineapple-lead-api/config"
)

var (
	dbPool     *pgxpool.Pool
	dbPoolOnce sync.Once
	dbInitErr  error
)

// InitDB initializes the database connection pool
func InitDB() error {
	dbPoolOnce.Do(func() {
		dsn := config.GetDSN()
		
		// Create a connection pool
		pool, err := pgxpool.New(context.Background(), dsn)
		if (err != nil) {
			dbInitErr = fmt.Errorf("failed to create connection pool: %w", err)
			return
		}
		
		// Ping the database to verify the connection works
		if err := pool.Ping(context.Background()); err != nil {
			dbInitErr = fmt.Errorf("failed to ping database: %w", err)
			return
		}
		
		dbPool = pool
		log.Println("Database connection pool initialized successfully")
	})
	
	return dbInitErr
}

// GetPool returns the database connection pool
func GetPool() (*pgxpool.Pool, error) {
	if dbPool == nil {
		// For development: return a nil pool but don't raise an error
		// This allows the app to run without a database
		log.Println("Database connection pool not initialized - running in development mode")
		return nil, nil
	}
	return dbPool, nil
}

// Close closes the database connection pool
func Close() {
	if dbPool != nil {
		dbPool.Close()
		log.Println("Database connection pool closed")
	}
}
