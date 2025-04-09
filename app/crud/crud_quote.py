import logging
from supabase import Client
from app.schemas import quote as quote_schema  # Use alias
from typing import Optional, Dict, Any, List
import uuid

# from postgrest.exceptions import APIError # Import specific Supabase errors if needed

logger = logging.getLogger(__name__)

# Assume 'quotes' table exists matching QuoteRecord schema


def create_quote_record(
    db: Client, *, quote_in: quote_schema.QuoteRecordCreate
) -> Optional[Dict[str, Any]]:
    """Creates a quote record in Supabase 'quotes' table."""
    if not quote_in.id:  # Generate UUID if not provided during creation
        quote_in.id = str(uuid.uuid4())

    # Use model_dump for Pydantic V2
    quote_data = quote_in.model_dump()
    log_ref_id = quote_data.get("id", "N/A")
    log_ref_user = quote_data.get("user_id", "N/A")
    logger.info(
        f"Attempting to create quote record with id: {log_ref_id} for user {log_ref_user}"
    )

    try:
        # Check supabase-py docs for exact syntax V2+ (insert might take dict)
        response = db.table("quotes").insert(quote_data).execute()

        if response.data:
            logger.info(
                f"Successfully created quote record: {response.data[0].get('id')}"
            )
            return response.data[0]
        else:
            logger.warning(
                f"Supabase insert for quote {log_ref_id} returned no data. Response: {response}"
            )
            # RLS might prevent returning data, try fetching if critical
            return get_quote_record_by_local_id(db, str(log_ref_id))
    except Exception as e:  # Catch potential PostgrestAPIError etc.
        logger.exception(f"Database error creating quote record id {log_ref_id}: {e}")
        return None  # Indicate failure


def update_quote_record(
    db: Client,
    *,
    local_quote_id: str,
    quote_update_data: quote_schema.QuoteRecordUpdate,  # Use specific update schema
) -> Optional[Dict[str, Any]]:
    """Updates a quote record in Supabase using non-null fields from update data."""
    # Use exclude_unset=True to only send fields that were explicitly set
    update_payload = quote_update_data.model_dump(exclude_unset=True)

    if not update_payload:
        logger.warning(
            f"Update called for quote {local_quote_id} with no data to update."
        )
        return get_quote_record_by_local_id(db, local_quote_id)  # Return current state

    logger.info(
        f"Attempting to update quote record: {local_quote_id} with fields: {list(update_payload.keys())}"
    )
    try:
        response = (
            db.table("quotes").update(update_payload).eq("id", local_quote_id).execute()
        )
        if response.data:
            logger.info(f"Successfully updated quote record: {local_quote_id}")
            return response.data[0]
        else:
            logger.warning(
                f"Update for quote ID {local_quote_id} returned no data (maybe ID not found or RLS prevent return)."
            )
            # Fetch the record to check current state if update seemed to fail silently
            # return get_quote_record_by_local_id(db, local_quote_id)
            return (
                None  # Indicate potentially no row was updated or couldn't be returned
            )
    except Exception as e:
        logger.exception(f"Database error updating quote record {local_quote_id}: {e}")
        return None  # Indicate failure


def get_quote_record_by_local_id(
    db: Client, local_quote_id: str
) -> Optional[Dict[str, Any]]:
    """Gets a quote record from Supabase by its internal ID."""
    logger.debug(f"Fetching quote record by local id: {local_quote_id}")
    try:
        # maybe_single returns dict directly if found, None otherwise
        response = (
            db.table("quotes")
            .select("*")
            .eq("id", local_quote_id)
            .maybe_single()
            .execute()
        )
        if response and response.data:
            logger.debug(f"Found quote record: {local_quote_id}")
            return response.data
        else:
            logger.debug(f"Quote record not found: {local_quote_id}")
            return None
    except Exception as e:
        logger.exception(f"Database error fetching quote record {local_quote_id}: {e}")
        return None  # Indicate failure


def get_quote_record_by_pineapple_id(
    db: Client, pineapple_quote_id: str
) -> Optional[Dict[str, Any]]:
    """Gets a quote record from Supabase by the Pineapple Quote ID."""
    logger.debug(f"Fetching quote record by pineapple_quote_id: {pineapple_quote_id}")
    try:
        response = (
            db.table("quotes")
            .select("*")
            .eq("pineapple_quote_id", pineapple_quote_id)
            .maybe_single()
            .execute()
        )
        if response and response.data:
            logger.debug(
                f"Found quote record with pineapple_quote_id: {pineapple_quote_id}"
            )
            return response.data
        else:
            logger.debug(
                f"Quote record not found for pineapple_quote_id: {pineapple_quote_id}"
            )
            return None
    except Exception as e:
        logger.exception(
            f"Database error fetching quote record by pineapple_id {pineapple_quote_id}: {e}"
        )
        return None
