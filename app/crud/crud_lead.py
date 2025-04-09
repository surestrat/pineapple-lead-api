import logging
from supabase import Client
from app.schemas import lead as lead_schema  # Use alias
from typing import Optional, Dict, Any
import uuid

# from postgrest.exceptions import APIError # Import specific Supabase errors if needed

logger = logging.getLogger(__name__)

# Assume 'leads' table exists matching LeadRecord schema


def create_lead_record(
    db: Client, *, lead_in: lead_schema.LeadRecordCreate
) -> Optional[Dict[str, Any]]:
    """Creates a lead record in Supabase 'leads' table."""
    if not lead_in.id:  # Generate UUID if not provided during creation
        lead_in.id = str(uuid.uuid4())

    # Use model_dump for Pydantic V2
    lead_data = lead_in.model_dump()
    log_ref_id = lead_data.get("id", "N/A")
    log_ref_user = lead_data.get("user_id", "N/A")
    logger.info(
        f"Attempting to create lead record with id: {log_ref_id} for user {log_ref_user}"
    )

    try:
        # Check supabase-py docs for exact syntax V2+ (insert might take dict)
        response = db.table("leads").insert(lead_data).execute()

        if response.data:
            logger.info(
                f"Successfully created lead record: {response.data[0].get('id')}"
            )
            return response.data[0]
        else:
            logger.warning(
                f"Supabase insert for lead {log_ref_id} returned no data. Response: {response}"
            )
            # RLS might prevent returning data, try fetching if critical
            return get_lead_record_by_local_id(db, str(log_ref_id))
    except Exception as e:  # Catch potential PostgrestAPIError etc.
        logger.exception(f"Database error creating lead record id {log_ref_id}: {e}")
        return None  # Indicate failure


def update_lead_record(
    db: Client,
    *,
    local_lead_id: str,
    lead_update_data: lead_schema.LeadRecordUpdate,  # Use specific update schema
) -> Optional[Dict[str, Any]]:
    """Updates a lead record in Supabase using non-null fields from update data."""
    # Use exclude_unset=True to only send fields that were explicitly set
    update_payload = lead_update_data.model_dump(exclude_unset=True)

    if not update_payload:
        logger.warning(
            f"Update called for lead {local_lead_id} with no data to update."
        )
        return get_lead_record_by_local_id(db, local_lead_id)  # Return current state

    logger.info(
        f"Attempting to update lead record: {local_lead_id} with fields: {list(update_payload.keys())}"
    )
    try:
        response = (
            db.table("leads").update(update_payload).eq("id", local_lead_id).execute()
        )
        if response.data:
            logger.info(f"Successfully updated lead record: {local_lead_id}")
            return response.data[0]
        else:
            logger.warning(
                f"Update for lead ID {local_lead_id} returned no data (maybe ID not found or RLS prevent return)."
            )
            # Fetch the record to check current state if update seemed to fail silently
            # return get_lead_record_by_local_id(db, local_lead_id)
            return (
                None  # Indicate potentially no row was updated or couldn't be returned
            )
    except Exception as e:
        logger.exception(f"Database error updating lead record {local_lead_id}: {e}")
        return None  # Indicate failure


def get_lead_record_by_local_id(
    db: Client, local_lead_id: str
) -> Optional[Dict[str, Any]]:
    """Gets a lead record from Supabase by its internal ID."""
    logger.debug(f"Fetching lead record by local id: {local_lead_id}")
    try:
        # maybe_single returns dict directly if found, None otherwise
        response = (
            db.table("leads")
            .select("*")
            .eq("id", local_lead_id)
            .maybe_single()
            .execute()
        )
        if response and response.data:
            logger.debug(f"Found lead record: {local_lead_id}")
            return response.data
        else:
            logger.debug(f"Lead record not found: {local_lead_id}")
            return None
    except Exception as e:
        logger.exception(f"Database error fetching lead record {local_lead_id}: {e}")
        return None  # Indicate failure
