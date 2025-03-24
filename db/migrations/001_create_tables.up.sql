CREATE TABLE IF NOT EXISTS lead_transfers (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    id_number TEXT,
    quote_id TEXT,
    contact_number TEXT NOT NULL,
    response_uuid TEXT NOT NULL,
    redirect_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quick_quotes (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    external_reference_id TEXT NOT NULL,
    vehicle_count INTEGER NOT NULL,
    response_id TEXT NOT NULL,
    response_premium NUMERIC,
    response_excess NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS lead_transfers_email_idx ON lead_transfers(email);
CREATE INDEX IF NOT EXISTS lead_transfers_response_uuid_idx ON lead_transfers(response_uuid);
CREATE INDEX IF NOT EXISTS quick_quotes_response_id_idx ON quick_quotes(response_id);
CREATE INDEX IF NOT EXISTS quick_quotes_external_reference_id_idx ON quick_quotes(external_reference_id);
