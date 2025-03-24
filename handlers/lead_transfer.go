// handlers/lead_transfer.go
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

// LeadTransferHandler godoc
// @Summary Transfer a lead to Pineapple
// @Description Transfers customer lead information to the Pineapple system
// @Tags leads
// @Accept json
// @Produce json
// @Param leadTransferRequest body models.LeadTransferRequest true "Lead information to transfer"
// @Success 200 {object} models.LeadTransferResponse "Lead transferred successfully"
// @Failure 400 {object} models.ErrorResponse "Invalid input data"
// @Failure 429 {object} models.ErrorResponse "Too many requests"
// @Failure 500 {object} models.ErrorResponse "Internal server error"
// @Router /users/motor_lead [post]
func LeadTransferHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("Processing lead transfer request")
	
	// Create a context with timeout for the entire operation
	ctx, cancel := context.WithTimeout(r.Context(), time.Duration(config.GetConfig().RequestTimeout)*time.Second)
	defer cancel()
	
	var req models.LeadTransferRequest
	if !utils.ValidateRequest(w, r, &req) {
		return
	}

	// Log request details without sensitive information
	log.Printf("Lead transfer request received for: %s %s from source: %s", req.FirstName, req.LastName, req.Source)

	// Get the endpoint from config
	endpoint := config.GetConfig().LeadTransferEndpoint

	// Make API request to Pineapple's Lead Transfer API asynchronously
	resultChan := utils.MakeAPIRequestAsync(ctx, endpoint, "POST", req)
	
	// Wait for the API response
	result := <-resultChan
	if result.Error != nil {
		log.Printf("Error calling Lead Transfer API at %s: %v", endpoint, result.Error)
		http.Error(w, "Error calling Lead Transfer API: "+result.Error.Error(), http.StatusInternalServerError)
		return
	}

	// Parse the response
	var resp models.LeadTransferResponse
	if err := json.Unmarshal(result.Body, &resp); err != nil {
		log.Printf("Error decoding Lead Transfer API response: %v", err)
		http.Error(w, "Error decoding Lead Transfer API response: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// Validate response
	if !resp.Success || resp.Data.UUID == "" {
		errMsg := "Invalid response from Lead Transfer API: missing success or UUID"
		log.Printf("%s: %+v", errMsg, resp)
		http.Error(w, errMsg, http.StatusInternalServerError)
		return
	}

	// Save the lead to database in a separate goroutine
	go func() {
		// Create a new context for the background operation
		bgCtx, bgCancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer bgCancel()
		
		repo, err := repositories.NewLeadRepository()
		if err != nil {
			log.Printf("Warning: Failed to create lead repository: %v", err)
			log.Println("The lead data will not be persisted in the database.")
			return
		}
		
		if err := repo.SaveLead(bgCtx, req, resp); err != nil {
			log.Printf("Warning: Failed to save lead to database: %v", err)
		} else {
			log.Printf("Successfully saved lead to database with UUID: %s", resp.Data.UUID)
		}
	}()

	// Log success
	log.Printf("Lead transfer successful, UUID: %s, Redirect URL: %s", 
		resp.Data.UUID, resp.Data.RedirectURL)

	// Return the response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}