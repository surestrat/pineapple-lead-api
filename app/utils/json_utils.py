"""
Utility functions for JSON handling and serialization.
"""

import json
from datetime import date, datetime
from typing import Any, Dict, List, Union
from enum import Enum


def serialize_dates(obj: Any) -> str:
    """
    Convert date, datetime, and enum objects to strings during JSON serialization.

    Args:
        obj: Object to potentially serialize

    Returns:
        String representation of the object if it's a date, datetime, or enum;
        otherwise raises TypeError
    """
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def to_json(data: Union[Dict, List]) -> str:
    """
    Convert a dictionary or list to a JSON string with proper date and enum handling.

    Args:
        data: Dictionary or list to convert to JSON

    Returns:
        JSON string representation of the data
    """
    # Create a deep copy of the data to avoid modifying the original
    if isinstance(data, dict):
        processed_data = {}
        # Convert any datetime or date objects to strings before serialization
        for key, value in data.items():
            if isinstance(value, (date, datetime)):
                processed_data[key] = value.isoformat()
            elif isinstance(value, Enum):
                processed_data[key] = value.value
            elif isinstance(value, dict):
                # Handle nested dictionaries
                processed_data[key] = to_json(value)
            elif isinstance(value, list):
                # Handle lists of objects
                processed_data[key] = [
                    (
                        item.isoformat()
                        if isinstance(item, (date, datetime))
                        else item.value if isinstance(item, Enum) else item
                    )
                    for item in value
                ]
            else:
                processed_data[key] = value
        return json.dumps(processed_data)
    else:
        # For list or other types, use the serialize_dates function
        return json.dumps(data, default=serialize_dates)


def from_json(json_str: str) -> Union[Dict, List]:
    """
    Parse a JSON string into Python objects.

    Args:
        json_str: JSON string to parse

    Returns:
        Dictionary or list parsed from the JSON string
    """
    return json.loads(json_str)
