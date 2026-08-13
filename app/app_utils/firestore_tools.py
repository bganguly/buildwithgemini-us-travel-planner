"""Firestore tools for querying and managing motorcycle rentals in Firestore.

Hardcoded GCP Project ID: 'qwiklabs-gcp-04-44a01d976633'
"""

from typing import Any, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-44a01d976633"
COLLECTION_NAME = "motorcycle_rentals"


def _get_firestore_client() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)


def list_motorcycle_rentals(city: Optional[str] = None, rental_type: Optional[str] = None) -> list[dict[str, Any]]:
    """List available motorcycle and bike rentals from the Firestore database.

    Args:
        city: Optional filter by city name (e.g. 'Salt Lake City', 'Las Vegas', 'Flagstaff').
        rental_type: Optional filter by motorcycle category (e.g. 'Cruiser', 'Adventure Touring', 'Touring').

    Returns:
        List of matching motorcycle rental documents with fields like name, type, city, daily_rate_usd, available, description, and features.
    """
    db = _get_firestore_client()
    query = db.collection(COLLECTION_NAME)

    if city:
        query = query.where("city", "==", city)
    if rental_type:
        query = query.where("type", "==", rental_type)

    docs = query.stream()
    rentals = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        rentals.append(data)
    return rentals


def get_motorcycle_rental(rental_id: str) -> dict[str, Any]:
    """Get detailed information for a specific motorcycle rental by ID.

    Args:
        rental_id: The document ID of the motorcycle rental (e.g. 'rental-001').

    Returns:
        Dictionary containing rental details, or error message if not found.
    """
    db = _get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(rental_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Rental ID '{rental_id}' not found."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def add_or_update_motorcycle_rental(
    rental_id: str,
    name: str,
    rental_type: str,
    city: str,
    daily_rate_usd: float,
    available: bool = True,
    description: str = "",
    features: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Add or update a motorcycle rental record in Firestore.

    Args:
        rental_id: Document ID (e.g. 'rental-005').
        name: Name/model of motorcycle (e.g. 'Harley-Davidson Road Glide').
        rental_type: Category (e.g. 'Cruiser', 'Adventure Touring', 'Touring').
        city: Rental location city (e.g. 'Salt Lake City, UT').
        daily_rate_usd: Daily rental rate in USD (e.g. 170.0).
        available: Availability status (default True).
        description: Overview of bike features and ideal riding routes.
        features: Optional list of features (e.g. ['Saddlebags', 'Windshield', 'GPS']).

    Returns:
        Status message and saved record details.
    """
    db = _get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(rental_id)

    record = {
        "name": name,
        "type": rental_type,
        "city": city,
        "daily_rate_usd": daily_rate_usd,
        "available": available,
        "description": description,
        "features": features or [],
    }

    doc_ref.set(record)
    record["id"] = rental_id
    return {"status": "success", "message": f"Saved rental '{rental_id}' to Firestore", "data": record}
