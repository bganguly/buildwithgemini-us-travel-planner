"""Travel planner tools for trip budget calculation, scenic route lookup, and destination image generation.

GCP Project ID: 'qwiklabs-gcp-04-44a01d976633'
Bucket Name: 'us-travel-planner-media-qwiklabs-04'
"""

import io
import re
from typing import Any, Optional
from google.cloud import storage
from PIL import Image, ImageDraw, ImageFont

PROJECT_ID = "qwiklabs-gcp-04-44a01d976633"
BUCKET_NAME = "us-travel-planner-media-qwiklabs-04"

# ---------------------------------------------------------------------------
# Tool 1: calculate_trip_budget
# ---------------------------------------------------------------------------
def calculate_trip_budget(
    days: int,
    daily_rental_rate: float,
    total_miles: float,
    lodging_tier: str = "moderate",
    park_passes_count: int = 1,
) -> dict[str, Any]:
    """Calculate itemized costs for a US road trip and motorcycle vacation.

    Args:
        days: Total number of trip days (e.g. 7).
        daily_rental_rate: Daily rate in USD for motorcycle/bike rental (e.g. 165.0).
        total_miles: Estimated total miles to ride/drive (e.g. 850.0).
        lodging_tier: Comfort level tier for nightly stay ('budget', 'moderate', or 'luxury').
        park_passes_count: Number of National Park vehicle entry passes needed (default 1 pass for $35).

    Returns:
        Itemized budget breakdown with total estimated cost in USD.
    """
    tier_rates = {
        "budget": 85.0,
        "moderate": 155.0,
        "luxury": 275.0,
    }
    lodging_nightly_rate = tier_rates.get(lodging_tier.lower(), 155.0)

    # Motorcycle average: 45 MPG, average US premium gas $3.85/gal
    mpg = 45.0
    gas_price_per_gal = 3.85
    estimated_gallons = total_miles / mpg
    estimated_fuel_cost = round(estimated_gallons * gas_price_per_gal, 2)

    motorcycle_rental_total = round(days * daily_rental_rate, 2)
    lodging_total = round(days * lodging_nightly_rate, 2)
    meals_total = round(days * 55.0, 2)  # $55/day estimate for food
    park_fees_total = round(park_passes_count * 35.0, 2)  # $35 per park/America the Beautiful pass

    total_cost = round(
        motorcycle_rental_total + estimated_fuel_cost + lodging_total + meals_total + park_fees_total,
        2,
    )

    return {
        "trip_duration_days": days,
        "lodging_tier": lodging_tier,
        "total_miles": total_miles,
        "itemized_breakdown_usd": {
            "motorcycle_rental": motorcycle_rental_total,
            "estimated_fuel": estimated_fuel_cost,
            "lodging": lodging_total,
            "meals_and_dining": meals_total,
            "park_entrance_passes": park_fees_total,
        },
        "total_estimated_cost_usd": total_cost,
        "average_cost_per_day_usd": round(total_cost / days, 2) if days > 0 else total_cost,
    }


