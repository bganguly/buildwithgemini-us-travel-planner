"""Image generation tools for US Travel Planner agent using gemini-3.1-flash-lite-image in global region.

GCP Project ID: 'qwiklabs-gcp-04-44a01d976633'
GCS Bucket: 'us-travel-planner-media-qwiklabs-04'
"""

import re
import time
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools.tool_context import ToolContext

PROJECT_ID = "qwiklabs-gcp-04-44a01d976633"
BUCKET_NAME = "us-travel-planner-media-qwiklabs-04"
MODEL_NAME = "gemini-3.1-flash-lite-image"
LOCATION = "global"


async def generate_domain_item_image(tool_context: ToolContext, prompt: str) -> str:
    """Generate a photo or image for a travel item, motorcycle rental model, destination, or landmark using gemini-3.1-flash-lite-image.

    Saves the image as a session artifact in the Playground and uploads it to public Cloud Storage.

    Args:
        tool_context: ADK ToolContext injected automatically by the framework.
        prompt: Detailed description of the travel item, motorcycle, landmark, or scenic view to generate.

    Returns:
        The public HTTPS URL of the uploaded image (https://storage.googleapis.com/us-travel-planner-media-qwiklabs-04/<object>).
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"Generate a vivid photo of: {prompt}",
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
        return f"Error: Failed to generate image for prompt: '{prompt}'."

    timestamp = int(time.time())
    slug = re.sub(r"[^a-zA-Z0-9_]", "_", prompt[:25].lower().strip())
    filename = f"generated_items/{slug}_{timestamp}.jpg"

    # 1. Save as artifact in Playground
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload image bytes directly to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url
