package utils

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/surestrat/pineapple-lead-api/config"
)

var (
	httpClient *http.Client
	// Rate limiting for API calls
	apiSemaphore chan struct{}
	clientOnce   sync.Once
)

// APIResult represents the result of an API call
type APIResult struct {
	Body  []byte
	Error error
}

// Initialize the HTTP client and semaphore
func init() {
	clientOnce.Do(func() {
		// Create client with default timeout
		httpClient = &http.Client{
			Timeout: time.Duration(config.GetConfig().RequestTimeout) * time.Second,
		}
		
		// Initialize semaphore to limit concurrent API calls
		apiSemaphore = make(chan struct{}, config.GetConfig().MaxConcurrentCalls)
	})
}

// MakeAPIRequest sends a request to the specified endpoint with the given method and body
func MakeAPIRequest(endpoint string, method string, body interface{}) ([]byte, error) {
	// Convert body to JSON
	jsonBody, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("error marshaling request body: %w", err)
	}

	// Check if this is a Swagger documentation request
	bearerToken := config.GetConfig().APIBearerToken
	userAgent := os.Getenv("HTTP_USER_AGENT")
	referer := os.Getenv("HTTP_REFERER")
	
	// Only use mock responses if:
	// 1. We're using the special Swagger documentation token OR
	// 2. The request is coming from the Swagger UI
	isSwaggerRequest := bearerToken == "swagger_documentation_token" || 
		strings.Contains(referer, "/swagger/") ||
		strings.Contains(userAgent, "Swagger")
	
	if isSwaggerRequest {
		// For Swagger documentation only, return a mock response
		return createMockResponse(endpoint, method, string(jsonBody))
	}

	// Create the request
	req, err := http.NewRequest(method, endpoint, bytes.NewBuffer(jsonBody))
	if err != nil {
		return nil, fmt.Errorf("error creating request: %w", err)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+bearerToken)

	// Acquire semaphore to limit concurrent requests
	apiSemaphore <- struct{}{}
	defer func() { <-apiSemaphore }()

	// Send the request
	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error sending request: %w", err)
	}
	defer resp.Body.Close()

	// Read the response body
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}

	// Check for non-2XX status codes
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("API returned non-2XX status code: %d, body: %s", resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

// createMockResponse generates a mock response for Swagger documentation testing only
func createMockResponse(endpoint string, method string, jsonBody string) ([]byte, error) {
	log.Println("SWAGGER DOCUMENTATION MODE: Using mock response for API documentation")
	
	// Lead transfer endpoint mock
	if strings.Contains(endpoint, "/users/motor_lead") {
		// Parse the request body to extract fields for the mock response
		var req map[string]interface{}
		if err := json.Unmarshal([]byte(jsonBody), &req); err != nil {
			return nil, err
		}
		
		// Generate a mock UUID and redirect URL
		uuid := fmt.Sprintf("swagger-doc-uuid-%d", time.Now().Unix())
		firstName := fmt.Sprintf("%v", req["first_name"])
		redirectURL := fmt.Sprintf("https://test-pineapple-claims.herokuapp.com/car-insurance/get-started?uuid=%s&ref=swagger-doc&name=%s", 
			uuid, firstName)
		
		mockResp := map[string]interface{}{
			"success": true,
			"data": map[string]interface{}{
				"uuid": uuid,
				"redirect_url": redirectURL,
			},
		}
		
		return json.Marshal(mockResp)
	}
	
	// Quick quote endpoint mock
	if strings.Contains(endpoint, "/api/v1/quote/quick-quote") {
		// Generate a mock quote ID and values
		quoteID := fmt.Sprintf("swagger-doc-quote-%d", time.Now().Unix())
		premium := 1240.46 // Mock premium
		excess := 6200.00  // Mock excess
		
		mockResp := map[string]interface{}{
			"success": true,
			"id": quoteID,
			"data": []map[string]interface{}{
				{
					"premium": premium,
					"excess": excess,
				},
			},
		}
		
		return json.Marshal(mockResp)
	}
	
	// Default fallback for unknown endpoints
	return json.Marshal(map[string]interface{}{
		"success": true,
		"message": "Swagger documentation mock response",
	})
}

// MakeAPIRequestAsync sends a request asynchronously and returns a channel with the result
func MakeAPIRequestAsync(ctx context.Context, endpoint string, method string, body interface{}) <-chan APIResult {
	resultChan := make(chan APIResult, 1)

	go func() {
		defer close(resultChan)

		// Handle context cancellation
		select {
		case <-ctx.Done():
			resultChan <- APIResult{nil, ctx.Err()}
			return
		default:
		}

		respBody, err := MakeAPIRequest(endpoint, method, body)
		resultChan <- APIResult{respBody, err}
	}()

	return resultChan
}

// ProcessAPIRequests processes multiple API requests concurrently
func ProcessAPIRequests(ctx context.Context, requests []func() ([]byte, error)) []APIResult {
	var wg sync.WaitGroup
	results := make([]APIResult, len(requests))

	for i, req := range requests {
		wg.Add(1)
		
		go func(index int, apiRequest func() ([]byte, error)) {
			defer wg.Done()

			// Handle context cancellation
			select {
			case <-ctx.Done():
				results[index] = APIResult{nil, ctx.Err()}
				return
			default:
			}

			respBody, err := apiRequest()
			results[index] = APIResult{respBody, err}
		}(i, req)
	}

	wg.Wait()
	return results
}