# ---------------------------------------------------------------------------
# Tool 2: get_scenic_route_highlights
# ---------------------------------------------------------------------------
SCENIC_ROUTES_DATABASE = {
    "utah Scenic byway 12": {
        "route_name": "Utah Scenic Byway 12 (A Highway Through Time)",
        "distance_miles": 122,
        "recommended_riding_days": 2,
        "start_end": "Torrey, UT to Panguitch, UT",
        "difficulty": "Moderate (Sinuous curves, steep drop-offs at The Hogback)",
        "highlights": [
            "Grand Staircase-Escalante National Monument",
            "The Hogback (cliffside ridge highway ride)",
            "Boulder Mountain & Escalante Canyons",
            "Kiva Koffeehouse overlook stop",
            "Calf Creek Falls trailhead",
        ],
        "best_season": "Spring through Autumn (May to October)",
        "description": "One of All-American Road's top rated motorcycle highways, traversing red rock canyons, slickrock ridges, and pine forests.",
    },
    "zion mount carmel highway": {
        "route_name": "Zion Mount Carmel Highway & Canyon Drive",
        "distance_miles": 25,
        "recommended_riding_days": 1,
        "start_end": "Springdale, UT to Mt. Carmel Junction, UT",
        "difficulty": "Easy to Moderate (Switchbacks and historic 1.1-mile tunnel)",
        "highlights": [
            "Zion Canyon Tunnel (1.1 miles through rock)",
            "Checkerboard Mesa sandstone formations",
            "Pine Creek Canyon switchbacks",
            "Weeping Rock & Angels Landing viewpoints",
        ],
        "best_season": "Year-round (Best April to November)",
        "description": "A breathtaking engineering marvel hugging reddish sandstone monoliths and towering canyon walls inside Zion National Park.",
    },
    "grand canyon desert view drive": {
        "route_name": "Grand Canyon South Rim & Desert View Drive",
        "distance_miles": 23,
        "recommended_riding_days": 1,
        "start_end": "Grand Canyon Village, AZ to Desert View Watchtower, AZ",
        "difficulty": "Easy (Paved national park highway with frequent overlooks)",
        "highlights": [
            "Mather Point & Yavapai Geology Museum",
            "Moran Point & Lipan Point (Colorado River views)",
            "Desert View Watchtower (Mary Colter historic tower)",
            "Tusayan Ruin & Pueblo site",
        ],
        "best_season": "Spring to Late Autumn",
        "description": "Panoramic ridge route offering endless vistas across the Colorado River gorge and Grand Canyon South Rim.",
    },
    "route 66 arizona": {
        "route_name": "Historic Route 66 Arizona (Kingman to Flagstaff)",
        "distance_miles": 160,
        "recommended_riding_days": 1,
        "start_end": "Kingman, AZ to Flagstaff, AZ via Oatman & Seligman",
        "difficulty": "Moderate (Sitgreaves Pass mountain twisties near Oatman)",
        "highlights": [
            "Oatman historic mining town & wild burros",
            "Sitgreaves Pass winding canyon road",
            "Hackberry General Store vintage Route 66 stop",
            "Seligman birth city of Historic Route 66",
        ],
        "best_season": "Year-round (Spring & Autumn ideal)",
        "description": "The quintessential American mother road experience with classic neon signs, vintage diners, and mountain twisties.",
    },
}


def get_scenic_route_highlights(route_name: str) -> dict[str, Any]:
    """Look up curated route highlights, mileage, difficulty, and scenic stops for US scenic highways.

    Args:
        route_name: Name or keyword of the route (e.g. 'Utah Scenic Byway 12', 'Zion', 'Grand Canyon', 'Route 66').

    Returns:
        Detailed scenic route information and waypoints.
    """
    clean_key = route_name.lower().strip()
    for key, data in SCENIC_ROUTES_DATABASE.items():
        if key in clean_key or clean_key in key:
            return {"status": "found", "route": data}

    # Default fallback matching
    if "utah" in clean_key or "byway" in clean_key:
        return {"status": "found", "route": SCENIC_ROUTES_DATABASE["utah Scenic byway 12"]}
    if "zion" in clean_key:
        return {"status": "found", "route": SCENIC_ROUTES_DATABASE["zion mount carmel highway"]}
    if "canyon" in clean_key:
        return {"status": "found", "route": SCENIC_ROUTES_DATABASE["grand canyon desert view drive"]}
    if "66" in clean_key:
        return {"status": "found", "route": SCENIC_ROUTES_DATABASE["route 66 arizona"]}

    return {
        "status": "not_found",
        "query": route_name,
        "available_routes": [v["route_name"] for v in SCENIC_ROUTES_DATABASE.values()],
        "message": f"Route '{route_name}' not found. Please choose from available routes.",
    }


# ---------------------------------------------------------------------------
# Tool 3: generate_destination_image
# ---------------------------------------------------------------------------
def generate_destination_image(destination_name: str, caption: str = "") -> dict[str, Any]:
    """Generate a real scenic photograph for a destination using gemini-3.1-flash-lite-image and publish to public Cloud Storage.

    Args:
        destination_name: Name of the destination or landmark (e.g. 'Utah Scenic Byway 12', 'Zion National Park', 'Grand Canyon').
        caption: Optional subtitle or description context.

    Returns:
        Public image URL and Markdown snippet ready to embed in response cards.
    """
    from google import genai

    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = f"A professional high-resolution photograph of {destination_name}. {caption or 'Scenic motorcycle travel road trip destination with stunning natural landscapes and scenic vistas.'}"

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
    )

    image_bytes = None
    for candidate in response.candidates or []:
        for part in candidate.content.parts or []:
            if part.inline_data and part.inline_data.data:
                image_bytes = part.inline_data.data
                break
        if image_bytes:
            break

    if not image_bytes:
        return {"status": "error", "message": f"Failed to generate photo for {destination_name}"}

    slug = re.sub(r"[^a-zA-Z0-9_]", "_", destination_name.lower().strip())
    filename = f"postcards/{slug}_postcard.jpg"

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    markdown_embed = f"![{destination_name}]({public_url})"

    return {
        "status": "success",
        "destination_name": destination_name,
        "public_image_url": public_url,
        "markdown_embed": markdown_embed,
    }
