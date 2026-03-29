"""
BiRefNet Background Removal - RunPod Serverless Handler

Accepts image URL or base64, returns PNG with transparent background.

Input:
  - url: Public URL of image to process
  - image: Base64-encoded image (alternative to url)
  - model: Model name (default: birefnet-general)
  - alpha_matting: Enable alpha matting for better edges (default: true)

Output:
  - image: Base64-encoded PNG with transparent background
  - width: Output image width
  - height: Output image height
"""

import runpod
import base64
import requests
import io
import os
import time
import traceback
from PIL import Image
from rembg import remove, new_session

# Pre-load session on startup for faster inference
print("birefnet-worker - Loading BiRefNet session...")
BIREFNET_SESSION = new_session("birefnet-general")
U2NET_SESSION = new_session("u2net")  # Fallback
print("birefnet-worker - Sessions loaded successfully")

# Supported models
SESSIONS = {
    "birefnet-general": BIREFNET_SESSION,
    "u2net": U2NET_SESSION,
}


def download_image(url: str, timeout: int = 60) -> bytes:
    """Download image from URL with timeout."""
    print(f"birefnet-worker - Downloading image from {url[:80]}...")
    response = requests.get(url, timeout=timeout, stream=True)
    response.raise_for_status()
    return response.content


def process_image(
    image_data: bytes,
    model: str = "birefnet-general",
    alpha_matting: bool = True,
) -> tuple[bytes, int, int]:
    """Remove background from image."""
    session = SESSIONS.get(model, BIREFNET_SESSION)
    
    print(f"birefnet-worker - Processing with model={model} alpha_matting={alpha_matting}")
    t0 = time.time()
    
    # Remove background
    result = remove(
        image_data,
        session=session,
        alpha_matting=alpha_matting,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10,
    )
    
    # Get dimensions from result
    img = Image.open(io.BytesIO(result))
    width, height = img.size
    
    elapsed = time.time() - t0
    print(f"birefnet-worker - Processed in {elapsed:.2f}s, output: {width}x{height}")
    
    return result, width, height


def handler(job: dict) -> dict:
    """RunPod serverless handler."""
    try:
        job_input = job.get("input", {})
        
        # Get image from URL or base64
        image_url = job_input.get("url")
        image_b64 = job_input.get("image")
        
        if not image_url and not image_b64:
            return {"error": "Missing 'url' or 'image' parameter"}
        
        # Download or decode image
        if image_url:
            try:
                image_data = download_image(image_url)
            except requests.RequestException as e:
                return {"error": f"Failed to download image: {e}"}
        else:
            try:
                # Handle data URI or raw base64
                if "," in image_b64:
                    image_b64 = image_b64.split(",", 1)[1]
                image_data = base64.b64decode(image_b64)
            except Exception as e:
                return {"error": f"Invalid base64 image: {e}"}
        
        # Get options
        model = job_input.get("model", "birefnet-general")
        alpha_matting = job_input.get("alpha_matting", True)
        
        if model not in SESSIONS:
            return {"error": f"Unknown model: {model}. Available: {list(SESSIONS.keys())}"}
        
        # Process image
        result_bytes, width, height = process_image(
            image_data,
            model=model,
            alpha_matting=alpha_matting,
        )
        
        # Encode result
        result_b64 = base64.b64encode(result_bytes).decode("utf-8")
        
        return {
            "image": result_b64,
            "width": width,
            "height": height,
            "model": model,
        }
        
    except Exception as e:
        print(f"birefnet-worker - Error: {traceback.format_exc()}")
        return {"error": str(e)}


if __name__ == "__main__":
    print("birefnet-worker - Starting serverless handler...")
    runpod.serverless.start({"handler": handler})
