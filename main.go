package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/surestrat/pineapple-lead-api/config"
	"github.com/surestrat/pineapple-lead-api/db"
	"github.com/surestrat/pineapple-lead-api/handlers"
	"github.com/surestrat/pineapple-lead-api/middlewares"

	"github.com/go-chi/chi/middleware"
	"github.com/go-chi/chi/v5"
	"github.com/joho/godotenv"
)

func main() {
    // Get working directory
    workDir, err := os.Getwd()
    if (err != nil) {
        log.Printf("Warning: Could not get working directory: %v", err)
    } else {
        log.Printf("Current working directory: %s", workDir)
    }

    // Check if .env file exists
    envPath := filepath.Join(workDir, ".env")
    if _, err := os.Stat(envPath); os.IsNotExist(err) {
        log.Printf("Warning: .env file not found at %s", envPath)
    } else {
        log.Printf(".env file found at %s", envPath)
    }

    // Try to load .env file with proper error handling
    err = godotenv.Load()
    if err != nil {
        log.Printf("Warning: Error loading .env file: %v", err)
        log.Println("Will try again with explicit path")
        
        // Try with explicit path
        err = godotenv.Load(envPath)
        if err != nil {
            log.Printf("Warning: Still failed to load .env file from %s: %v", envPath, err)
        } else {
            log.Println("Successfully loaded .env file from explicit path")
        }
    } else {
        log.Println("Successfully loaded .env file")
    }

    // Print all environment variables for debugging (except sensitive ones)
    log.Println("Environment variables loaded:")
    for _, env := range os.Environ() {
        if len(env) > 15 && (env[:15] == "API_BEARER_TOKE" || env[:12] == "DB_PASSWORD=") {
            // Don't print sensitive values, just show that they're set
            log.Printf("  %s=[SET]", env[:strings.Index(env, "=")])
        } else {
            log.Printf("  %s", env)
        }
    }

    // Check API_BEARER_TOKEN specifically
    tokenValue := os.Getenv("API_BEARER_TOKEN")
    if tokenValue == "" {
        log.Println("ERROR: API_BEARER_TOKEN environment variable is not set.")
        log.Println("Please set a valid bearer token in your .env file or environment variables.")
        log.Println("Example: API_BEARER_TOKEN=your_token_from_pineapple")
        
        // Try a direct approach as a fallback
        log.Println("Setting a temporary token for development... MOCK RESPONSES WILL BE USED")
        os.Setenv("API_BEARER_TOKEN", "temporary_development_token")
        if os.Getenv("API_BEARER_TOKEN") != "" {
            log.Println("Set temporary token for development MOCK mode")
        } else {
            log.Println("Failed to set temporary token")
            os.Exit(1)
        }
    } else if tokenValue == "your_bearer_token_here" {
        log.Println("WARNING: You are using the placeholder API_BEARER_TOKEN value.")
        log.Println("*** DEVELOPMENT MODE ACTIVATED: Real APIs will NOT be called ***")
        log.Println("*** The system will generate MOCK responses instead ***")
        log.Println("Replace the token with your actual API token to make real API calls.")
    } else {
        log.Println("API_BEARER_TOKEN is set properly - will make real API calls")
    }

    // Validate other aspects of configuration
    if err := config.ValidateConfig(); err != nil {
        log.Printf("Configuration warning: %v", err)
        log.Println("Continuing with default values for development...")
    }

    // Initialize database with better error handling
    if err := db.InitDB(); err != nil {
        log.Printf("Database error: %v", err)
        log.Println("Continuing without database for development purposes.")
        log.Println("The API will function but data won't be persisted.")
    } else {
        defer db.Close()
        
        // Run database migrations
        if err := db.MigrateUp(); err != nil {
            log.Printf("Migration warning: %v", err)
            log.Println("Continuing without migrations. Some features may not work correctly.")
        }
    }

    // Configure Go's runtime for optimal concurrency
    numCPU := runtime.NumCPU()
    runtime.GOMAXPROCS(numCPU)
    
    r := chi.NewRouter()

    // Middleware
    r.Use(middleware.RequestID)
    r.Use(middleware.RealIP)
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(time.Duration(config.GetConfig().RequestTimeout) * time.Second))
    r.Use(middlewares.RateLimitMiddleware)

    // API Routes
    r.Post("/users/motor_lead", handlers.LeadTransferHandler)
    r.Post("/api/v1/quote/quick-quote", handlers.QuickQuoteHandler)

    // Health check
    r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
        // Return information about the API
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusOK)
        fmt.Fprintf(w, `{"status":"healthy","version":"1.0.0","cpus":%d}`, numCPU)
    })

    // API Documentation routes
    swaggerDir := filepath.Join(workDir, "swagger")
    
    // Static files for Swagger UI
    r.Route("/swagger", func(r chi.Router) {
        r.Get("/*", middlewares.ServeSwaggerUI(swaggerDir))
    })
    
    // Serve Swagger JSON spec file
    r.Get("/docs/swagger.json", func(w http.ResponseWriter, r *http.Request) {
        http.ServeFile(w, r, filepath.Join(workDir, "docs", "swagger.json"))
    })
    
    // Redirect /docs to /swagger/
    r.Get("/docs", middlewares.RedirectToDocs)
    
    // Redirect root to Swagger docs
    r.Get("/", func(w http.ResponseWriter, r *http.Request) {
        http.Redirect(w, r, "/swagger/", http.StatusFound)
    })

    // Start the server
    cfg := config.GetConfig()
    port := strconv.Itoa(cfg.Port)
    
    log.Printf("Server listening on port %s with %d CPUs", port, numCPU)
    log.Printf("Documentation available at http://localhost:%s/swagger/", port)
    if err := http.ListenAndServe(":"+port, r); err != nil {
        log.Fatalf("Error starting server: %v", err)
    }
}