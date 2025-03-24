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

// QuoteRepository handles database operations for quick quotes
type QuoteRepository struct {
	pool *pgxpool.Pool
}

// NewQuoteRepository creates a new QuoteRepository
func NewQuoteRepository() (*QuoteRepository, error) {
	pool, err := db.GetPool()
	if err != nil {
		return nil, err
	}
	
	return &QuoteRepository{
		pool: pool,
	}, nil
}

// SaveQuote stores a quick quote request and response in the database
func (r *QuoteRepository) SaveQuote(ctx context.Context, quote models.QuickQuoteRequest, resp models.QuickQuoteResponse) error {
	// Check if database pool is nil (development mode without DB)
	if r.pool == nil {
		log.Printf("Development mode: Quote would be saved with ID %s for reference %s", 
			resp.ID, quote.ExternalReferenceID)
		return nil
	}

	var premium, excess sql.NullFloat64
	
	if len(resp.Data) > 0 {
		premium = sql.NullFloat64{Float64: resp.Data[0].Premium, Valid: true}
		excess = sql.NullFloat64{Float64: resp.Data[0].Excess, Valid: true}
	} else {
		premium = sql.NullFloat64{Valid: false}
		excess = sql.NullFloat64{Valid: false}
	}
	
	query := `
		INSERT INTO quick_quotes 
		(source, external_reference_id, vehicle_count, response_id, response_premium, response_excess)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING id
	`
	
	var id int64
	
	// Using QueryRow instead of Exec to get the ID
	err := r.pool.QueryRow(ctx, query,
		quote.Source,
		quote.ExternalReferenceID,
		len(quote.Vehicles),
		resp.ID,
		premium,
		excess,
	).Scan(&id)
	
	if err != nil {
		return fmt.Errorf("failed to save quick quote: %w", err)
	}
	
	log.Printf("Saved quick quote with ID %d for reference %s with response ID %s", id, quote.ExternalReferenceID, resp.ID)
	return nil
}

// GetQuoteByID retrieves a quick quote by its response ID
func (r *QuoteRepository) GetQuoteByID(ctx context.Context, id string) (*models.QuickQuoteRecord, error) {
	query := `
		SELECT id, source, external_reference_id, vehicle_count, response_id, 
		       response_premium, response_excess, created_at
		FROM quick_quotes
		WHERE response_id = $1
	`
	
	var quote models.QuickQuoteRecord
	
	err := r.pool.QueryRow(ctx, query, id).Scan(
		&quote.ID,
		&quote.Source,
		&quote.ExternalReferenceID,
		&quote.VehicleCount,
		&quote.ResponseID,
		&quote.Premium,
		&quote.Excess,
		&quote.CreatedAt,
	)
	
	if err != nil {
		return nil, fmt.Errorf("failed to get quick quote by ID: %w", err)
	}
	
	return &quote, nil
}
