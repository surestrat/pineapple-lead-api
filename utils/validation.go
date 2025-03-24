// utils/validation.go
package utils

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/go-playground/validator"
	"github.com/surestrat/pineapple-lead-api/models"
)

var validate *validator.Validate

func init() {
	validate = validator.New()
}

// ValidateRequest decodes and validates a request body
func ValidateRequest(w http.ResponseWriter, r *http.Request, req interface{}) bool {
	// Check if content type is JSON
	if r.Header.Get("Content-Type") != "application/json" {
		respondWithError(w, http.StatusUnsupportedMediaType, "Content-Type must be application/json")
		return false
	}

	// Decode the request body
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(req); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request body: "+err.Error())
		return false
	}

	// Validate the request
	if err := validate.Struct(req); err != nil {
		log.Printf("Validation error: %v", err)
		respondWithError(w, http.StatusBadRequest, "Validation error: "+err.Error())
		return false
	}

	return true
}

// respondWithError sends a JSON error response
func respondWithError(w http.ResponseWriter, code int, message string) {
	errorResponse := models.ErrorResponse{
		Success: false,
		Error:   message,
	}
	
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(errorResponse)
}