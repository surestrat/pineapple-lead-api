package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
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
    }

    // Load .env file if in development environment
    if os.Getenv("ENVIRONMENT") != "production" {
        // Check if .env file exists
        envPath := filepath.Join(workDir, ".env")
        if _, err := os.Stat(envPath); !os.IsNotExist(err) {
            err = godotenv.Load(envPath)
            if err != nil {
                log.Printf("Warning: Error loading .env file: %v", err)
            } else {
                log.Println("Loaded configuration from .env file")
            }
        }
    } else {
        log.Println("Running in production mode - using environment variables")
    }

    // Check API_BEARER_TOKEN
    tokenValue := os.Getenv("API_BEARER_TOKEN")
    if tokenValue == "" {
        log.Println("ERROR: API_BEARER_TOKEN environment variable is not set.")
        log.Println("A valid bearer token is required for production operation.")
        os.Exit(1)
    } else if tokenValue == "swagger_documentation_token" {
        log.Println("WARNING: Using documentation token. Mock responses will be used ONLY for Swagger documentation.")
        log.Println("This should not be used in production environments.")
    }

    // Validate configuration
    if err := config.ValidateConfig(); err != nil {
        log.Printf("Configuration error: %v", err)
        log.Println("Fix configuration issues before continuing.")
        os.Exit(1)
    }

    // Initialize database
    if err := db.InitDB(); err != nil {
        log.Printf("Database error: %v", err)
        log.Println("The application requires a valid database connection.")
        os.Exit(1)
    }
    defer db.Close()
    
    // Run database migrations
    if err := db.MigrateUp(); err != nil {
        log.Printf("Migration error: %v", err)
        log.Println("Database schema must be properly initialized.")
        os.Exit(1)
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