package repositories

import (
	"context"
	"database/sql"
	"fmt"
	"log"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/surestrat/pineapple-lead-api/db"
	"github.com/surestrat/pineapple-lead-api/models"
)

// LeadRepository handles database operations for lead transfers
type LeadRepository struct {
	pool *pgxpool.Pool
}

// NewLeadRepository creates a new LeadRepository
func NewLeadRepository() (*LeadRepository, error) {
	pool, err := db.GetPool()
	if err != nil {
		return nil, err
	}
	
	return &LeadRepository{
		pool: pool,
	}, nil
}

// SaveLead stores a lead transfer request and response in the database
func (r *LeadRepository) SaveLead(ctx context.Context, lead models.LeadTransferRequest, resp models.LeadTransferResponse) error {
	// Check if database pool is nil (development mode without DB)
	if r.pool == nil {
		log.Printf("Development mode: Lead would be saved with UUID %s for %s %s", 
			resp.Data.UUID, lead.FirstName, lead.LastName)
		return nil
	}

	query := `
		INSERT INTO lead_transfers 
		(source, first_name, last_name, email, id_number, quote_id, contact_number, response_uuid, redirect_url)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
		RETURNING id
	`
	
	var id int64
	
	// Using QueryRow instead of Exec to get the ID
	err := r.pool.QueryRow(ctx, query,
		lead.Source,
		lead.FirstName,
		lead.LastName,
		lead.Email,
		sql.NullString{String: lead.IDNumber, Valid: lead.IDNumber != ""},
		sql.NullString{String: lead.QuoteID, Valid: lead.QuoteID != ""},
		lead.ContactNumber,
		resp.Data.UUID,
		resp.Data.RedirectURL,
	).Scan(&id)
	
	if err != nil {
		return fmt.Errorf("failed to save lead transfer: %w", err)
	}
	
	log.Printf("Saved lead transfer with ID %d for %s %s with UUID %s", id, lead.FirstName, lead.LastName, resp.Data.UUID)
	return nil
}

// GetLeadByUUID retrieves a lead transfer by its UUID
func (r *LeadRepository) GetLeadByUUID(ctx context.Context, uuid string) (*models.LeadTransferRecord, error) {
	query := `
		SELECT id, source, first_name, last_name, email, id_number, quote_id, contact_number, 
		       response_uuid, redirect_url, created_at
		FROM lead_transfers
		WHERE response_uuid = $1
	`
	
	var lead models.LeadTransferRecord
	
	err := r.pool.QueryRow(ctx, query, uuid).Scan(
		&lead.ID,
		&lead.Source,
		&lead.FirstName,
		&lead.LastName,
		&lead.Email,
		&lead.IDNumber,
		&lead.QuoteID,
		&lead.ContactNumber,
		&lead.ResponseUUID,
		&lead.RedirectURL,
		&lead.CreatedAt,
	)
	
	if err != nil {
		return nil, fmt.Errorf("failed to get lead transfer by UUID: %w", err)
	}
	
	return &lead, nil
}
