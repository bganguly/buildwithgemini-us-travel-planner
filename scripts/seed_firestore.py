"""Seed script for Firestore motorcycle rentals collection.

Hardcoded Project ID: 'qwiklabs-gcp-04-44a01d976633'
"""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-44a01d976633"
COLLECTION_NAME = "motorcycle_rentals"

SEED_ITEMS = [
    {
        "id": "rental-001",
        "name": "Harley-Davidson Heritage Classic 114",
        "type": "Cruiser",
        "city": "Salt Lake City, UT",
        "daily_rate_usd": 165.0,
        "available": True,
        "description": "Iconic American cruiser with saddlebags and windshield. Perfect for cruising Utah's Scenic Byway 12.",
        "features": ["Saddlebags", "Windshield", "ABS", "Cruise Control"],
    },
    {
        "id": "rental-002",
        "name": "BMW R1250GS Adventure",
        "type": "Adventure Touring",
        "city": "Las Vegas, NV",
        "daily_rate_usd": 185.0,
        "available": True,
        "description": "Ultimate adventure touring bike designed for highway cruising and light trail riding around Zion & Grand Canyon.",
        "features": ["Aluminum Cases", "Heated Grips", "GPS Navigation", "Riding Modes"],
    },
    {
        "id": "rental-003",
        "name": "Indian Chieftain Dark Horse",
        "type": "Touring",
        "city": "Flagstaff, AZ",
        "daily_rate_usd": 175.0,
        "available": True,
        "description": "Premium heavy touring motorcycle equipped with touchscreen navigation and power windshield for Route 66 and Grand Canyon South Rim.",
        "features": ["Power Windshield", "Touchscreen Audio/GPS", "Hard Saddlebags"],
    },
    {
        "id": "rental-004",
        "name": "Honda Africa Twin Adventure Sports",
        "type": "Adventure Touring",
        "city": "Salt Lake City, UT",
        "daily_rate_usd": 150.0,
        "available": True,
        "description": "Versatile and nimble adventure motorcycle ideal for exploring Bryce Canyon and Moab desert backroads.",
        "features": ["DCT Automatic", "Saddlebags", "Engine Guard"],
    },
]


def seed():
    print(f"Connecting to Firestore project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    for item in SEED_ITEMS:
        doc_data = dict(item)
        item_id = doc_data.pop("id")
        doc_ref = collection_ref.document(item_id)
        doc_ref.set(doc_data)
        print(f"Seeded document: {item_id} -> {doc_data['name']} ({doc_data['city']})")

    print(f"Successfully seeded {len(SEED_ITEMS)} items into collection '{COLLECTION_NAME}'!")


if __name__ == "__main__":
    seed()
