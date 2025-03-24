package config

import (
	"fmt"
	"os"
	"strconv"
	"sync"
)

// Configuration holds all application configuration
type Configuration struct {
	APIBearerToken       string
	DBHost               string
	DBPort               int
	DBUser               string
	DBPassword           string
	DBName               string
	DBSSLMode            string
	Port                 int
	RequestTimeout       int // in seconds
	MaxConcurrentCalls   int
	LeadTransferEndpoint string
	QuickQuoteEndpoint   string
}

var (
	config     *Configuration
	configOnce sync.Once
)

// GetConfig returns the application configuration
func GetConfig() *Configuration {
	configOnce.Do(func() {
		config = &Configuration{
			APIBearerToken:       getEnv("API_BEARER_TOKEN", ""),
			DBHost:               getEnv("DB_HOST", "localhost"),
			DBPort:               getEnvAsInt("DB_PORT", 5432),
			DBUser:               getEnv("DB_USER", "postgres"),
			DBPassword:           getEnv("DB_PASSWORD", ""),
			DBName:               getEnv("DB_NAME", "pineapple_leads"),
			DBSSLMode:            getEnv("DB_SSLMODE", "disable"),
			Port:                 getEnvAsInt("PORT", 9000),
			RequestTimeout:       getEnvAsInt("REQUEST_TIMEOUT", 30),
			MaxConcurrentCalls:   getEnvAsInt("MAX_CONCURRENT_CALLS", 10),
			LeadTransferEndpoint: getEnv("LEAD_TRANSFER_ENDPOINT", "http://gw-test.pineapple.co.za/users/motor_lead"),
			QuickQuoteEndpoint:   getEnv("QUICK_QUOTE_ENDPOINT", "http://gw-test.pineapple.co.za/api/v1/quote/quick-quote"),
		}
	})

	return config
}

// ValidateConfig validates that all required configuration is present
func ValidateConfig() error {
	c := GetConfig()
	
	// API_BEARER_TOKEN is checked separately in main.go for better error messages
	
	if c.DBPassword == "" {
		return fmt.Errorf("DB_PASSWORD environment variable is required")
	}

	if c.LeadTransferEndpoint == "" {
		return fmt.Errorf("LEAD_TRANSFER_ENDPOINT environment variable is required")
	}

	if c.QuickQuoteEndpoint == "" {
		return fmt.Errorf("QUICK_QUOTE_ENDPOINT environment variable is required")
	}
	
	return nil
}

// Helper function to get environment variable with a default value
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

// Helper function to get environment variable as an integer with a default value
func getEnvAsInt(key string, defaultValue int) int {
	valueStr := getEnv(key, "")
	if valueStr == "" {
		return defaultValue
	}
	
	value, err := strconv.Atoi(valueStr)
	if err != nil {
		return defaultValue
	}
	
	return value
}

// GetDSN returns the PostgreSQL connection string
func GetDSN() string {
	cfg := GetConfig()
	return fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
		cfg.DBHost, cfg.DBPort, cfg.DBUser, cfg.DBPassword, cfg.DBName, cfg.DBSSLMode)
}
