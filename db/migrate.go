package db

import (
	"fmt"
	"log"

	"github.com/golang-migrate/migrate/v4"
	_ "github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file"
	"github.com/surestrat/pineapple-lead-api/config"
)

// MigrateUp runs all database migrations
func MigrateUp() error {
	m, err := getMigrate()
	if err != nil {
		return err
	}
	
	defer func() {
		srcErr, dbErr := m.Close()
		if srcErr != nil {
			log.Printf("Error closing migration source: %v", srcErr)
		}
		if dbErr != nil {
			log.Printf("Error closing migration database: %v", dbErr)
		}
	}()
	
	if err := m.Up(); err != nil && err != migrate.ErrNoChange {
		return fmt.Errorf("failed to run migrations: %w", err)
	}
	
	log.Println("Database migrations applied successfully")
	return nil
}

// MigrateDown rolls back all database migrations
func MigrateDown() error {
	m, err := getMigrate()
	if err != nil {
		return err
	}
	
	defer func() {
		srcErr, dbErr := m.Close()
		if srcErr != nil {
			log.Printf("Error closing migration source: %v", srcErr)
		}
		if dbErr != nil {
			log.Printf("Error closing migration database: %v", dbErr)
		}
	}()
	
	if err := m.Down(); err != nil && err != migrate.ErrNoChange {
		return fmt.Errorf("failed to roll back migrations: %w", err)
	}
	
	log.Println("Database migrations rolled back successfully")
	return nil
}

func getMigrate() (*migrate.Migrate, error) {
	dsn := fmt.Sprintf("postgres://%s:%s@%s:%d/%s?sslmode=%s",
		config.GetConfig().DBUser,
		config.GetConfig().DBPassword,
		config.GetConfig().DBHost,
		config.GetConfig().DBPort,
		config.GetConfig().DBName,
		config.GetConfig().DBSSLMode,
	)
	
	m, err := migrate.New("file://db/migrations", dsn)
	if err != nil {
		return nil, fmt.Errorf("failed to create migrate instance: %w", err)
	}
	
	return m, nil
}
