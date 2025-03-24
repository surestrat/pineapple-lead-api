package handlers

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/surestrat/pineapple-lead-api/config"
	"github.com/surestrat/pineapple-lead-api/models"
	"github.com/surestrat/pineapple-lead-api/repositories"
	"github.com/surestrat/pineapple-lead-api/utils"
)

// QuickQuoteHandler godoc
// @Summary Get a quick quote for vehicles
// @Description Requests a quick insurance quote from Pineapple for one or more vehicles
// @Tags quotes
// @Accept json
// @Produce json
// @Param quickQuoteRequest body models.QuickQuoteRequest true "Vehicle information for quote"
// @Success 200 {object} models.QuickQuoteResponse "Quote retrieved successfully"
// @Failure 400 {object} models.ErrorResponse "Invalid input data"
// @Failure 429 {object} models.ErrorResponse "Too many requests"
// @Failure 500 {object} models.ErrorResponse "Internal server error"
// @Router /api/v1/quote/quick-quote [post]
func QuickQuoteHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("Processing quick quote request")
	
	// Create a context with timeout for the entire operation
	ctx, cancel := context.WithTimeout(r.Context(), time.Duration(config.GetConfig().RequestTimeout)*time.Second)
	defer cancel()
	
	var req models.QuickQuoteRequest
	if !utils.ValidateRequest(w, r, &req) {
		return
	}

	// Log request details
	log.Printf("Quick quote request received for source: %s, ref: %s with %d vehicles", 
		req.Source, req.ExternalReferenceID, len(req.Vehicles))

	// Get the endpoint from config
	endpoint := config.GetConfig().QuickQuoteEndpoint

	// Make API request to Pineapple's Quick Quote API asynchronously
	resultChan := utils.MakeAPIRequestAsync(ctx, endpoint, "POST", req)
	
	// Wait for the API response
	result := <-resultChan
	if result.Error != nil {
		log.Printf("Error calling Quick Quote API at %s: %v", endpoint, result.Error)
		http.Error(w, "Error calling Quick Quote API: "+result.Error.Error(), http.StatusInternalServerError)
		return
	}

	// Parse the response
	var resp models.QuickQuoteResponse
	if err := json.Unmarshal(result.Body, &resp); err != nil {
		log.Printf("Error decoding Quick Quote API response: %v", err)
		http.Error(w, "Error decoding Quick Quote API response: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// Validate response
	if !resp.Success || resp.ID == "" {
		errMsg := "Invalid response from Quick Quote API: missing success or ID"
		log.Printf("%s: %+v", errMsg, resp)
		http.Error(w, errMsg, http.StatusInternalServerError)
		return
	}

	// Save the quote to database in a separate goroutine
	go func() {
		// Create a new context for the background operation
		bgCtx, bgCancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer bgCancel()
		
		repo, err := repositories.NewQuoteRepository()
		if err != nil {
			log.Printf("Warning: Failed to create quote repository: %v", err)
			log.Println("The quote data will not be persisted in the database.")
			return
		}
		
		if err := repo.SaveQuote(bgCtx, req, resp); err != nil {
			log.Printf("Warning: Failed to save quote to database: %v", err)
		} else {
			log.Printf("Successfully saved quote to database with ID: %s", resp.ID)
		}
	}()

	// Log success with premium and excess details if available
	if len(resp.Data) > 0 {
		log.Printf("Quick quote successful, ID: %s, Premium: %.2f, Excess: %.2f", 
			resp.ID, resp.Data[0].Premium, resp.Data[0].Excess)
	} else {
		log.Printf("Quick quote successful, ID: %s (no pricing data returned)", resp.ID)
	}

	// Return the response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}