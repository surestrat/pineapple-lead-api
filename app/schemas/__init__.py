from .lead import (
    LeadRead,
    LeadCreate,
    LeadUpdate,
    LeadTransferRequest,
    LeadTransferResponse,
)
from .quote import QuoteRead, QuoteCreate, QuoteUpdate, QuoteResponse

# For backwards compatibility
from .lead import LeadSchema
from .quote import QuoteSchema
