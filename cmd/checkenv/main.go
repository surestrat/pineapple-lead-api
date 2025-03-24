package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/joho/godotenv"
)

func main() {
	// Get and print current working directory
	wd, err := os.Getwd()
	fmt.Printf("Current working directory: %s\n", wd)

	// Look for .env file
	envPath := filepath.Join(wd, ".env")
	info, err := os.Stat(envPath)
	if os.IsNotExist(err) {
		fmt.Printf(".env file not found at %s\n", envPath)
		
		// Try parent directory
		parentEnvPath := filepath.Join(filepath.Dir(wd), ".env")
		_, err = os.Stat(parentEnvPath)
		if os.IsNotExist(err) {
			fmt.Printf(".env file also not found at %s\n", parentEnvPath)
		} else {
			fmt.Printf(".env file found at %s\n", parentEnvPath)
			envPath = parentEnvPath
		}
	} else {
		fmt.Printf(".env file found at %s (size: %d bytes, mode: %s)\n", 
			envPath, info.Size(), info.Mode())
	}

	// Try to read .env file content directly
	content, err := os.ReadFile(envPath)
	if err != nil {
		fmt.Printf("Error reading .env file: %v\n", err)
	} else {
		fmt.Println("\n.env file content (first line and number of lines):")
		lines := strings.Split(string(content), "\n")
		if len(lines) > 0 {
			fmt.Printf("  First line: %s\n", lines[0])
			fmt.Printf("  Total lines: %d\n", len(lines))
		}
	}

	// Try to load using godotenv
	fmt.Println("\nAttempting to load .env file with godotenv...")
	err = godotenv.Load()
	if err != nil {
		fmt.Printf("Error loading .env file: %v\n", err)
		
		// Try with explicit path
		fmt.Printf("Trying with explicit path: %s\n", envPath)
		err = godotenv.Load(envPath)
		if err != nil {
			fmt.Printf("Still failed to load .env file: %v\n", err)
		} else {
			fmt.Println("Successfully loaded .env file with explicit path")
		}
	} else {
		fmt.Println("Successfully loaded .env file")
	}

	// Check if API_BEARER_TOKEN is set
	fmt.Println("\nChecking environment variables:")
	token := os.Getenv("API_BEARER_TOKEN")
	if token == "" {
		fmt.Println("API_BEARER_TOKEN is not set")
	} else {
		fmt.Printf("API_BEARER_TOKEN is set to: %s\n", token)
	}

	// List a few other important variables
	checkEnv := func(name string) {
		value := os.Getenv(name)
		if value == "" {
			fmt.Printf("%s is not set\n", name)
		} else {
			fmt.Printf("%s is set to: %s\n", name, value)
		}
	}

	checkEnv("DB_HOST")
	checkEnv("DB_PORT")
	checkEnv("LEAD_TRANSFER_ENDPOINT")
}
