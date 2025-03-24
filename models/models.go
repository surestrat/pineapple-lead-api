// models/models.go
package models

import (
	"database/sql"
	"time"
)

// LeadTransferRequest represents the request payload for transferring a lead
type LeadTransferRequest struct {
	Source        string `json:"source" validate:"required"`
	FirstName     string `json:"first_name" validate:"required"`
	LastName      string `json:"last_name" validate:"required"`
	Email         string `json:"email" validate:"required,email"`
	IDNumber      string `json:"id_number" validate:"omitempty,len=13"`
	QuoteID       string `json:"quote_id" validate:"omitempty"`
	ContactNumber string `json:"contact_number" validate:"required"`
}

// LeadTransferResponse represents the response from the Lead Transfer API
type LeadTransferResponse struct {
	Success bool `json:"success"`
	Data    struct {
		UUID        string `json:"uuid"`
		RedirectURL string `json:"redirect_url"`
	} `json:"data"`
}

// QuickQuoteRequest represents the request payload for getting a quick quote
type QuickQuoteRequest struct {
	Source              string    `json:"source" validate:"required"`
	ExternalReferenceID string    `json:"externalReferenceId" validate:"required"`
	Vehicles            []Vehicle `json:"vehicles" validate:"required,dive"`
}

// Vehicle represents a vehicle in the QuickQuoteRequest
type Vehicle struct {
	Year                     int      `json:"year" validate:"required,min=1900,max=2100"`
	Make                     string   `json:"make" validate:"required"`
	Model                    string   `json:"model" validate:"required"`
	MMCode                   string   `json:"mmCode" validate:"required"`
	Modified                 string   `json:"modified" validate:"required,oneof=Y N"`
	Category                 string   `json:"category" validate:"required,oneof=SUV HB SD CP SAV DC SC MPV CB SW XO HT RV CC PV BS DS"`
	Colour                   string   `json:"colour" validate:"required"`
	EngineSize               float64  `json:"engineSize" validate:"required,gt=0"`
	Financed                 string   `json:"financed" validate:"required,oneof=Y N"`
	Owner                    string   `json:"owner" validate:"required,oneof=Y N"`
	Status                   string   `json:"status" validate:"required,oneof=New SecondHand"`
	PartyIsRegularDriver     string   `json:"partyIsRegularDriver" validate:"required,oneof=Y N"`
	Accessories              string   `json:"accessories" validate:"required,oneof=Y N"`
	AccessoriesAmount        float64  `json:"accessoriesAmount" validate:"required,min=0"`
	RetailValue              float64  `json:"retailValue" validate:"required,gt=0"`
	MarketValue              float64  `json:"marketValue" validate:"required,gt=0"`
	InsuredValueType         string   `json:"insuredValueType" validate:"required,oneof=Retail Market"`
	UseType                  string   `json:"useType" validate:"required,oneof=Private Commercial BusinessUse"`
	OvernightParkingSituation string   `json:"overnightParkingSituation" validate:"required,oneof=Garage Carport InTheOpen Unconfirmed"`
	CoverCode                string   `json:"coverCode" validate:"required,oneof=Comprehensive"`
	Address                  Address  `json:"address" validate:"required"`
	RegularDriver           Driver   `json:"regularDriver" validate:"required"`
}

// Address represents a location in the Vehicle struct
type Address struct {
	AddressLine string  `json:"addressLine" validate:"required"`
	PostalCode  int     `json:"postalCode" validate:"required,min=0"`
	Suburb      string  `json:"suburb" validate:"required"`
	Latitude    float64 `json:"latitude" validate:"required"`
	Longitude   float64 `json:"longitude" validate:"required"`
}

// Driver represents the regular driver of a vehicle
type Driver struct {
	MaritalStatus        string `json:"maritalStatus" validate:"required,oneof=Single Married Divorced Widowed LivingTogether Annulment"`
	CurrentlyInsured     bool   `json:"currentlyInsured"`
	YearsWithoutClaims   int    `json:"yearsWithoutClaims" validate:"min=0"`
	RelationToPolicyHolder string `json:"relationToPolicyHolder" validate:"required,oneof=Self Spouse Child Other"`
	EmailAddress         string `json:"emailAddress" validate:"required,email"`
	MobileNumber         string `json:"mobileNumber" validate:"required"`
	IDNumber             string `json:"idNumber" validate:"required,len=13"`
	PrvInsLosses         int    `json:"prvInsLosses" validate:"min=0"`
	LicenseIssueDate     string `json:"licenseIssueDate" validate:"required,datetime=2006-01-02"`
	DateOfBirth          string `json:"dateOfBirth" validate:"required,datetime=2006-01-02"`
}

// QuickQuoteResponse represents the response from the Quick Quote API
type QuickQuoteResponse struct {
	Success bool   `json:"success"`
	ID      string `json:"id"`
	Data    []struct {
		Premium float64 `json:"premium"`
		Excess  float64 `json:"excess"`
	} `json:"data"`
}

// ErrorResponse represents a standardized error response
type ErrorResponse struct {
	Success bool   `json:"success"`
	Error   string `json:"error"`
}

// Database record models
type LeadTransferRecord struct {
	ID           int64
	Source       string
	FirstName    string
	LastName     string
	Email        string
	IDNumber     sql.NullString
	QuoteID      sql.NullString
	ContactNumber string
	ResponseUUID string
	RedirectURL  string
	CreatedAt    time.Time
}

type QuickQuoteRecord struct {
	ID                  int64
	Source              string
	ExternalReferenceID string
	VehicleCount        int
	ResponseID          string
	Premium             sql.NullFloat64
	Excess              sql.NullFloat64
	CreatedAt           time.Time
}